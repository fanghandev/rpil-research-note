"""Make size-reduced copies of report figures for embedding in PDFs and HTML.

Full-resolution figures stay where they are (they are the originals); this writes JPEG
copies, resized so that the width is at most --max-width pixels, into an output folder
that mirrors the input tree. Reports then embed the copies, so a PDF or a self-contained
HTML page carries print-quality images instead of 5000-pixel PNGs.

Defaults (1800 px, quality 88, no chroma subsampling) are about 270 dpi at full page
width on US letter, with no visible artifacts on plots and reconstructions.

Usage:
    python tools/reencode_images.py SRC_DIR OUT_DIR [--max-width 1800] [--quality 88]

Needs Pillow (the opengate environment has it).
"""

import argparse
from pathlib import Path

from PIL import Image

EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"}


def reencode(src: Path, dst: Path, max_width: int, quality: int) -> int:
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.getchannel("A"))
        im = bg
    else:
        im = im.convert("RGB")
    if im.width > max_width:
        im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=quality, subsampling=0, optimize=True)
    return dst.stat().st_size


def reencode_tree(src_dir: Path, out_dir: Path, max_width: int = 1800, quality: int = 88):
    """Re-encode every image under src_dir into out_dir (same relative path, .jpg)."""
    before = after = n = 0
    for src in sorted(p for p in src_dir.rglob("*") if p.suffix.lower() in EXTS):
        dst = out_dir / src.relative_to(src_dir).with_suffix(".jpg")
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            after += dst.stat().st_size
        else:
            after += reencode(src, dst, max_width, quality)
        before += src.stat().st_size
        n += 1
    return n, before, after


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--max-width", type=int, default=1800)
    ap.add_argument("--quality", type=int, default=88)
    a = ap.parse_args()
    n, before, after = reencode_tree(a.src, a.out, a.max_width, a.quality)
    print(f"{n} images: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB in {a.out}")


if __name__ == "__main__":
    main()
