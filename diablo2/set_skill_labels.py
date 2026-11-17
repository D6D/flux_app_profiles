"""Leyendas del perfil de Diablo II, por la API de Polymath.

    python diablo2/set_skill_labels.py

- Habilidades: estilo iconLabel (icono + nombre), o iconFull (solo icono) las de
  ICON_ONLY (base.py). El icono sale de icons_all/<Nombre>.png (extract_icons.py) y
  se importa con /config/addIcon; si no hay, Polymath pone uno genérico.
- Números (y º si no es habilidad): estilo single con el carácter, para quitar los
  símbolos alternativos (!, ", ·, $...).
- El resto de letras vuelve al estilo automático, por si tenían una habilidad antes.

Estilos en flux_api/Models/LegendStyle.md. Usa el cliente de flux_perf (clave de la API
y certificado), así que hay que lanzarlo con el Python de su .venv.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "flux_perf"))
from flux_perf.polymath import PolymathClient  # noqa: E402

from base import ICON_ONLY  # noqa: E402
from skills import SKILLS  # noqa: E402

PROFILE = "Diablo II: Resurrected"
ICON_LABEL, ICON_FULL, SINGLE = 2, 3, 10
AUTO = 0
KEY_CODES = {**{c: f"KC_{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}, "º": "KC_GRAVE"}
# C: al volver a automático tras tener habilidad, el teclado seguía enseñando «Decoy».
SINGLE_KEYS = {**{f"KC_{n}": str(n) for n in range(10)}, "KC_GRAVE": "º", "KC_C": "C"}
ICONS_DIR = HERE / "icons_all"
POLYMATH_ICONS = Path.home() / "Documents" / "flux" / "config" / "icons"
ICON_MAP = HERE / "work" / "icon_map.json"


def import_icons(client):
    """Importa los iconos que falten y devuelve {tecla: nombre del icono en Polymath}.

    /config/addIcon copia cada imagen con un nombre nuevo y devuelve esos nombres en el
    mismo orden (iconPaths). Se guardan en ICON_MAP, por hash del contenido, para no
    importar el mismo icono cada vez. Ojo: en iconAssetPath va el nombre a secas; con la
    ruta absoluta (lo que dice la documentación) Polymath responde OK pero guarda "null".
    """
    by_name = {p.stem.lower(): p for p in ICONS_DIR.glob("*.png")}
    files = {k: by_name[label.lower()] for k, label in SKILLS.items() if label.lower() in by_name}
    known = json.loads(ICON_MAP.read_text(encoding="utf-8")) if ICON_MAP.is_file() else {}
    digest = {k: hashlib.md5(p.read_bytes()).hexdigest() for k, p in files.items()}
    missing = [k for k in files if not (POLYMATH_ICONS / known.get(digest[k], "-")).is_file()]
    if missing:
        result = client.post("/config/addIcon", {"icons": [{"file": str(files[k])} for k in missing]}, timeout=60)
        for k, name in zip(missing, result["iconPaths"]):
            known[digest[k]] = name
        ICON_MAP.write_text(json.dumps(known, indent=1), encoding="utf-8")
    return {k: known[digest[k]] for k in files}


def main():
    client = PolymathClient()
    client.connect()
    layer0 = client.get("/config/keymapData")["message"]["0"]
    where = {k["action"].get("keyCode"): k["location"] for k in layer0}
    icons = import_icons(client)

    def entry(key_code, style):
        return {"profileName": PROFILE, "layer": 0, "newStyle": style,
                "model": {f: where[key_code][f] for f in ("width", "frameLayoutType", "row", "index")}}

    styles = []
    for key, label in SKILLS.items():
        style = {"style": ICON_FULL if key in ICON_ONLY else ICON_LABEL, "label": label}
        if key in icons:
            style["iconAssetPath"] = icons[key]
        styles.append(entry(KEY_CODES[key], style))
    skill_codes = {KEY_CODES[k] for k in SKILLS}
    styles += [entry(code, {"style": SINGLE, "label": label}) for code, label in SINGLE_KEYS.items()
               if code not in skill_codes]
    styles += [entry(code, {"style": AUTO}) for code in KEY_CODES.values()
               if code not in skill_codes and code not in SINGLE_KEYS]
    print(client.put("/config/addKeystyleToAppearance", {"styles": styles}))


if __name__ == "__main__":
    main()
