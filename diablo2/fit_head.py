"""Encoge la cabeza y el sigilo para que quepan encima de la barra física del Polymath.

    python diablo2/fit_head.py     # work/new_bg/x4.png -> background_1920.png

Entre los módulos y las teclas hay una barra opaca que tapa y≈255-295 (foto
calibration1.jpg, zona ampliada): lo que tenga que verse entero acaba antes de y=245.
Por encima de la barra, cada zona se reduce con un zoom local que se funde con el cielo.
Por debajo se usa la imagen original, y el salto queda escondido tras la barra (SEAM).
Debajo solo se salta lo que ya se ve arriba (barbilla y sigilo): SKIP.
"""
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
W, H = 3840, 2160          # se trabaja a doble resolución y se reduce al final
K = W / 1920
# ax,ay: punto de destino que se queda en su sitio tras el zoom (sx,sy en origen).
# zone: x0,y0,x1,y1 en destino con zoom pleno; fade: margen de fundido (izq,arr,der,aba).
HEAD = dict(scale=0.75, target=(960, 0), source=(960, 0), zone=(590, -50, 1310, 300), fade=(270, 1, 215, 1))
SIGIL = dict(scale=0.75, target=(1790, 143), source=(1773, 250), zone=(1675, 30, 1890, 300), fade=(125, 29, 30, 1))
SEAM = 275
# Bajo la barra: x0, x1 (con fundido), píxeles que se saltan junto a la barra, alto del fundido.
SKIP = [(500, 1420, 40, 200), (1620, 2100, 100, 260)]


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def warp_field(xs, ys, z):
    """Devuelve el peso del zoom y el origen zoomeado, en píxeles de 1920x1080."""
    x0, y0, x1, y1 = z["zone"]
    l, t, r, b = z["fade"]
    w = smooth((xs - (x0 - l)) / l) * smooth(((x1 + r) - xs) / r) * smooth((ys - (y0 - t)) / t) * smooth(((y1 + b) - ys) / b)
    tx, ty = z["target"]
    sx, sy = z["source"]
    return w, sx + (xs - tx) / z["scale"], sy + (ys - ty) / z["scale"]


def main():
    x4 = Image.open(HERE / "work" / "new_bg" / "x4.png").convert("RGB")
    cw = round(x4.height * 16 / 9)
    cx = (x4.width - cw) // 2
    src = np.asarray(x4.crop((cx, 0, cx + cw, x4.height)).resize((W, H), Image.LANCZOS), dtype=np.float32)

    ys, xs = np.mgrid[:H, :W].astype(np.float32)
    xs, ys = xs / K, ys / K
    mx, my = xs.copy(), ys.copy()
    for z in (HEAD, SIGIL):
        w, zx, zy = warp_field(xs, ys, z)
        mx, my = mx * (1 - w) + zx * w, my * (1 - w) + zy * w
    low_y = ys.copy()
    for x0, x1, skip, fade in SKIP:
        side = smooth((xs - x0) / 100) * smooth((x1 - xs) / 100)
        low_y += skip * side * (1 - smooth((ys - SEAM) / fade))
    below = ys >= SEAM
    mx, my = np.where(below, xs, mx), np.where(below, low_y, my)
    edge = round(SEAM * K)
    fold = min(np.diff(mx, axis=1).min(), np.diff(my[:edge], axis=0).min(), np.diff(my[edge:], axis=0).min())
    if fold <= 0:
        raise SystemExit(f"La deformación se pliega sobre sí misma ({fold:.4f}): ajusta los márgenes")

    mx, my = np.clip(mx * K, 0, W - 1.001), np.clip(my * K, 0, H - 1.001)
    x0, y0 = mx.astype(np.int32), my.astype(np.int32)
    fx, fy = (mx - x0)[..., None], (my - y0)[..., None]
    out = (src[y0, x0] * (1 - fx) * (1 - fy) + src[y0, x0 + 1] * fx * (1 - fy)
           + src[y0 + 1, x0] * (1 - fx) * fy + src[y0 + 1, x0 + 1] * fx * fy)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).resize((W // 2, H // 2), Image.LANCZOS)
    img.save(HERE / "background_1920.png")
    print("background_1920.png")


if __name__ == "__main__":
    main()
