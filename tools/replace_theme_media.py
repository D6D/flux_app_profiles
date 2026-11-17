"""Cambia el fondo de un tema de Polymath por otro fichero, sin pasar por la interfaz.

    <python de flux_perf> tools/replace_theme_media.py "Diablo II" diablo2/out/diablo2_bg.mp4

Polymath solo lee su configuración al arrancar y la reescribe al cerrarse, así que:
cierra Polymath, añade el fichero a su biblioteca con un ID NUEVO, apunta el tema a él,
borra el fondo anterior si ningún otro tema lo usa, vuelve a abrir Polymath y graba en
el teclado.

El ID tiene que ser nuevo: el teclado guarda su propia copia de los fondos por ID, y si
se pisa el fichero con el mismo nombre, Polymath lo enseña bien pero el teclado sigue
con el viejo. Reutiliza el cierre y arranque de flux_perf (mosaic_switch), por eso se
lanza con su Python.
"""
import copy
import json
import logging
import shutil
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "flux_perf"))
from flux_perf.mosaic_switch import MosaicSwitcher  # noqa: E402
from flux_perf.polymath import CONFIG_DIR  # noqa: E402

APPEARANCE = CONFIG_DIR / "appearance.json"
MEDIA_JSON = CONFIG_DIR / "media.json"
MEDIA_DIR = CONFIG_DIR / "media"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def main(theme_name, new_file):
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    new_file = Path(new_file).resolve()
    switcher = MosaicSwitcher([])
    # Primero cerrar: al cerrarse, Polymath reescribe appearance.json y media.json.
    switcher._close_polymath()

    appearance = load(APPEARANCE)
    themes = [appearance["defaultTheme"], *appearance["customThemes"]]
    theme = next((t for t in themes if t["name"] == theme_name), None)
    if not theme:
        switcher._start_polymath_and_save()
        sys.exit(f"No hay ningún tema llamado {theme_name!r}: {[t['name'] for t in themes]}")
    old_name = theme["backgroundImagePath"]

    media = load(MEDIA_JSON)
    old_entry = next((f for f in media["files"] if f["name"] == old_name), None)
    new_id = uuid.uuid4().hex
    new_name = f"{new_id}{new_file.suffix.lower()}"
    shutil.copyfile(new_file, MEDIA_DIR / new_name)
    entry = copy.deepcopy(old_entry) if old_entry else {"type": 1 if new_file.suffix.lower() == ".mp4" else 0,
                                                        "deletable": True}
    entry.update(id=new_id, name=new_name, size=float(new_file.stat().st_size))
    media["files"].append(entry)
    theme["backgroundImagePath"] = new_name

    if not any(t["backgroundImagePath"] == old_name for t in themes):
        media["files"] = [f for f in media["files"] if f["name"] != old_name]
        (MEDIA_DIR / old_name).unlink(missing_ok=True)
        for thumb in (MEDIA_DIR / "thumbnails").glob(f"{Path(old_name).stem}_*"):
            thumb.unlink()

    save(MEDIA_JSON, media)
    save(APPEARANCE, appearance)
    print(f"{theme_name}: fondo {old_name} -> {new_name} ({new_file.name})")
    switcher._start_polymath_and_save()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
