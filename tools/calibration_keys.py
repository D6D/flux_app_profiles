"""Segunda calibración: pinta cada tecla donde layout_es_iso cree que está.

Si una tecla se ve de un solo color con la cruz blanca centrada, la posición es buena;
si asoma el color de la vecina o la franja negra, indica hacia dónde está desplazada.

    python tools/calibration_keys.py [salida.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

from layout_es_iso import ROW_TOP, keys

W, H = 1920, 1080
GAP = 3

img = Image.new("RGB", (W, H), "black")
d = ImageDraw.Draw(img)
font = ImageFont.truetype("consola.ttf", 14)
colors = [(200, 40, 40), (40, 160, 60), (50, 80, 210), (200, 170, 30), (170, 50, 190), (30, 170, 180)]

for i, (name, (x0, y0, x1, y1)) in enumerate(keys().items()):
    row = ROW_TOP.index(y0)
    d.rectangle([x0 + GAP, y0 + GAP, x1 - GAP - 1, y1 - GAP - 1], fill=colors[(i + 2 * row) % len(colors)])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.line([(cx - 14, cy), (cx + 14, cy)], fill="white", width=3)
    d.line([(cx, cy - 14), (cx, cy + 14)], fill="white", width=3)
    # Marcas a 30 px del borde: si se pierde alguna, la tecla está desplazada hacia ese lado.
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = (x0 + 30 if dx < 0 else x1 - 30), (y0 + 30 if dy < 0 else y1 - 30)
        d.rectangle([px - 4, py - 4, px + 4, py + 4], fill="white")
    d.text((x0 + GAP + 4, y1 - GAP - 18), name, font=font, fill="white")

# Franja de módulos: regla horizontal cada 120 px.
for x in range(0, W, 120):
    d.rectangle([x, 0, x + 119, ROW_TOP[0] - 1], fill=(25, 25, 25) if x // 120 % 2 else (55, 55, 55))
    d.text((x + 6, 6), str(x), font=font, fill="white")
for y in range(0, ROW_TOP[0], 60):
    d.line([(0, y), (W, y)], fill=(90, 90, 90))
    d.text((W - 40, y + 4), str(y), font=font, fill="white")
d.rectangle([0, 0, W - 1, H - 1], outline=(0, 255, 255), width=6)

out = sys.argv[1] if len(sys.argv) > 1 else "calibration_keys.png"
img.save(out)
print(out)
