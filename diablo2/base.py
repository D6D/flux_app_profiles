"""Base común a todos los personajes de Diablo II: atajos del juego y Town Portal.

Cada personaje (skills.py) parte de aquí y solo añade sus habilidades, que van en rojo.
Si un personaje usa una de estas teclas para una habilidad, gana la habilidad.

    python make_still.py --base     # base_still.png / base_preview.png
    python make_video.py --base     # out/diablo2_base.mp4: fondo sin habilidades

Formato de tools/keyplates.py: degradado top→bottom con alfa, borde y halo opcional.
El degradado va de claro arriba a oscuro abajo: al revés, la placa parecía caerse de la tecla.
"""
PARCHMENT = dict(top=(128, 102, 56), bottom=(92, 74, 40), alpha=120, edge=(176, 146, 88, 220))
CUBE = dict(top=(186, 144, 54), bottom=(140, 105, 38), alpha=150, edge=(232, 190, 100, 255), glow=(230, 170, 60))
MAP = dict(top=(104, 70, 38), bottom=(72, 46, 24), alpha=130, edge=(150, 108, 66, 220))
LIFE = dict(top=(140, 18, 26), bottom=(96, 8, 14), alpha=130, edge=(196, 48, 52, 230))
MANA = dict(top=(26, 46, 150), bottom=(14, 24, 96), alpha=130, edge=(80, 118, 220, 230))
PORTAL = dict(top=(110, 150, 215), bottom=(36, 78, 176), alpha=150, edge=(225, 240, 255, 255), glow=(150, 200, 255))

# A ficha, T habilidades, B inventario, O mercenario, Alt objetos, Ctrl correr,
# Shift quieto y atacar, H cubo, Tab mapa, 1 pociones de vida, 2-4 de maná.
SYSTEM_TINTS = {**{k: PARCHMENT for k in ("A", "T", "B", "O", "LAlt", "LCtrl", "LShift")},
                "H": CUBE, "Tab": MAP, "1": LIFE, "2": MANA, "3": MANA, "4": MANA}

# Town Portal: lo lleva todo personaje. Solo icono (estilo iconFull) y placa azul portal.
BASE_SKILLS = {"º": "Town Portal"}
ICON_ONLY = {"º"}
BASE_TINTS = {"º": PORTAL, **SYSTEM_TINTS}


def tints_for(skills):
    """Placas de color de un personaje: la base menos las teclas que usa para habilidades."""
    return {k: t for k, t in BASE_TINTS.items() if k not in skills or k in ICON_ONLY}
