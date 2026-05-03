# Tileset Cleanup — jasias-quest

## Overview

`cleanup_tilesets.py` scans every `level_0*.tmx` map and every template map in
`AndorsTrail/res/xml/`, collects the union of all tileset PNG files they
reference, then moves any PNG in `AndorsTrail/res/drawable/` that is **not**
referenced by either group into a new `AndorsTrail/res/unused_tileset/`
directory.

---

## How to run

```
cd path/to/jasias-quest/scripts
python3 cleanup_tilesets.py
```

### Options

| Flag | Effect |
|------|--------|
| *(none)* | Scan, compute, and move unused PNGs |
| `--dry-run` | Show what would be moved; move nothing |
| `--verbose` | Print every tileset name found while scanning |

---

## What the script scans

| Group | Pattern matched |
|-------|----------------|
| Level-0 maps | `level_0*.tmx` |
| Template maps | `template*.tmx`, `jq*template*.tmx`, `jqa_template*.tmx`, `jq_bank_template.tmx` |

At the time of analysis the repo contained **2,004 level-0 maps** and
**32 template maps**.

---

## Expected results (from pre-run analysis)

The numbers below were computed by sampling ~200 of the 2,004 level-0 maps
and all 32 template maps. Running the script locally will produce the exact
counts because it reads **every** map.

| Metric | Count |
|--------|-------|
| PNG files in `res/drawable/` | 1,516 |
| Unique tilesets used by level-0 maps (sample) | ~569 |
| Unique tilesets used by template maps | 62 |
| **Estimated files to move** | **~700–900** |

After the script runs it writes `AndorsTrail/res/unused_tileset/moved_files.txt`
with the exact list of everything it moved.

---

## Category breakdown of files expected to move

Based on pre-run analysis the unused files break down roughly as follows.
Note that many of these are **not** map tilesets at all — they are UI assets,
sprite sheets, item icons, and other engine resources that live in `drawable/`
but are never referenced from a `.tmx` tileset element.

| Category prefix | ~Count | Notes |
|-----------------|--------|-------|
| `furniture_*` | 157 | Interior furniture variants not placed in any scanned map |
| `item_*` / `items_*` | 165 | Item icons and sprite sheets |
| `building_*` | 109 | Building variants / entrance styles not yet in use |
| `ui_*` | 125 | UI chrome — buttons, frames, spinners (never map tilesets) |
| `monsters_*` | 65 | Monster sprite sheets (game engine assets, not map tiles) |
| `logic_*` | 50 | Logic/collision tiles not placed in scanned maps |
| `ground_*` | 66 | Ground texture variants |
| `plant_*` | 31 | Plant / foliage variants |
| `light_*` | 4 | Lighting overlay tiles |
| `sky_*` / `ts_sky_*` | 13 | Sky texture strips |
| `terrain_*` | 15 | Cave/outdoor terrain tiles |
| `char_*` / `character_*` | 9 | Hero / character sprite sheets |
| `effect_*` | 8 | Combat visual effects |
| `equip_*` | 9 | Equipment slot icons |
| `loading_anim_*` | 7 | Loading screen animation frames |
| `logo_anim_*` | 10 | Logo / splash animation frames |
| `actorconditions_*` | 6 | Status-condition icon strips |
| `object_*` | 10 | Miscellaneous map objects |
| Other | ~10 | `andors_trail_logo`, `placehold_tile`, `plain_colors`, `walkable_sentinel`, etc. |

---

## Reversing the operation

All moved files land in `AndorsTrail/res/unused_tileset/`. To restore them:

```bash
# from the repo root
mv AndorsTrail/res/unused_tileset/*.png AndorsTrail/res/drawable/
```

`moved_files.txt` inside that directory lists every file that was moved.

---

## Notes

* The script never deletes anything — it only moves files.
* If `unused_tileset/` already exists the script will add to it (it will not
  overwrite files that are already there).
* Re-running on an already-cleaned repo is safe; there will simply be fewer
  PNGs left in `drawable/` and the script will report fewer moves.
* Files referenced via the `source` attribute of an external `.tsx` tileset
  (rather than an embedded `<tileset name="…">` element) are **not** currently
  tracked. If your project uses external `.tsx` files, review the output before
  committing.
