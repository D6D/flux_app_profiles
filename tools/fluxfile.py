"""Generar perfiles de Polymath (.flux) con un juego de atajos propio.

Polymath solo trae plantillas de atajos para 41 programas y no carga plantillas nuevas,
pero sí importa perfiles .flux (Shortcuts → Import). Este módulo construye uno a partir
de un .flux exportado desde Polymath, que sirve de plantilla (tema, actuación y mapa de
teclas), cambiándole el perfil y los atajos.

Formato .flux (deducido de una exportación de Polymath 1.4.5.7):
    u32 longitud + JSON  ·  u32 nº de adjuntos  ·  por adjunto: u32 + nombre, u32 + datos  ·  u32 0

Después de importarlo hay que grabar en el teclado (Save to Keyboard): es el teclado el
que cambia de perfil al detectar el programa, y hasta entonces no tiene el perfil nuevo.
"""
import copy
import json
import struct
import uuid
from pathlib import Path

# Tecla -> (código HID, keyCode de Polymath, constante VK, nombre en Polymath).
# Son posiciones físicas (distribución US). El teclado no tiene teclado numérico.
KEYS = {
    **{c: (4 + i, f"KC_{c}", f"VK_{c}", c) for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")},
    **{str(n): (30 + (n - 1) % 10, f"KC_{n}", f"VK_{n}", str(n)) for n in range(10)},
    **{f"F{n}": (57 + n, f"KC_F{n}", f"VK_F{n}", f"F{n}") for n in range(1, 13)},
    "RETURN": (40, "KC_ENTER", "VK_RETURN", "Return"),
    "ESCAPE": (41, "KC_ESCAPE", "VK_ESCAPE", "Esc"),
    "BACK": (42, "KC_BACKSPACE", "VK_BACK", "Backspace"),
    "TAB": (43, "KC_TAB", "VK_TAB", "Tab"),
    "SPACE": (44, "KC_SPACE", "VK_SPACE", "Spacebar"),
    "MINUS": (45, "KC_MINUS", "VK_OEM_MINUS", "-"),
    "EQUALS": (46, "KC_EQUAL", "VK_OEM_PLUS", "="),
    "COMMA": (54, "KC_COMMA", "VK_OEM_COMMA", ","),
    "PERIOD": (55, "KC_DOT", "VK_OEM_PERIOD", "."),
    "CAPITAL": (57, "KC_CAPS_LOCK", "VK_CAPITAL", "Caps Lock"),
    "INSERT": (73, "KC_INSERT", "VK_INSERT", "Insert"),
    "HOME": (74, "KC_HOME", "VK_HOME", "Home"),
    "PAGE_UP": (75, "KC_PAGE_UP", "VK_PRIOR", "PageUp"),
    "DELETE": (76, "KC_DELETE", "VK_DELETE", "Delete"),
    "END": (77, "KC_END", "VK_END", "End"),
    "PAGE_DOWN": (78, "KC_PAGE_DOWN", "VK_NEXT", "PageDown"),
    "RIGHT": (79, "KC_RIGHT", "VK_RIGHT", "Right Arrow"),
    "LEFT": (80, "KC_LEFT", "VK_LEFT", "Left Arrow"),
    "DOWN": (81, "KC_DOWN", "VK_DOWN", "Down Arrow"),
    "UP": (82, "KC_UP", "VK_UP", "Up Arrow"),
    "OEM_102": (100, "KC_NONUS_BACKSLASH", "VK_OEM_102", "<>"),
}
MODIFIERS = {"CTRL": "WIN_CTRL", "SHIFT": "WIN_SHIFT", "ALT": "WIN_ALT"}


def read_flux(path):
    b = Path(path).read_bytes()
    n = struct.unpack_from("<I", b, 0)[0]
    data = json.loads(b[4:4 + n])
    pos, files = 4 + n, []
    count = struct.unpack_from("<I", b, pos)[0]
    pos += 4
    for _ in range(count):
        ln = struct.unpack_from("<I", b, pos)[0]
        name = b[pos + 4:pos + 4 + ln].decode("utf-8")
        pos += 4 + ln
        dl = struct.unpack_from("<I", b, pos)[0]
        files.append((name, b[pos + 4:pos + 4 + dl]))
        pos += 4 + dl
    if b[pos:] != b"\0\0\0\0":
        raise ValueError(f"Final inesperado en {path}: {b[pos:]!r}")
    return data, files


def write_flux(path, data, files):
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    out = [struct.pack("<I", len(js)), js, struct.pack("<I", len(files))]
    for name, blob in files:
        nb = name.encode("utf-8")
        out += [struct.pack("<I", len(nb)), nb, struct.pack("<I", len(blob)), blob]
    out.append(b"\0\0\0\0")
    Path(path).write_bytes(b"".join(out))


def parse_combo(combo):
    """'CTRL+SHIFT+T' -> ({'CTRL', 'SHIFT'}, 'T')."""
    *mods, key = combo.upper().split("+")
    unknown = set(mods) - MODIFIERS.keys()
    if unknown or key not in KEYS:
        raise ValueError(f"Combinación no soportada: {combo}")
    return set(mods), key


def shortcut_entry(app, i, context, label, mods, key):
    hid, kc, vk, key_name = KEYS[key]
    combo = {flag: mod in mods for mod, flag in MODIFIERS.items()}
    return {
        "id": f"{app}_{label}_{i}",
        "applicationContext": context,
        "collectionName": app,
        "isSvg": False,
        "builtInIcon": True,
        "shortcutKey": {
            "win_us_key1_constant": vk,
            "HidKeyCode": {"lctrl": False, "lshift": False, "lalt": False, "lmeta": False,
                           "rctrl": False, "rshift": False, "ralt": False, "rmeta": False,
                           "keycode": hid, "type": 0},
            "win_us_key1": key_name,
            "mac_us_key1_constant": "",
            "mac_us_key1": "",
            "keyCode": kc,
        },
        "shortcutLabel": label,
        "keyCombo": {**combo, "WIN_WINKEY": False, "WIN_US_KEY1_CONSTANT": True, "MAC_CMD": False,
                     "MAC_CTRL": False, "MAC_SHIFT": False, "MAC_OPT": False, "MAC_FN": False,
                     "MAC_US_KEY1_CONSTANT": False},
    }


def build_profile(template, output, app, exe, shortcuts, profile_id=None):
    """shortcuts: lista de (contexto, etiqueta, modificadores, tecla).

    Los IDs del perfil y del mapa de teclas salen del nombre del programa (uuid5): así,
    si se vuelve a generar e importar, Polymath actualiza el mismo perfil en vez de crear
    otro. profile_id fuerza un ID concreto (para perfiles ya importados con otro).
    """
    data, files = read_flux(template)
    data = copy.deepcopy(data)
    profile = data["profile"][0]
    profile.update(id=profile_id or str(uuid.uuid5(uuid.NAMESPACE_URL, f"flux-profile:{app}")), name=app,
                   associatedProcess=exe, selectedShortcutApplication=app)
    for km in data["keymaps"]:
        km["data"]["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"flux-keymap:{app}:{km['layer']}"))
    contexts = list(dict.fromkeys(s[0] for s in shortcuts))
    data["shortcuts"] = [{
        "applicationName": app,
        "sourceTemplate": app,
        "shortcuts": [shortcut_entry(app, i, *s) for i, s in enumerate(shortcuts, 1)],
        "deltas": {},
        "applicationContexts": ["all", *contexts],
    }]
    write_flux(output, data, files)

    seen = {}
    for ctx, label, mods, key in shortcuts:
        seen.setdefault((ctx, frozenset(mods), key), []).append(label)
    conflicts = {k: v for k, v in seen.items() if len(set(v)) > 1}
    print(f"{output}: {app} ({exe}), {len(shortcuts)} atajos")
    for ctx in contexts:
        print(f"  {ctx}: {sum(s[0] == ctx for s in shortcuts)}")
    if conflicts:
        print("  Conflictos:", conflicts)
