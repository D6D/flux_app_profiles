"""Perfil de Polymath para Diablo II: Resurrected con el tema del fondo animado.

    python diablo2/make_profile.py <plantilla.flux> <tema.flux> [salida.flux]

- plantilla.flux: un perfil exportado de Polymath; de él salen el mapa de teclas ISO y
  la actuación (p. ej. total-war-warhammer-3/tww3.flux).
- tema.flux: el tema «Diablo II» exportado desde Polymath (Create New → Export, solo el
  tema), con el vídeo de make_video.py ya puesto de fondo. Se copia tal cual, vídeo
  incluido.

¿Por qué no se genera el tema desde cero? Porque Polymath 1.4.5.7 rechaza ese .flux
(«The Flux import file is corrupted») y no dice por qué. El tema construido a mano solo
difería del exportado en IDs, colores, escala y autoStyleConfig, y el ID del vídeo no es
un hash del contenido. Con el tema exportado entra a la primera.

Las etiquetas de las habilidades se ponen después por la API (set_skill_labels.py).
Ojo: cada importación crea un perfil y un tema nuevos («... 2») aunque los IDs coincidan.
"""
import copy
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "tools"))
from fluxfile import read_flux, write_flux  # noqa: E402

NAME = "Diablo II: Resurrected"
EXE = "D2R.exe"


def uid(what):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"flux-diablo2:{what}"))


def main(template, theme_export, output):
    data, _ = read_flux(template)
    theme, files = read_flux(theme_export)
    data = copy.deepcopy(data)
    data["appearance"], data["media"] = theme["appearance"], theme["media"]

    profile = data["profile"][0]
    # Sin atajos, pero la colección tiene que existir (con la lista vacía tampoco entra).
    profile.update(id=uid("profile"), name=NAME, associatedProcess=EXE,
                   themeId=theme["appearance"][0]["id"], selectedShortcutApplication=NAME)
    for km in data["keymaps"]:
        km["data"]["id"] = uid(f"keymap:{km['layer']}")
    data["shortcuts"] = [{"applicationName": NAME, "sourceTemplate": NAME, "shortcuts": [], "deltas": {},
                          "applicationContexts": ["all"]}]

    write_flux(output, data, files)
    print(f"{output}: {NAME} ({EXE}), tema «{theme['appearance'][0]['name']}»")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else str(HERE / "out" / "diablo2.flux"))
