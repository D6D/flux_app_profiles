"""Fondo animado de Diablo II para el Polymath: la imagen fija cobra vida en un bucle.

    python diablo2/make_video.py [--seconds 12] [--fps 30] [--preview] [--base]

Efectos, todos periódicos para que el bucle no tenga salto:
- la lava fluye hacia abajo (una textura de vetas que se desplaza dentro de la lava)
  y titila por zonas;
- brasas que suben desde la lava;
- los ojos del demonio y el sigilo laten;
- placas de las teclas encima (tools/keyplates.py), con el halo rojo de las habilidades
  latiendo;
- grieta de lava que respira en la barra espaciadora (space_crack.py).

Sale diablo2/out/diablo2_bg.mp4 (H.264, 1920x1080). --preview hace 3 s a 15 fps para
probar rápido. --base hace out/diablo2_base.mp4, solo con los atajos comunes (base.py).
"""
import argparse
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "tools"))
import keyplates  # noqa: E402
from layout_es_iso import keys  # noqa: E402
import base  # noqa: E402
import skills  # noqa: E402
import space_crack  # noqa: E402

W, H = 1920, 1080
EYES = [(935, 148), (1011, 148)]
SIGIL_BOX = (1660, 20, 1910, 262)
# Zonas rojas que no son lava: aquí no nacen llamas ni chispas (cuernos, capucha y cara, sigilo).
NO_FIRE = [(640, 0, 1320, 170), (770, 0, 1160, 275), SIGIL_BOX]
EMBERS = 170
SEED = 666


def periodic_noise(rng, shape, keys_count):
    """Ruido suave en el espacio y periódico en el tiempo: keyframes en bucle."""
    frames = rng.standard_normal((keys_count, *shape)).astype(np.float32)

    def at(phase):
        """phase en [0, 1): interpolación Catmull-Rom entre keyframes, cerrando el bucle."""
        x = phase * keys_count
        i = int(x)
        t = x - i
        p0, p1, p2, p3 = (frames[(i + k) % keys_count] for k in (-1, 0, 1, 2))
        return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                      + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    return at


def upsample(field, size=(W, H)):
    return np.asarray(Image.fromarray(field, "F").resize(size, Image.BICUBIC), dtype=np.float32)


def tileable_streaks(rng, period, cols, rows):
    """Textura de vetas verticales que se repite cada `period` píxeles en vertical."""
    grid = rng.random((rows, cols)).astype(np.float32)
    tall = np.vstack([grid, grid, grid])
    big = upsample(tall, (W, period * 3))
    t = big[period:2 * period]
    return (t - t.min()) / (t.max() - t.min())


def lava_mask(bg):
    r, g = bg[..., 0], bg[..., 1]
    m = np.clip((r - 0.33) / 0.45, 0, 1) * np.clip((r - g - 0.10) / 0.25, 0, 1)
    img = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
    return np.asarray(img, dtype=np.float32) / 255


