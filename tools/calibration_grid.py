"""Imagen-rejilla para calibrar dónde cae cada tecla sobre el fondo de Polymath.

Se pone como fondo de un tema (dimming 0, blur 0), se hace una foto del teclado desde
arriba y se leen las coordenadas en píxeles que asoman a través de cada tecla.

    python tools/calibration_grid.py [salida.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
CELL = 60       # celda con su coordenada escrita
MAJOR = 300     # línea gruesa de color

img = Image.new("RGB", (W, H), "black")
d = ImageDraw.Draw(img)
font = ImageFont.truetype("consola.ttf", 13)
big = ImageFont.truetype("arialbd.ttf", 22)

# Celdas en damero con un tono por bloque de 300 px: así se reconoce la zona
# aunque la leyenda de la tecla tape el número.
hues = [(70, 20, 20), (20, 60, 20), (20, 30, 75), (65, 55, 10), (55, 15, 60), (10, 55, 60), (60, 35, 15)]
for y in range(0, H, CELL):
    for x in range(0, W, CELL):
        base = hues[(x // MAJOR + 3 * (y // MAJOR)) % len(hues)]
        k = 1.0 if (x // CELL + y // CELL) % 2 else 0.55
        d.rectangle([x, y, x + CELL - 1, y + CELL - 1], fill=tuple(int(c * k) for c in base))
        d.text((x + 3, y + 2), f"{x}", font=font, fill=(235, 235, 235))
        d.text((x + 3, y + 16), f"{y}", font=font, fill=(170, 170, 170))

for x in range(0, W + 1, CELL):
    d.line([(x, 0), (x, H)], fill=(110, 110, 110), width=1)
for y in range(0, H + 1, CELL):
    d.line([(0, y), (W, y)], fill=(110, 110, 110), width=1)
for x in range(0, W + 1, MAJOR):
    d.line([(x, 0), (x, H)], fill=(255, 60, 60), width=3)
for y in range(0, H + 1, MAJOR):
    d.line([(0, y), (W, y)], fill=(255, 60, 60), width=3)

# Diagonales y centro: delatan recortes o deformaciones al escalar.
d.line([(0, 0), (W, H)], fill=(255, 255, 0), width=2)
d.line([(0, H), (W, 0)], fill=(255, 255, 0), width=2)
d.ellipse([W / 2 - 40, H / 2 - 40, W / 2 + 40, H / 2 + 40], outline=(255, 255, 0), width=3)

# Marco y esquinas: si alguna no se ve, Polymath está recortando por ese lado.
d.rectangle([0, 0, W - 1, H - 1], outline=(0, 255, 255), width=6)
for (cx, cy), name in {(0, 0): "TL", (W, 0): "TR", (0, H): "BL", (W, H): "BR"}.items():
    tx = 12 if cx == 0 else W - 50
    ty = 12 if cy == 0 else H - 40
    d.rectangle([tx - 4, ty - 2, tx + 38, ty + 28], fill="black")
    d.text((tx, ty), name, font=big, fill=(0, 255, 255))

out = sys.argv[1] if len(sys.argv) > 1 else "calibration_grid.png"
img.save(out)
print(out, img.size)
