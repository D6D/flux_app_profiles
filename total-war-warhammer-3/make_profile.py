"""Genera un perfil de Polymath (.flux) para Total War: Warhammer III con sus atajos.

Las teclas salen del propio juego (data/text/default_keys.xml), así que son las de serie
de la versión instalada. Las etiquetas cortas que se ven en las teclas están en LABELS.
El resto del .flux (tema, actuación, mapa de teclas) se copia de un .flux exportado
desde Polymath, que sirve de plantilla.

Ver tools/fluxfile.py para el formato .flux y cómo se importa.

Uso:
    python total-war-warhammer-3/make_profile.py <plantilla.flux> <salida.flux> [ruta del juego]
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from fluxfile import KEYS, build_profile

APP = "Total War: Warhammer III"
EXE = "Warhammer3.exe"
DEFAULT_GAME = Path(r"D:\SteamLibrary\steamapps\common\Total War WARHAMMER III")
CONTEXTS = {"universal": "Universal", "campaign": "Campaign", "battle": "Battle"}
# ID con el que se importó el perfil el 26-oct-2026; se mantiene para que al regenerarlo se actualice
PROFILE_ID = "5b9f1058-a3e8-4268-b3f5-db7d5423fa91"

# Modificadores que en el juego significan «con o sin»: la tecla va sola
LOOSE_MODIFIERS = {None, "ALLOW_SHIFT", "ANY", "ANY_EXCEPT_CTRL"}

LABELS = {
    # universal
    "select_all": "Select All", "select_next": "Next Unit", "select_prev": "Prev Unit",
    "current_selection_order_cancel": "Cancel Order", "standard_ping": "Ping",
    "toggle_sfx": "SFX On/Off", "toggle_music": "Music On/Off", "toggle_ui": "Hide UI",
    "toggle_ui_with_borders": "Hide UI+",
    "rot_u": "Tilt Up", "rot_d": "Tilt Down", "cam_up": "Cam Up", "cam_down": "Cam Down",
    "rot_l": "Rotate Left", "rot_r": "Rotate Right", "step_l": "Left", "step_r": "Right",
    "step_fwd": "Fwd", "step_bck": "Back", "increase_camera_rot": "Rot Speed +",
    "decrease_camera_rot": "Rot Speed -", "show_tactical_map": "Tactical Map",
    **{f"camera_bookmark_save{i}": f"Save Cam {i + 1}" for i in range(4)},
    **{f"camera_bookmark_view{i}": f"Cam {i + 1}" for i in range(4)},
    # campaña
    "show_finance": "Finance", "show_clan": "Faction", "show_overview": "Overview",
    "show_garrison": "Garrison", "show_building_browser": "Buildings",
    "show_recruitment_units": "Recruit", "show_recruitment_agents": "Heroes",
    **{f"button_group_management_{i}": f"Group {i}" for i in range(1, 7)},
    "end_turn": "End Turn", "end_turn_skip_warnings": "End Turn!",
    "end_turn_notification_zoom": "Next Notice", "show_campaign_overlay_options": "Overlays",
    "zoom_to_strategic": "Strategic Map", "toggle_show_cpu_moves": "AI Moves",
    "current_selection_disband": "Disband", "quick_save": "Quick Save", "quick_load": "Quick Load",
    "toggle_labels": "Labels", "auto_merge_units": "Auto Merge", "home_zoom": "Capital",
    "default_camera_rotation": "Reset Cam", "toggle_move_speed": "Move Speed",
    # batalla
    "cycle_next_spawn_zone": "Spawn Zone", "select_all_artillery": "Artillery",
    "select_all_melee": "Infantry", "select_all_cavalry": "Cavalry", "select_all_ranged": "Missile",
    "select_all_idle_units": "All Idle", "select_next_idle_unit": "Next Idle",
    "deselect_all": "Deselect", "general_zoom": "General", "toggle_group": "Group",
    "toggle_locked_group": "Lock Group", "battle_land_melee": "Melee Mode", "battle_land_toggle_run": "Run",
    **{f"battle_land_spell_{i}": f"Spell {i}" for i in range(1, 7)},
    "battle_land_guard_mode": "Guard", "battle_land_withdraw": "Withdraw",
    **{f"battle_land_behaviour_{i}": f"Behaviour {i}" for i in range(1, 4)},
    **{f"battle_land_unit_ability_{i}": f"Ability {i}" for i in range(1, 7)},
    "battle_land_increase_rank": "More Ranks", "battle_land_increase_file": "More Files",
    "battle_land_step_backwards": "Step Back", "battle_land_step_forward": "Step Fwd",
    "battle_both_rotate_left": "Turn Left", "battle_both_rotate_right": "Turn Right",
    "battle_land_strafe_left": "Strafe L", "battle_land_strafe_right": "Strafe R",
    "unit_zoom": "Unit Cam", "battle_land_about_face": "About Face",
    "accel": "Speed +", "decel": "Speed -", "show_allied_units_proxies": "Show Units",
    "visibility_toggle_porthole": "Porthole", "toggle_pause": "Pause",
    "intelli_zoom": "Intelli Zoom", "toggle_tracking": "Track Cam", "context_camera": "Context Cam",
}
# Los grupos de batalla tienen dos teclas: el número solo (seleccionar) y Ctrl+número (asignar)
GROUP_LABELS = {False: "Group {n}", True: "Set Group {n}"}


def game_shortcuts(game_dir):
    root = ET.fromstring((Path(game_dir) / "data" / "text" / "default_keys.xml").read_text(encoding="utf-8", errors="replace"))
    result, skipped = [], []
    for cat in root.find("keyset").findall("category"):
        context = CONTEXTS[cat.get("name")]
        for fn in cat.iter("func"):
            name = fn.get("name")
            if fn.get("hidden") == "1":
                continue
            for k in fn.findall("key"):
                key, mod = (k.text or "").strip(), k.get("modifier")
                if not key:
                    continue
                if key not in KEYS:
                    skipped.append(f"{name}: {key}")
                    continue
                if name.startswith("usegroup"):
                    label = GROUP_LABELS[mod == "CTRL"].format(n=name[-1])
                elif name in LABELS:
                    label = LABELS[name]
                else:
                    skipped.append(f"{name}: sin etiqueta")
                    continue
                result.append((context, label, set() if mod in LOOSE_MODIFIERS else {mod}, key))
    return result, skipped


def main():
    template, output = sys.argv[1], sys.argv[2]
    game_dir = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_GAME
    shortcuts, skipped = game_shortcuts(game_dir)
    build_profile(template, output, APP, EXE, shortcuts, profile_id=PROFILE_ID)
    if skipped:
        print("Descartados:", "; ".join(skipped))


if __name__ == "__main__":
    main()
