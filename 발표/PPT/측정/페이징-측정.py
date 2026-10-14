"""오프셋 페이징과 커서 페이징, count 쿼리 비용을 SQLite로 직접 잰다.

python3 발표/PPT/측정/페이징-측정.py [DB 파일 경로]
→ 발표/PPT/측정/결과.json (PPT 차트가 이 숫자를 쓴다)
환경마다 숫자는 다르다. 경향(뒤로 갈수록 오프셋만 느려진다)을 보여 주는 용도.
"""
import json, os, sqlite3, statistics, sys, tempfile, time

ROWS, SIZE, RUNS = 1_000_000, 20, 15
db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "paging-bench.db")
if os.path.exists(db):
    os.remove(db)
con = sqlite3.connect(db)
con.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, content TEXT, created_at TEXT)")
con.executemany("INSERT INTO posts VALUES (?, ?, ?, ?)",
                ((i, f"글 {i}", "본문 " * 20, f"2026-10-{1 + i % 28:02d}") for i in range(1, ROWS + 1)))
con.commit()


def ms(sql, *args):
    times = []
    for _ in range(RUNS):
        t = time.perf_counter(); con.execute(sql, args).fetchall(); times.append((time.perf_counter() - t) * 1000)
    return round(statistics.median(times), 2)


pages = [1, 10, 100, 1000, 10000, 25000, 50000]
offset, cursor = [], []
for p in pages:
    skip = (p - 1) * SIZE
    offset.append(ms("SELECT id, title FROM posts ORDER BY id DESC LIMIT ? OFFSET ?", SIZE, skip))
    last_id = ROWS - skip + 1                      # 앞 페이지의 마지막 id
    cursor.append(ms("SELECT id, title FROM posts WHERE id < ? ORDER BY id DESC LIMIT ?", last_id, SIZE))
page_query = ms("SELECT id, title FROM posts ORDER BY id DESC LIMIT 20")
count_query = ms("SELECT COUNT(*) FROM posts")
out = {"rows": ROWS, "size": SIZE, "runs": RUNS, "engine": f"SQLite {sqlite3.sqlite_version}",
       "pages": pages, "offset_ms": offset, "cursor_ms": cursor,
       "page_query_ms": page_query, "count_query_ms": count_query}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "결과.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
con.close(); os.remove(db)
