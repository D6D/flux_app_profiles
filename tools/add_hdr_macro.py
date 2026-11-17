"""Pone en la tecla Pausa una macro «HDR» que pulsa Win+Alt+B (activar/desactivar HDR en Windows).

    <python de flux_perf> tools/add_hdr_macro.py

La API de Polymath solo deja LEER el keymap, así que se edita keymap.json con Polymath
cerrado (lo reescribe al cerrarse), igual que replace_theme_media.py. Crea la macro si
no existe y la asigna a la Pausa (posición 14 del ISO) en todas las capas base que
tengan KC_PAUSE normal; respeta las que ya llevan otra macro (Brave → «Priv»).
"""
import json
import logging
import shutil
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "flux_perf"))
from flux_perf.mosaic_switch import MosaicSwitcher  # noqa: E402
from flux_perf.polymath import CONFIG_DIR  # noqa: E402

KEYMAP = CONFIG_DIR / "keymap.json"
PAUSE_INDEX = 14
NAME = "HDR"
SEQUENCE = ["KC_LEFT_GUI", "KC_LEFT_ALT", "KC_B"]


def steps():
    press = [{"keyCode": k, "delayMs": 5, "isRelease": False} for k in SEQUENCE]
    release = [{"keyCode": k, "delayMs": 5, "isRelease": True} for k in reversed(SEQUENCE)]
    return press + release


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    switcher = MosaicSwitcher([])
    switcher._close_polymath()

    backup = KEYMAP.with_name(f"keymap.json.{int(time.time())}.pre_hdr.bak")
    shutil.copyfile(KEYMAP, backup)
    logging.info("Copia de seguridad: %s", backup)

    data = json.loads(KEYMAP.read_text(encoding="utf-8"))
    macros = data.setdefault("macros", {})
    macro = next((m for m in macros.values() if m["name"] == NAME), None)
    if macro is None:
        macro_id = str(uuid.uuid4())
        macros[macro_id] = {"id": macro_id, "name": NAME, "steps": steps(),
                            "useFixedTiming": False, "fixedDelayMs": 10}
    else:
        macro_id = macro["id"]
        macro["steps"] = steps()

    for i, layer in enumerate(data["keymaps"]["iso"]["layers"]):
        action = layer["keyActions"][PAUSE_INDEX]
        if action.get("keyCode") == "KC_PAUSE" or action.get("macroId") == macro_id:
            layer["keyActions"][PAUSE_INDEX] = {"macroId": macro_id, "cachedName": NAME, "type": 1}
            logging.info("Capa %d (%s): Pausa -> %s", i, layer["name"], NAME)
        elif action.get("type") == 1:
            logging.info("Capa %d (%s): se deja la macro %s", i, layer["name"], action.get("cachedName"))

    KEYMAP.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    switcher._start_polymath_and_save()


if __name__ == "__main__":
    main()
