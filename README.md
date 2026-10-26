# flux_game_profiles

Shortcut profiles for the [Flux keyboard](https://fluxkeyboard.com) (Polymath), one folder per game or app. Each profile labels the keys with that program's shortcuts and switches automatically when the program is in the foreground.

| Folder | Program | Executable | Shortcuts | Status |
|---|---|---|---|---|
| [`total-war-warhammer-3`](total-war-warhammer-3) | Total War: Warhammer III | `Warhammer3.exe` | 125 (Universal, Campaign, Battle) | Tested |
| [`brave`](brave) | Brave browser (Chromium shortcuts) | `brave.exe` | 64 | Not tested yet |

## Install a profile

1. Polymath → **SHORTCUTS** → **Create New** → **Import** → choose the `.flux` file.
2. Click **Save to Keyboard**. Required: the keyboard itself switches profiles when it sees the program, so it needs the new profile stored.
3. Open the program. Shortcuts with Ctrl/Alt/Shift show up while you hold that modifier.

Tested with Polymath 1.4.5.7 and an ISO Spanish layout. Keys are physical US positions.

## Make your own

`tools/fluxfile.py` builds a `.flux` from a list of `(context, label, modifiers, key)` and a `.flux` exported from Polymath used as template (theme, actuation and keymap are copied from it). See `brave/make_profile.py` for the simplest example:

```
python brave/make_profile.py <template.flux> <output.flux>
```

The Warhammer III script reads the default keys straight from the game (`data/text/default_keys.xml`).

## License

[MIT](LICENSE).
