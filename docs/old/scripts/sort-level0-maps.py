#!/usr/bin/env python3
"""
sort-level0-maps.py

Scans AndorsTrail/res/xml/ for level_0_*.tmx files and moves any that do NOT
correspond to a main Stendhal overworld zone into an "unused/" subdirectory.

Usage (run from the scripts/ directory or anywhere):
    python3 sort-level0-maps.py [path/to/AndorsTrail/res/xml] [--dry-run]

If no path argument is given it defaults to:
    <repo root>/AndorsTrail/res/xml
    (two levels up from this script's location)

Pass --dry-run to preview what would move without touching files.

Source of truth: https://github.com/arianne/stendhal/tree/master/data/maps/Level%200
Cross-referenced May 2026.
"""

import os
import re
import sys
import shutil
import argparse
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Complete set of Stendhal Level-0 MAIN OVERWORLD zones.
# Key = "<region>_<zone>" matching the prefix of each tmx file after "level_0_".
# Zones excluded from this set (memory, northpole, seasonal, placeholder, raid)
# will be moved to unused/.
# ---------------------------------------------------------------------------
OVERWORLD_ZONES = {
    # ados
    "ados_city",
    "ados_city_n",
    "ados_city_n2",
    "ados_city_s",
    "ados_coast_s",
    "ados_coast_s_w2",
    "ados_coast_se",
    "ados_coast_sw",
    "ados_forest_w2",
    "ados_mountain_n2",
    "ados_mountain_n2_w",
    "ados_mountain_n2_w2",
    "ados_mountain_n_w2",
    "ados_mountain_nw",
    "ados_ocean_e",
    "ados_outside_nw",
    "ados_outside_w",
    "ados_river_s2_w2",
    "ados_rock",
    "ados_rock_w",
    "ados_swamp",
    "ados_wall",
    "ados_wall_n",
    "ados_wall_n2",
    "ados_wall_s",

    # amazon
    "amazon_island_ne",
    "amazon_island_nw",
    "amazon_island_se",
    "amazon_island_sw",

    # athor (island + ship — all accessible overworld zones in Stendhal)
    "athor_island",
    "athor_island_e",
    "athor_island_w",
    "athor_ship_w2",

    # deniran
    "deniran_city",
    "deniran_city_e",
    "deniran_city_e2",
    "deniran_city_s",
    "deniran_city_s_e2",
    "deniran_city_se",
    "deniran_city_sw",
    "deniran_city_w",
    "deniran_forest_n",
    "deniran_forest_n2",
    "deniran_forest_n2_e",
    "deniran_forest_n2_e2",
    "deniran_forest_n2_w",
    "deniran_forest_n_e2",
    "deniran_forest_ne",
    "deniran_forest_nw",
    "deniran_river_s",
    "deniran_river_s_e2",
    "deniran_river_se",
    "deniran_river_sw",

    # fado — city and forests only; city_easter and raid_main are NOT overworld
    "fado_city",
    "fado_forest",
    "fado_forest_e",
    "fado_forest_s",
    "fado_forest_s_e2",
    "fado_forest_s_e3",
    "fado_forest_se",

    # kalavan
    "kalavan_castle",
    "kalavan_castle_w",
    "kalavan_city",
    "kalavan_city_gardens",
    "kalavan_forest",
    "kalavan_forest_e",
    "kalavan_forest_e2",

    # kirdneh
    "kirdneh_city",
    "kirdneh_river_w",

    # nalwor
    "nalwor_city",
    "nalwor_forest_e",
    "nalwor_forest_e2",
    "nalwor_forest_n",
    "nalwor_forest_n_e2",
    "nalwor_forest_ne",
    "nalwor_forest_nw",
    "nalwor_forest_w",
    "nalwor_river_s",
    "nalwor_river_s_e2",
    "nalwor_river_se",
    "nalwor_river_sw",

    # orril
    "orril_castle",
    "orril_forest_e",
    "orril_forest_n",
    "orril_mountain_n2_w2",
    "orril_mountain_n_w2",
    "orril_mountain_nw",
    "orril_mountain_w",
    "orril_mountain_w2",
    "orril_river_s",
    "orril_river_s_w2",
    "orril_river_se",
    "orril_river_sw",

    # semos — permanent zones only; _easter / _halloween / _xmas are NOT overworld
    "semos_canyon",
    "semos_city",
    "semos_forest_s",
    "semos_mountain_n2",
    "semos_mountain_n2_e",
    "semos_mountain_n2_e2",
    "semos_mountain_n2_mine_town_weeks",
    "semos_mountain_n2_mine_town_weeks_construction",
    "semos_mountain_n2_w",
    "semos_mountain_n2_w2",
    "semos_mountain_n2_w3",
    "semos_mountain_n_e2",
    "semos_mountain_n_w2",
    "semos_mountain_n_w3",
    "semos_mountain_n_w4",
    "semos_mountain_w2",
    "semos_plains_n",
    "semos_plains_n_e2",
    "semos_plains_ne",
    "semos_plains_s",
    "semos_plains_w",
    "semos_road_e",
    "semos_road_se",
    "semos_village_w",

    # sikhw — real city/desert zones only; sikhw_placeholder is NOT overworld
    "sikhw_city",
    "sikhw_desert_e",
    "sikhw_desert_n",
    "sikhw_desert_n_w2",
    "sikhw_desert_ne",
    "sikhw_desert_nw",
    "sikhw_desert_s",
    "sikhw_desert_s2",
    "sikhw_desert_s2_e",
    "sikhw_desert_s2_w",
    "sikhw_desert_s2_w2",
    "sikhw_desert_s_w2",
    "sikhw_desert_se",
    "sikhw_desert_sw",
    "sikhw_desert_w",
    "sikhw_desert_w2",
}

