"""Capas con un fondo bajo cada tecla, para poner encima del fondo (imagen o vídeo).

Polymath no deja dar color a teclas sueltas, así que se pinta en el propio fondo: una
placa oscura bajo cada tecla para que la leyenda se lea, y otra de color con brillo
bajo las teclas que se quieren resaltar.

    plates, glow = render(keys(), highlight={"Q", "W"}, tints={"Tab": MAP})
    frame = Image.alpha_composite(Image.alpha_composite(bg, plates), glow)

La placa es algo más pequeña que la tecla (INSET) y va algo más arriba (VIEW_DY):
las teclas tienen altura y, sentado delante del teclado, a través de cada una se ve
un trozo de pantalla más alejado. VIEW_DY se ajusta a ojo desde la silla.
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1920, 1080
INSET = 4
VIEW_DY = -16
TINT_DY = -18  # las placas de color (tints) se veían más bajas que las rojas: suben algo más
RADIUS = 12

DARK = (10, 5, 4, 165)
DARK_EDGE = (70, 14, 6, 255)
OPEN_KEYS = {"Space": 70}     # teclas con la placa casi transparente: alfa propio

HOT_TOP, HOT_BOTTOM = (110, 6, 3), (200, 28, 8)
HOT_ALPHA = 150
HOT_EDGE = (255, 90, 30, 255)
GLOW = (255, 45, 10)


def _plate_box(rect, dy=0):
    x0, y0, x1, y1 = (round(v) for v in rect)
    dy += VIEW_DY
    return [x0 + INSET, y0 + INSET + dy, x1 - INSET - 1, y1 - INSET - 1 + dy]


def _gradient(size, top, bottom):
    w, h = size
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        g.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    return g.resize((w, h))


def _fill(plates, box, top, bottom, alpha):
    x0, y0, x1, y1 = box
    size = (x1 - x0 + 1, y1 - y0 + 1)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], RADIUS, fill=alpha)
    fill = _gradient(size, top, bottom).convert("RGBA")
    fill.putalpha(mask)
    plates.alpha_composite(fill, (x0, y0))


def render(keys, highlight=(), tints=None, glow_radius=14):
    """Devuelve (placas, brillo), dos RGBA de W x H.

    highlight: teclas en rojo con halo. tints: {tecla: {top, bottom, alpha, edge, glow}},
    placas de otro color (degradado top→bottom, borde edge, halo glow o None).
    El brillo va aparte para poder animarlo (latido) sin rehacer las placas.
    """
    tints = tints or {}
    plates = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(plates)
    glow_mask = Image.new("L", (W, H), 0)
    gm = ImageDraw.Draw(glow_mask)

    for name, rect in keys.items():
        box = _plate_box(rect)
        if name in highlight or name in tints:
            continue
        alpha = OPEN_KEYS.get(name, DARK[3])
        d.rounded_rectangle(box, RADIUS, fill=DARK[:3] + (alpha,), outline=DARK_EDGE[:3] + (min(255, alpha + 30),), width=1)

    for name in highlight:
        box = _plate_box(keys[name])
        x0, y0, x1, y1 = box
        _fill(plates, box, HOT_TOP, HOT_BOTTOM, HOT_ALPHA)
        d.rounded_rectangle(box, RADIUS, outline=HOT_EDGE, width=3)
        gm.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], RADIUS + 2, outline=255, width=6)

    # Halo: el contorno difuminado, fuera y dentro de la placa.
    halo = glow_mask.filter(ImageFilter.GaussianBlur(glow_radius))
    halo = ImageChops.multiply(halo, Image.new("L", (W, H), 200))
    glow = Image.new("RGBA", (W, H), GLOW + (0,))
    glow.putalpha(halo)

    for name, t in tints.items():
        box = _plate_box(keys[name], TINT_DY)
        x0, y0, x1, y1 = box
        _fill(plates, box, t["top"], t["bottom"], t["alpha"])
        d.rounded_rectangle(box, RADIUS, outline=t["edge"], width=2)
        if t.get("glow"):
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], RADIUS + 2, outline=255, width=5)
            m = ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(glow_radius * 0.8)), Image.new("L", (W, H), 160))
            g = Image.new("RGBA", (W, H), t["glow"] + (0,))
            g.putalpha(m)
            glow = Image.alpha_composite(glow, g)
    return plates, glow
