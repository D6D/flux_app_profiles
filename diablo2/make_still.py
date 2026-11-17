"""Fondo fijo de Diablo II: imagen + placas de teclas, y una vista previa con leyendas.

    python diablo2/make_still.py [--base]

Genera en diablo2/: still.png (lo que iría al teclado) y preview.png (simulando las
leyendas, solo para juzgar si se leen). Con --base, base_still.png y base_preview.png:
solo los atajos comunes de base.py, sin habilidades del personaje.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "tools"))
import keyplates  # noqa: E402
from layout_es_iso import keys  # noqa: E402

import base  # noqa: E402
import skills  # noqa: E402
import space_crack  # noqa: E402
LEGEND = (255, 222, 165)

LABELS = {"LShift": "Shift", "RShift": "Shift", "LCtrl": "Ctrl", "RCtrl": "Ctrl", "LAlt": "Alt",
          "RAlt": "Alt", "Enter2": "Enter","MT": "MT", "MT1": "MT:1", "Left": "←", "Right": "→",
          "Up": "↑", "Down": "↓", "Space": ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", action="store_true")
    args = ap.parse_args()
    if args.base:
        prefix, labels, tints = "base_", base.BASE_SKILLS, base.BASE_TINTS
        highlight = set(labels) - base.ICON_ONLY
    else:
        prefix, labels, tints = "", skills.SKILLS, skills.TINTS
        highlight = skills.HIGHLIGHT
    k = keys()
    bg = Image.open(HERE / "background_1920.png").convert("RGBA")
    plates, glow = keyplates.render(k, highlight=highlight, tints=tints)
    still = Image.alpha_composite(Image.alpha_composite(bg, plates), glow).convert("RGB")
    frame = space_crack.apply(np.asarray(still, dtype=np.float32) / 255, *space_crack.render(), 0.8)
    still = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    still.convert("RGB").save(HERE / f"{prefix}still.png")

    prev = still.copy()
    d = ImageDraw.Draw(prev)
    font = str(HERE / "fonts" / "Cinzel-Bold.ttf")   # la fuente del tema
    big = ImageFont.truetype(font, 32)
    small = ImageFont.truetype(font, 21)
    tiny = ImageFont.truetype(font, 13)
    for name, (x0, y0, x1, y1) in k.items():
        label = LABELS.get(name, name)
        cx = (x0 + x1) / 2
        if name in base.ICON_ONLY:
            continue   # en el teclado va el icono, que aquí no se simula
        if name in labels:
            d.text((x0 + 20, y0 + 16), label, font=big, fill=LEGEND)
            d.multiline_text((cx, y1 - 18), labels[name].replace(" ", "\n"), font=tiny, fill=LEGEND,
                             anchor="md", align="center", spacing=1)
        elif label:
            d.text((cx, (y0 + y1) / 2), label, font=big if len(label) <= 2 else small, fill=LEGEND, anchor="mm")
    prev.convert("RGB").save(HERE / f"{prefix}preview.png")
    print(f"{prefix}still.png, {prefix}preview.png")


if __name__ == "__main__":
    main()