# Zones intentionally excluded (kept here as documentation):
#   memory_large_1, memory_large_2, memory_small_many_1..6
#   northpole_northpole_island
#   fado_city_easter, fado_raid_main
#   semos_city_easter, semos_city_halloween, semos_city_xmas, semos_village_w_xmas
#   sikhw_placeholder


def extract_zone_key(filename: str) -> str | None:
    """Strip level_0_ prefix and trailing _xN_yN.tmx to get the zone key."""
    base = filename.lower()
    if not base.startswith("level_0_") or not base.endswith(".tmx"):
        return None
    inner = filename[len("level_0_"):-len(".tmx")]
    stripped = re.sub(r"_x\d+_y\d+$", "", inner)
    return stripped if stripped else None


def classify_non_overworld(zone_key: str) -> str | None:
    """Return a human-readable reason if the zone is not main overworld, else None."""
    if zone_key.startswith("memory_"):
        return "memory/dream map"
    if zone_key.startswith("northpole_"):
        return "northpole seasonal island"
    if "_easter" in zone_key:
        return "seasonal Easter variant"
    if "_halloween" in zone_key:
        return "seasonal Halloween variant"
    if "_xmas" in zone_key:
        return "seasonal Christmas variant"
    if zone_key.startswith("fado_raid_"):
        return "fado raid event map"
    if zone_key.startswith("sikhw_placeholder"):
        return "sikhw placeholder (unimplemented)"
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Move non-overworld level_0_*.tmx maps to an unused/ subdirectory."
    )
    parser.add_argument(
        "xml_dir",
        nargs="?",
        help="Path to AndorsTrail/res/xml (default: ../../AndorsTrail/res/xml relative to this script)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be moved without touching any files.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    if args.xml_dir:
        xml_dir = Path(args.xml_dir).resolve()
    else:
        xml_dir = (script_dir / ".." / "AndorsTrail" / "res" / "xml").resolve()

    unused_dir = xml_dir / "unused"

    print("=" * 70)
    print("  Stendhal Overworld Level-0 Map Sorter")
    print("=" * 70)
    print(f"  XML directory : {xml_dir}")
    print(f"  Unused target : {unused_dir}")
    print(f"  Mode          : {'DRY RUN (no files will move)' if args.dry_run else 'LIVE'}")
    print("=" * 70)
    print()

    if not xml_dir.is_dir():
        print(f"ERROR: Directory not found: {xml_dir}", file=sys.stderr)
        print(file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print("  python3 sort-level0-maps.py [path/to/AndorsTrail/res/xml] [--dry-run]", file=sys.stderr)
        sys.exit(1)

    all_files = sorted(
        f for f in os.listdir(xml_dir)
        if f.lower().startswith("level_0_") and f.lower().endswith(".tmx")
    )

    if not all_files:
        print("No level_0_*.tmx files found in the directory. Nothing to do.")
        sys.exit(0)

    print(f"Found {len(all_files)} level_0_*.tmx file(s) to evaluate.\n")

    to_move: list[tuple[str, str, str]] = []   # (filename, zone_key, reason)
    to_keep: list[tuple[str, str]] = []         # (filename, zone_key)
    unrecognised: list[str] = []

    for filename in all_files:
        zone_key = extract_zone_key(filename)

        if zone_key is None:
            unrecognised.append(filename)
            continue

        if zone_key in OVERWORLD_ZONES:
            to_keep.append((filename, zone_key))
            continue

        reason = classify_non_overworld(zone_key) or "not found in Stendhal overworld zone list"
        to_move.append((filename, zone_key, reason))

    print(f"  KEEP  {len(to_keep):>5} file(s) — match the Stendhal main overworld")
    print(f"  MOVE  {len(to_move):>5} file(s) — will go to unused/")
    if unrecognised:
        print(f"  SKIP  {len(unrecognised):>5} file(s) — could not be parsed (left in place)")
    print()

    if to_move:
        # Group by reason for readability
        groups: dict[str, list[str]] = defaultdict(list)
        for filename, _, reason in to_move:
            groups[reason].append(filename)

        for reason, files in sorted(groups.items()):
            print(f"  [{reason}]  ({len(files)} files)")
            for f in files[:5]:
                print(f"    {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
            print()

    if unrecognised:
        print("  Unrecognised files (skipped):")
        for f in unrecognised:
            print(f"    {f}")
        print()

    if not to_move:
        print("Nothing to move. All level_0 maps already match the overworld.")
        sys.exit(0)

    if args.dry_run:
        print("=" * 70)
        print("  DRY RUN complete — no files were moved.")
        print("  Remove --dry-run to perform the actual move.")
        print("=" * 70)
        sys.exit(0)

    # Create unused/ directory if it doesn't exist
    unused_dir.mkdir(parents=True, exist_ok=True)
    print(f"Target directory: {unused_dir}\n")

    moved = 0
    skipped = 0

    for filename, _, _ in to_move:
        src = xml_dir / filename
        dst = unused_dir / filename

        if dst.exists():
            print(f"  SKIP (already in unused/): {filename}")
            skipped += 1
            continue

        shutil.move(str(src), str(dst))
        moved += 1

    print("=" * 70)
    print("  Done.")
    print(f"  Moved  : {moved} file(s)  →  {unused_dir}")
    if skipped:
        print(f"  Skipped: {skipped} file(s) (already present in unused/)")
    print(f"  Kept   : {len(to_keep)} file(s) (main Stendhal overworld)")
    print("=" * 70)


if __name__ == "__main__":
    main()
