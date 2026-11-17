"""Recorta los iconos de habilidades de la Amazona del árbol de habilidades (captura de
Icy Veins, 1543x871) y los deja como dibujo blanco sobre transparente en icons_all/.

    python diablo2/extract_icons.py "<captura del árbol>.png"

Polymath recolorea los iconos con el color de las leyendas (retintIcons), así que
interesa la silueta, no el color del juego.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
SIZE = 128
PORTAL_DY = -12  # y sentado se veía bajo
PORTAL_SCALE = 0.85  # con 0,9 se cortaba por arriba al subirlo
PORTAL_DX = 10   # en el teclado, el remolino del Town Portal se veía desplazado a la izquierda
# Esquina superior izquierda de cada icono en la captura.
TREE = {
    "Jab": (98, 113), "Power Strike": (236, 227), "Poison Javelin": (374, 227), "Impale": (98, 341),
    "Lightning Bolt": (374, 341), "Charged Strike": (236, 455), "Plague Javelin": (374, 455),
    "Fend": (98, 569), "Lightning Strike": (236, 683), "Lightning Fury": (374, 683),
    "Inner Sight": (598, 113), "Critical Strike": (874, 113), "Dodge": (736, 227), "Slow Missiles": (598, 341),
    "Avoid": (736, 341), "Penetrate": (874, 455), "Decoy": (598, 569), "Evade": (736, 569),
    "Valkyrie": (598, 683), "Pierce": (874, 683),
    "Magic Arrow": (1236, 113), "Fire Arrow": (1374, 113), "Cold Arrow": (1098, 227), "Multiple Shot": (1236, 227),
    "Exploding Arrow": (1374, 341), "Ice Arrow": (1098, 455), "Guided Arrow": (1236, 455), "Strafe": (1236, 569),
    "Immolation Arrow": (1374, 569), "Freezing Arrow": (1098, 683),
}


def glyph(crop):
    """El dibujo es gris claro y poco saturado; el fondo, marrón más oscuro."""
    a = np.asarray(crop.convert("RGB"), dtype=np.float32)
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    alpha = np.clip((lum - 125) / 70, 0, 1) * np.clip((70 - sat) / 40, 0, 1)
    h, w = alpha.shape
    alpha[int(h * 0.82):, int(w * 0.82):] = 0   # la casilla de puntos del árbol asoma en la esquina
    out = np.zeros((*alpha.shape, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out).resize((SIZE, SIZE), Image.LANCZOS)


def shift(icon, dx, dy=0, scale=0.9):
    """Mueve el dibujo dx píxeles a la derecha y dy hacia abajo, reducido para que no se corte por el borde."""
    small = icon.resize((round(icon.width * scale), round(icon.height * scale)), Image.LANCZOS)
    out = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    out.paste(small, ((icon.width - small.width) // 2 + dx, (icon.height - small.height) // 2 + dy))
    return out


def main(tree_png):
    src = Image.open(tree_png)
    out_dir = HERE / "icons_all"
    out_dir.mkdir(exist_ok=True)
    cols = 6
    sheet = Image.new("RGB", (cols * 170, (len(TREE) + cols - 1) // cols * 190), (40, 20, 15))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("arial.ttf", 15)
    for i, (name, (x, y)) in enumerate(TREE.items()):
        icon = glyph(src.crop((x + 7, y + 7, x + 71, y + 71)))
        icon.save(out_dir / f"{name}.png")
        cx, cy = (i % cols) * 170 + 21, (i // cols) * 190 + 10
        sheet.paste(icon, (cx, cy), icon)
        d.text((cx + SIZE // 2, cy + SIZE + 10), name, font=font, fill="white", anchor="mt")
    # Lanzar (Throw) no está en el árbol: sale de la barra del juego (diablo2/ingame1.png).
    if (HERE / "ingame1.png").is_file():
        game = Image.open(HERE / "ingame1.png")
        throw = glyph(game.crop((1108 + 6, 890 + 4, 1108 + 58, 890 + 56)))
        throw.paste((0, 0, 0, 0), (int(SIZE * 0.85), 0, SIZE, int(SIZE * 0.25)))   # la «R» del atajo
        throw.save(out_dir / "Throw.png")
        # Town Portal: el remolino del tomo de portales (con el número de cargas abajo).
        portal = glyph(game.crop((1040 + 6, 752 + 4, 1040 + 58, 752 + 56)))
        portal.paste((0, 0, 0, 0), (int(SIZE * 0.85), 0, SIZE, int(SIZE * 0.25)))
        portal = shift(portal, PORTAL_DX, PORTAL_DY, PORTAL_SCALE)
        portal.save(out_dir / "Town Portal.png")
    sheet.save(HERE / "work" / "icons_all_sheet.png")
    print(f"{len(TREE)} iconos en {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1])