def radial(cx, cy, sigma):
    ys, xs = np.ogrid[:H, :W]
    return np.exp(-((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * sigma ** 2)).astype(np.float32)


class Embers:
    def __init__(self, rng, mask, loop_seconds):
        weights = (mask ** 2).ravel()
        weights /= weights.sum()
        self.rng_seed = rng.integers(1 << 30)
        self.spawns = rng.choice(W * H, size=(EMBERS, 4), p=weights)   # un sitio por ciclo
        self.cycles = rng.integers(2, 5, EMBERS)                        # ciclos por bucle
        self.offset = rng.random(EMBERS)
        self.life = rng.uniform(0.55, 0.95, EMBERS)
        self.speed = rng.uniform(25, 75, EMBERS)
        self.sway = rng.uniform(4, 16, EMBERS)
        self.size = rng.uniform(1.0, 2.6, EMBERS)
        self.loop = loop_seconds

    def draw(self, d, t):
        for i in range(EMBERS):
            period = self.loop / self.cycles[i]
            x = (t / period + self.offset[i])
            cycle = int(x) % self.cycles[i]
            phase = x - int(x)
            if phase > self.life[i]:
                continue
            age = phase * period
            env = math.sin(math.pi * phase / self.life[i])
            sy, sx = divmod(int(self.spawns[i, cycle]), W)
            px = sx + self.sway[i] * math.sin(2 * math.pi * phase * 2 + i)
            py = sy - self.speed[i] * age
            c = (int(255 * env), int(120 * env), int(30 * env))
            r = self.size[i]
            d.ellipse([px - r, py - r, px + r, py + r], fill=c)


def lava_surface(mask):
    """Borde superior de la lava: lava con roca oscura justo encima. De ahí salen las llamas."""
    above = np.zeros_like(mask)
    above[6:] = mask[:-6]
    s = np.clip(mask - above, 0, 1)
    for x0, y0, x1, y1 in NO_FIRE:
        s[y0:y1, x0:x1] = 0
    # Excepción: los ojos del demonio sí arden.
    for x, y in EYES:
        s = np.maximum(s, radial(x, y - 4, 7))
    img = Image.fromarray((s * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    return np.asarray(img, dtype=np.float32) / 255


def flame_source(surface, height=46):
    """La superficie «emite» hacia arriba, perdiendo fuerza con la altura."""
    src = np.zeros_like(surface)
    for dy in range(0, height, 2):
        shifted = np.zeros_like(surface)
        shifted[:H - dy] = surface[dy:]
        src = np.maximum(src, shifted * (1 - dy / height))
    return np.clip(src * 1.8, 0, 1)


class Bursts:
    """Chisporroteos: un fogonazo en la lava y un puñado de chispas que saltan y caen."""
    GRAVITY = 320

    def __init__(self, rng, surface, loop_seconds, count=18):
        weights = (surface ** 2).ravel()
        weights /= weights.sum()
        self.loop = loop_seconds
        self.bursts = []
        for t0, pos in zip(rng.uniform(0, loop_seconds, count), rng.choice(W * H, size=count, p=weights)):
            y, x = divmod(int(pos), W)
            n = rng.integers(12, 26)
            sparks = list(zip(rng.normal(0, 70, n), -rng.uniform(90, 260, n), rng.uniform(0.35, 0.95, n),
                              rng.uniform(0.8, 1.8, n)))
            self.bursts.append((t0, x, y, sparks))

    def draw(self, d, t):
        for t0, x, y, sparks in self.bursts:
            age = (t - t0) % self.loop
            if age > 1.0:
                continue
            if age < 0.25:
                k = 1 - age / 0.25
                r = 6 + 16 * k
                d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(int(255 * k), int(150 * k), int(50 * k)))
            for vx, vy, life, size in sparks:
                if age > life:
                    continue
                k = 1 - age / life

                def pos(a):
                    return x + vx * a, y + vy * a + 0.5 * self.GRAVITY * a * a
                (x0, y0), (x1, y1) = pos(max(age - 0.035, 0)), pos(age)
                c = (255, int(110 + 120 * k), int(40 * k))
                d.line([x0, y0, x1, y1], fill=tuple(int(v * k) for v in c), width=max(1, round(size)))


def particles(embers, bursts, t):
    layer = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(layer)
    embers.draw(d, t)
    bursts.draw(d, t)
    glow = layer.filter(ImageFilter.GaussianBlur(3))
    return (np.asarray(layer, dtype=np.float32) + 1.5 * np.asarray(glow, dtype=np.float32)) / 255


def bloom(field, scale=4, radius=6):
    """Resplandor barato: difuminar a baja resolución y volver a ampliar."""
    small = Image.fromarray((np.clip(field, 0, 1) * 255).astype(np.uint8)).resize((W // scale, H // scale), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(radius))   # GaussianBlur no admite modo F
    return upsample(np.asarray(small, dtype=np.float32) / 255)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=12)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--base", action="store_true")
    args = ap.parse_args()
    if args.preview:
        args.seconds, args.fps = 3, 15

    rng = np.random.default_rng(SEED)
    bg = np.asarray(Image.open(HERE / "background_1920.png").convert("RGB"), dtype=np.float32) / 255
    mask = lava_mask(bg)
    m3 = mask[..., None]

    flicker = periodic_noise(rng, (H // 60, W // 60), 6)
    streak_period = 270
    streaks = [tileable_streaks(rng, streak_period, 220, 5), tileable_streaks(rng, streak_period, 140, 3)]

    eyes = sum(radial(x, y, 9) + 0.5 * radial(x, y, 28) for x, y in EYES)[..., None]
    x0, y0, x1, y1 = SIGIL_BOX
    sigil = np.zeros((H, W), np.float32)
    s = bg[y0:y1, x0:x1]
    sigil[y0:y1, x0:x1] = np.clip((s[..., 0] - 0.45) / 0.4, 0, 1) * (s[..., 1] < 0.35)
    sigil = sigil[..., None]

    ember_mask = mask.copy()      # ni brasas en la capucha, la cara o el sigilo
    for ex0, ey0, ex1, ey1 in NO_FIRE:
        ember_mask[ey0:ey1, ex0:ex1] = 0
    embers = Embers(rng, ember_mask, 12.0)
    surface = lava_surface(mask)
    flames_src = flame_source(surface)
    flame_period = 180
    flame_tex = [tileable_streaks(rng, flame_period, 300, 4), tileable_streaks(rng, flame_period, 170, 3)]
    bursts = Bursts(rng, surface, 12.0)
    if args.base:
        highlight, tints = set(base.BASE_SKILLS) - base.ICON_ONLY, base.BASE_TINTS
    else:
        highlight, tints = skills.HIGHLIGHT, skills.TINTS
    plates, glow = keyplates.render(keys(), highlight=highlight, tints=tints)
    plates = np.asarray(plates, dtype=np.float32) / 255
    glow = np.asarray(glow, dtype=np.float32) / 255
    crack_core, crack_halo = space_crack.render()

    out_dir = HERE / "out"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / ("preview.mp4" if args.preview else "diablo2_base.mp4" if args.base else "diablo2_bg.mp4")
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(args.fps), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)

    loop = 12.0   # todos los periodos dividen a 12 s; --seconds solo recorta o repite
    n = round(args.seconds * args.fps)
    for f in range(n):
        t = (f / args.fps) % loop
        ph = t / loop
        # Lava: vetas que bajan (2 y 3 vueltas por bucle) y titileo por zonas.
        flow = 0.5 * (np.roll(streaks[0], int(2 * streak_period * ph), axis=0)[np.arange(H) % streak_period]
                      + np.roll(streaks[1], int(3 * streak_period * ph), axis=0)[np.arange(H) % streak_period])
        flick = upsample(flicker(ph))
        light = 1 + 0.18 * flick[..., None] + 0.9 * (flow[..., None] - 0.5)
        frame = bg * (1 + m3 * (light - 1))
        frame += m3 * np.clip(flow[..., None] - 0.55, 0, 1) * np.array([0.9, 0.35, 0.05], np.float32)

        beat_eyes = 0.5 + 0.5 * math.sin(2 * math.pi * t / 4)        # 3 por bucle
        frame += eyes * (0.25 + 0.6 * beat_eyes) * np.array([1.0, 0.12, 0.04], np.float32)
        beat_sigil = 0.5 + 0.5 * math.sin(2 * math.pi * t / 6 + 1)   # 2 por bucle
        frame *= 1 + sigil * 0.7 * beat_sigil
        # Llamas: textura que sube (3 y 4 vueltas por bucle) recortada por la fuente; el
        # umbral hace las lenguas, y el color va de rojo (débil) a amarillo (fuerte).
        rows = np.arange(H) % flame_period
        noise = (0.6 * np.roll(flame_tex[0], -int(3 * flame_period * ph), axis=0)[rows]
             + 0.4 * np.roll(flame_tex[1], -int(4 * flame_period * ph), axis=0)[rows])
        fire = np.clip(flames_src * 1.35 - (1 - noise) * 1.05, 0, 1)
        fire_rgb = np.stack([fire, fire ** 1.6 * 0.72, fire ** 3 * 0.35], axis=-1)
        frame += fire_rgb + bloom(fire)[..., None] * np.array([0.55, 0.16, 0.02], np.float32)
        frame += particles(embers, bursts, t)

        a = plates[..., 3:]
        frame = frame * (1 - a) + plates[..., :3] * a
        beat_keys = 0.7 + 0.3 * math.sin(2 * math.pi * t / 3)         # 4 por bucle
        ga = glow[..., 3:] * beat_keys
        frame = frame * (1 - ga) + glow[..., :3] * ga
        frame = space_crack.apply(frame, crack_core, crack_halo, space_crack.wave(t))

        ff.stdin.write((np.clip(frame, 0, 1) * 255).astype(np.uint8).tobytes())
        if f % 30 == 0:
            print(f"{f}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print(out, f"{out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
