#!/usr/bin/env python3
"""Turn the source pictures in src/sources/img into WebP files in src/static/assets/img.
Writes src/images.json (name -> widths, height ratio) for the page templates.

Product pictures are cut-outs of different shapes, so each one is centred on a 4:3 card
in its own background colour. That keeps every product tile and gallery the same shape.
Run:  python3 src/images.py   (needs Pillow). build.py --images runs it for you.
"""
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sources", "img")
DST = os.path.join(HERE, "static", "assets", "img")
os.makedirs(DST, exist_ok=True)

CARD = (1600, 1200)     # 4:3
PAD = 0.07              # empty margin around the product, as a share of the card
AS_IS = {"sss-diagram", "placeholder"}   # kept at their own shape (diagrams, ready-made cards)

registry = {}
total = 0
for fn in sorted(os.listdir(SRC)):
    name, ext = os.path.splitext(fn)
    if ext.lower() not in (".webp", ".png", ".jpg", ".jpeg"):
        continue
    im = Image.open(os.path.join(SRC, fn)).convert("RGBA")
    flat = Image.new("RGB", im.size, (255, 255, 255))
    flat.paste(im, mask=im.split()[3])
    if name in AS_IS:
        out = flat
    else:
        ground = flat.getpixel((2, 2))                       # the picture's own background colour
        box_w, box_h = CARD[0] * (1 - 2 * PAD), CARD[1] * (1 - 2 * PAD)
        k = min(box_w / flat.width, box_h / flat.height)
        w, h = round(flat.width * k), round(flat.height * k)
        out = Image.new("RGB", CARD, ground)
        out.paste(flat.resize((w, h), Image.LANCZOS), ((CARD[0] - w) // 2, (CARD[1] - h) // 2))
    widths = [w for w in (480, 800, 1600) if w <= out.width] or [out.width]
    for w in widths:
        h = round(out.height * w / out.width)
        r = out if w == out.width else out.resize((w, h), Image.LANCZOS)
        path = os.path.join(DST, f"{name}-{w}.webp")
        r.save(path, "WEBP", quality=80, method=6)
        total += os.path.getsize(path)
    registry[name] = {"widths": widths, "ratio": round(out.height / out.width, 4)}

json.dump(registry, open(os.path.join(HERE, "images.json"), "w"), indent=1)
print(f"{len(registry)} pictures, {total / 1e6:.1f} MB in {DST}")
