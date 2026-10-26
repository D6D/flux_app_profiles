"""Genera un perfil de Polymath (.flux) para el navegador Brave.

Brave está hecho sobre Chromium y usa los atajos de Chrome. Lista sacada de la ayuda
oficial de Google (https://support.google.com/chrome/answer/157179, Windows y Linux,
consultada el 26-oct-2026). Se omiten los que se hacen escribiendo o en dos pasos y el
zoom con Ctrl + y Ctrl -, porque en un teclado español esas teclas no están en la
posición US que usa la plantilla.

Uso:
    python brave/make_profile.py <plantilla.flux> <salida.flux>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from fluxfile import build_profile, parse_combo

APP = "Brave"
EXE = "brave.exe"

SHORTCUTS = [
    # Pestañas y ventanas
    ("New Window", "CTRL+N"), ("Private Window", "CTRL+SHIFT+N"),
    ("New Tab", "CTRL+T"), ("Reopen Tab", "CTRL+SHIFT+T"),
    ("Next Tab", "CTRL+TAB"), ("Next Tab", "CTRL+PAGE_DOWN"),
    ("Prev Tab", "CTRL+SHIFT+TAB"), ("Prev Tab", "CTRL+PAGE_UP"),
    *[(f"Tab {n}", f"CTRL+{n}") for n in range(1, 9)], ("Last Tab", "CTRL+9"),
    ("Home Page", "ALT+HOME"), ("Back", "ALT+LEFT"), ("Forward", "ALT+RIGHT"),
    ("Close Tab", "CTRL+W"), ("Close Tab", "CTRL+F4"), ("Close Window", "CTRL+SHIFT+W"),
    ("Move Tab L", "CTRL+SHIFT+PAGE_UP"), ("Move Tab R", "CTRL+SHIFT+PAGE_DOWN"),
    ("Full Screen", "F11"),
    # Funciones del navegador
    ("Menu", "ALT+F"), ("Bookmarks Bar", "CTRL+SHIFT+B"), ("Bookmarks", "CTRL+SHIFT+O"),
    ("History", "CTRL+H"), ("Downloads", "CTRL+J"), ("Task Manager", "SHIFT+ESCAPE"),
    ("Find", "CTRL+F"), ("Find", "F3"), ("Find Next", "CTRL+G"), ("Find Prev", "CTRL+SHIFT+G"),
    ("DevTools", "CTRL+SHIFT+J"), ("DevTools", "F12"), ("Clear Data", "CTRL+SHIFT+DELETE"),
    ("Help", "F1"), ("Profiles", "CTRL+SHIFT+M"), ("Caret Mode", "F7"),
    # Barra de direcciones
    ("Address Bar", "CTRL+L"), ("Address Bar", "ALT+D"), ("Address Bar", "F6"),
    ("Search", "CTRL+K"), ("Search", "CTRL+E"),
    # Página
    ("Print", "CTRL+P"), ("Save Page", "CTRL+S"), ("Reload", "F5"), ("Reload", "CTRL+R"),
    ("Hard Reload", "SHIFT+F5"), ("Hard Reload", "CTRL+SHIFT+R"), ("Stop", "ESCAPE"),
    ("Open File", "CTRL+O"), ("View Source", "CTRL+U"), ("Bookmark", "CTRL+D"),
    ("Bookmark All", "CTRL+SHIFT+D"), ("Reset Zoom", "CTRL+0"),
    ("Top", "HOME"), ("Bottom", "END"), ("Del Word", "CTRL+BACK"),
    ("Word Left", "CTRL+LEFT"), ("Word Right", "CTRL+RIGHT"),
]


def main():
    template, output = sys.argv[1], sys.argv[2]
    shortcuts = [("default", label, *parse_combo(combo)) for label, combo in SHORTCUTS]
    build_profile(template, output, APP, EXE, shortcuts)


if __name__ == "__main__":
    main()
