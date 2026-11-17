"""Habilidades asignadas en el juego: tecla -> nombre (el icono es icons_all/<nombre>.png).

Personaje: Amazona. Los atajos comunes y el Town Portal están en base.py; para otro
personaje basta con cambiar CHARACTER_SKILLS.

Estas teclas van resaltadas en rojo en el fondo y con icono + nombre en Polymath. Al
cambiar algo: make_video.py, tools/replace_theme_media.py y set_skill_labels.py.
"""
from base import BASE_SKILLS, ICON_ONLY, tints_for

CHARACTER_SKILLS = {
    "Q": "Lightning Fury",
    "E": "Throw",
    "R": "Plague Javelin",
    "S": "Slow Missiles",
    "D": "Decoy",
    "F": "Valkyrie",
    "Z": "Lightning Strike",
    "X": "Charged Strike",
}
SKILLS = {**CHARACTER_SKILLS, **BASE_SKILLS}
HIGHLIGHT = (set(SKILLS) - ICON_ONLY) | {"Caps"}   # Caps: alternar correr/andar, rojo sin habilidad
TINTS = tints_for(SKILLS)
