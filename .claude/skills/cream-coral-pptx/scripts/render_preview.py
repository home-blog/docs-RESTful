#!/usr/bin/env python3
"""덱 미리보기: .pptx → PDF → 슬라이드별 PNG → 4장씩 묶은 접촉 인화(contact sheet).

    python render_preview.py deck.pptx [--out 폴더] [--dpi 60]

LibreOffice(soffice)와 pdftoppm(poppler-utils)이 필요하다. 묶음 이미지는 Pillow가 있을 때만 만든다.
결과 이미지를 Read 도구로 열어 슬라이드를 한 장씩 눈으로 확인한다.
LibreOffice는 PowerPoint와 줄바꿈이 조금 다르므로, 여기서 빠듯한 상자는 PowerPoint에서도 빠듯하다고 보면 된다.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile


def to_pdf(pptx, out_dir):
    profile = tempfile.mkdtemp(prefix="lo-profile-")
    env = dict(os.environ, SAL_USE_VCLPLUGIN="svp")
    cmd = ["soffice", f"-env:UserInstallation=file://{profile}", "--headless",
           "--convert-to", "pdf", "--outdir", out_dir, pptx]
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, timeout=300)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        sys.exit(f"soffice 변환 실패: {getattr(e, 'stderr', b'').decode(errors='ignore')[:500]}")
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    if not os.path.exists(pdf):
        sys.exit("PDF가 만들어지지 않았습니다. (sandbox에서 막히면 pptx 스킬의 scripts/office/soffice.py 사용)")
    return pdf


def sheets(pngs, out_dir, per=4):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return []
    made = []
    for k in range(0, len(pngs), per):
        group = [Image.open(p) for p in pngs[k:k + per]]
        w, h = group[0].size
        pad = 16
        sheet = Image.new("RGB", (w * 2 + pad * 3, h * 2 + pad * 3 + 24 * 2), "#888888")
        d = ImageDraw.Draw(sheet)
        for i, im in enumerate(group):
            x = pad + (i % 2) * (w + pad)
            y = pad + (i // 2) * (h + pad + 24)
            d.text((x, y), f"{k + i + 1}", fill="#000000")
            sheet.paste(im, (x, y + 20))
        f = os.path.join(out_dir, f"sheet-{k // per + 1:02d}.png")
        sheet.save(f)
        made.append(f)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--out", default=None)
    ap.add_argument("--dpi", type=int, default=60)
    a = ap.parse_args()
    pptx = os.path.abspath(a.pptx)
    out = os.path.abspath(a.out or os.path.splitext(pptx)[0] + "-preview")
    os.makedirs(out, exist_ok=True)
    for old in glob.glob(os.path.join(out, "*.png")):
        os.remove(old)
    pdf = to_pdf(pptx, out)
    subprocess.run(["pdftoppm", "-png", "-r", str(a.dpi), pdf, os.path.join(out, "slide")], check=True)
    pngs = sorted(glob.glob(os.path.join(out, "slide-*.png")))
    made = sheets(pngs, out)
    print(f"PDF: {pdf}")
    print(f"슬라이드 PNG {len(pngs)}장: {out}/slide-*.png")
    if made:
        print("묶음:", *made, sep="\n  ")


if __name__ == "__main__":
    main()
