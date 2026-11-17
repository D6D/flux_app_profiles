"""Grieta de lava que cruza la barra espaciadora y se ilumina como si respirara.

Nace en la lava que hay a la derecha de la barra y se va estrechando hacia la izquierda.
Se pinta encima de las placas: la barra tiene placa casi transparente y la grieta debe
verse entera. Va ~10 px por encima de la tecla, como las placas (keyplates.VIEW_DY).

    core, halo = render()     # float32 H x W en [0, 1]
    frame = apply(frame, core, halo, beat)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
SS = 2                # supermuestreo: líneas finas sin escalones
SEED = 66
START, END = (1216, 978), (536, 1022)
BRANCHES = [(0.26, -1, 150), (0.46, 1, 110), (0.63, -1, 95), (0.80, 1, 70)]   # posición, lado, largo
COLD, WARM, HOT = (0.60, 0.05, 0.01), (0.85, 0.16, 0.02), (1.0, 0.62, 0.16)
TOP, BOTTOM = 958, 1040   # las ramas no salen de la tecla (ya con el ajuste de VIEW_DY)


def _jagged(rng, a, b, rough, depth=6):
    """Línea quebrada entre a y b: desplazamiento del punto medio, en perpendicular."""
    pts = [np.array(a, float), np.array(b, float)]
    for level in range(depth):
        out = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            d = q - p
            normal = np.array([-d[1], d[0]]) / max(np.hypot(*d), 1)
            out += [(p + q) / 2 + normal * rng.normal(0, rough * 0.6 ** level), q]
        pts = out
    return pts


def _stroke(d, pts, w0, w1):
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        w = w0 + (w1 - w0) * i / (len(pts) - 2)
        d.line([*(p * SS), *(q * SS)], fill=255, width=max(1, round(w * SS)))
        r = w * SS / 2
        d.ellipse([q[0] * SS - r, q[1] * SS - r, q[0] * SS + r, q[1] * SS + r], fill=255)


def render():
    rng = np.random.default_rng(SEED)
    img = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(img)
    trunk = _jagged(rng, START, END, 22)
    _stroke(d, trunk, 10, 2)
    for pos, side, length in BRANCHES:
        i = round(pos * (len(trunk) - 1))
        p = trunk[i]
        tip = (p[0] - length * 0.75, np.clip(p[1] + side * length * 0.42, TOP, BOTTOM))
        _stroke(d, _jagged(rng, p, tip, 5, depth=4), (10 + (2 - 10) * pos) * 0.7, 1)
    core = img.resize((W, H), Image.LANCZOS)
    halo = core.filter(ImageFilter.GaussianBlur(9))
    return (np.asarray(core, dtype=np.float32) / 255,
            np.clip(np.asarray(halo, dtype=np.float32) / 255 * 3.0, 0, 1))


def wave(t, period=6.0):
    """Respiración (0 a 1) por columna: el pulso nace en la lava y corre hacia la izquierda."""
    x = np.arange(W, dtype=np.float32)
    return (0.5 + 0.5 * np.sin(2 * np.pi * (t / period + (x - START[0]) / 1800)))[None, :, None]


def apply(frame, core, halo, beat):
    """frame: RGB float H x W x 3 en [0, 1]. beat: escalar o wave(t)."""
    c, h = core[..., None], halo[..., None]
    level = 0.30 + 0.70 * beat
    out = frame + h * level * 0.75 * np.array(COLD, np.float32)
    color = np.array(WARM, np.float32) + level * (np.array(HOT, np.float32) - np.array(WARM, np.float32))
    a = c * (0.55 + 0.45 * level)
    return out * (1 - a) + color * a
