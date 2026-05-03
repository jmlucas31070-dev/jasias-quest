#!/usr/bin/env python3
"""
generate-world-file.py

Generates a Tiled Editor .world file for the Andor's Trail / jasias-quest
overworld (level 0) maps, using canonical Stendhal zone coordinates as the
positional source of truth.

Coordinate source: https://github.com/arianne/stendhal/tree/master/data/conf/zones
Cross-referenced May 2026.

How it works
------------
Stendhal stores each zone's top-left position in tile units (1 tile = 32 px).
Adjacent zones are separated by either 64 or 128 tiles.  In jasias-quest every
zone is split into a grid of 32×32-tile chunks named
    level_0_<zone>_x<cx>_y<cy>.tmx
so a 128-tile zone has a 4×4 grid and a 64-tile zone has a 2×2 grid — every
chunk is always 1024×1024 px (32 tiles × 32 px/tile).

Usage
-----
    # scan a live repo and produce the world file next to the .tmx files
    python3 generate-world-file.py [path/to/AndorsTrail/res/xml] [--dry-run]

    # generate from the built-in zone database only (no local files needed)
    python3 generate-world-file.py --from-database [output.world]

If no path is given the script defaults to ../../AndorsTrail/res/xml relative
to itself, which is correct when run from the jasias-quest scripts/ directory.
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Stendhal zone coordinate database  (zone_name → (tile_x, tile_y))
# Source: data/conf/zones/*.xml from arianne/stendhal on GitHub
# ---------------------------------------------------------------------------
ZONE_COORDS: dict[str, tuple[int, int]] = {
    # ados
    "ados_city":           (500896, 500000),
    "ados_city_n":         (500896, 499872),
    "ados_city_n2":        (500896, 499744),
    "ados_city_s":         (500896, 500128),
    "ados_coast_s":        (500896, 500256),
    "ados_coast_s_w2":     (500640, 500256),
    "ados_coast_sw":       (500768, 500256),
    "ados_forest_w2":      (500256, 500000),
    "ados_mountain_n2":    (500640, 499744),
    "ados_mountain_n2_w":  (500512, 499744),
    "ados_mountain_n2_w2": (500384, 499744),
    "ados_mountain_n_w2":  (500384, 499872),
    "ados_mountain_nw":    (500512, 499872),
    "ados_ocean_e":        (501024, 500000),
    "ados_outside_nw":     (500640, 499872),
    "ados_outside_w":      (500640, 500000),
    "ados_river_s2_w2":    (500640, 500384),
    "ados_rock":           (500512, 500000),
    "ados_rock_w":         (500384, 500000),
    "ados_swamp":          (500640, 500128),
    "ados_wall":           (500768, 500000),
    "ados_wall_n":         (500768, 499872),
    "ados_wall_n2":        (500768, 499744),
    "ados_wall_s":         (500768, 500128),

    # amazon
    "amazon_island_ne": (501152, 499744),
    "amazon_island_nw": (501024, 499744),
    "amazon_island_se": (501152, 499872),
    "amazon_island_sw": (501024, 499872),

    # athor
    "athor_island":   (501024, 500384),
    "athor_island_e": (501152, 500384),
    "athor_island_w": (500896, 500384),
    "athor_ship_w2":  (500768, 500384),

    # deniran
    "deniran_city":       (499232, 500000),
    "deniran_city_e":     (499360, 500000),
    "deniran_city_e2":    (499488, 500000),
    "deniran_city_s":     (499232, 500128),
    "deniran_city_s_e2":  (499488, 500128),
    "deniran_city_se":    (499360, 500128),
    "deniran_city_sw":    (499104, 500128),
    "deniran_city_w":     (499104, 500000),
    "deniran_forest_n":   (499232, 499872),
    "deniran_forest_n2":  (499232, 499744),
    "deniran_forest_n2_e":  (499360, 499744),
    "deniran_forest_n2_e2": (499488, 499744),
    "deniran_forest_n2_w":  (499104, 499744),
    "deniran_forest_n_e2":  (499488, 499872),
    "deniran_forest_ne":    (499360, 499872),
    "deniran_forest_nw":    (499104, 499872),
    "deniran_river_s":      (499232, 500256),
    "deniran_river_s_e2":   (499488, 500256),
    "deniran_river_se":     (499360, 500256),
    "deniran_river_sw":     (499104, 500256),

    # fado  (city_easter and raid_main excluded — non-overworld)
    "fado_city":       (499616, 500512),
    "fado_forest":     (499744, 500512),
    "fado_forest_e":   (499872, 500512),
    "fado_forest_s":   (499744, 500640),
    "fado_forest_s_e2":(500000, 500640),
    "fado_forest_s_e3":(500128, 500640),
    "fado_forest_se":  (499872, 500640),

    # kalavan
    "kalavan_castle":       (499616, 500640),
    "kalavan_castle_w":     (499552, 500640),
    "kalavan_city":         (499616, 500768),
    "kalavan_city_gardens": (499744, 500768),
    "kalavan_forest":       (499872, 500768),
    "kalavan_forest_e":     (500000, 500768),
    "kalavan_forest_e2":    (500128, 500768),

    # kirdneh
    "kirdneh_city":    (500000, 500512),
    "kirdneh_river_w": (500128, 500512),

    # nalwor
    "nalwor_city":       (500256, 500256),
    "nalwor_forest_e":   (500384, 500256),
    "nalwor_forest_e2":  (500512, 500256),
    "nalwor_forest_n":   (500256, 500128),
    "nalwor_forest_n_e2":(500512, 500128),
    "nalwor_forest_ne":  (500384, 500128),
    "nalwor_forest_nw":  (500128, 500128),
    "nalwor_forest_w":   (500128, 500256),
    "nalwor_river_s":    (500256, 500384),
    "nalwor_river_s_e2": (500512, 500384),
    "nalwor_river_se":   (500384, 500384),
    "nalwor_river_sw":   (500128, 500384),

    # orril
    "orril_castle":          (499872, 500256),
    "orril_forest_e":        (500000, 500256),
    "orril_forest_n":        (499872, 500128),
    "orril_mountain_n2_w2":  (499616, 500000),
    "orril_mountain_n_w2":   (499616, 500128),
    "orril_mountain_nw":     (499744, 500128),
    "orril_mountain_w":      (499744, 500256),
    "orril_mountain_w2":     (499616, 500256),
    "orril_river_s":         (499872, 500384),
    "orril_river_s_w2":      (499616, 500384),
    "orril_river_se":        (500000, 500384),
    "orril_river_sw":        (499744, 500384),

    # semos  (_easter / _halloween / _xmas excluded — non-overworld)
    "semos_canyon":          (500320, 499680),
    "semos_city":            (500064, 500000),
    "semos_forest_s":        (500000, 500128),
    "semos_mountain_n2":     (500000, 499744),
    "semos_mountain_n2_e":   (500128, 499744),
    "semos_mountain_n2_e2":  (500256, 499744),
    "semos_mountain_n2_mine_town_weeks":              (500000, 499616),
    "semos_mountain_n2_mine_town_weeks_construction": (500000, 499488),
    "semos_mountain_n2_w":   (499872, 499744),
    "semos_mountain_n2_w2":  (499744, 499744),
    "semos_mountain_n2_w3":  (499616, 499872),
    "semos_mountain_n_e2":   (500256, 499872),
    "semos_mountain_n_w2":   (499872, 499872),
    "semos_mountain_n_w3":   (499744, 499872),
    "semos_mountain_n_w4":   (499616, 499744),
    "semos_mountain_w2":     (499744, 500000),
    "semos_plains_n":        (500000, 499872),
    "semos_plains_n_e2":     (500192, 499872),
    "semos_plains_ne":       (500128, 499872),
    "semos_plains_s":        (500000, 500064),
    "semos_plains_w":        (499872, 500000),
    "semos_road_e":          (500128, 500000),
    "semos_road_se":         (500128, 500064),
    "semos_village_w":       (500000, 500000),

    # sikhw  (sikhw_placeholder excluded — non-overworld)
    "sikhw_city":        (499360, 500512),
    "sikhw_desert_e":    (499488, 500512),
    "sikhw_desert_n":    (499360, 500384),
    "sikhw_desert_n_w2": (499104, 500384),
    "sikhw_desert_ne":   (499488, 500384),
    "sikhw_desert_nw":   (499232, 500384),
    "sikhw_desert_s":    (499360, 500640),
    "sikhw_desert_s2":   (499360, 500768),
    "sikhw_desert_s2_e": (499488, 500768),
    "sikhw_desert_s2_w": (499232, 500768),
    "sikhw_desert_s2_w2":(499104, 500768),
    "sikhw_desert_s_w2": (499104, 500640),
    "sikhw_desert_se":   (499488, 500640),
    "sikhw_desert_sw":   (499232, 500640),
    "sikhw_desert_w":    (499232, 500512),
    "sikhw_desert_w2":   (499104, 500512),
}

TILE_PX   = 32    # pixels per tile (Stendhal / Andor's Trail standard)
CHUNK_TILES = 32  # every chunk is 32×32 tiles
CHUNK_PX  = CHUNK_TILES * TILE_PX   # 1024 px per chunk side


def extract_zone_and_chunk(filename: str) -> tuple[str, int, int] | None:
    """
    Parse 'level_0_<zone>_x<cx>_y<cy>.tmx' into (zone, cx, cy).
    Returns None if the filename doesn't match.
    """
    base = filename
    if base.lower().endswith(".tmx"):
        base = base[:-4]
    m = re.match(r"level_0_(.+)_x(\d+)_y(\d+)$", base)
    if not m:
        return None
    return m.group(1), int(m.group(2)), int(m.group(3))


def derive_zone_extent(zone: str) -> tuple[int, int]:
    """
    Derive the zone's tile extent (width, height) from the spacing between
    zones in the database.  Falls back to 128×128 tiles (4×4 chunks) when
    no neighbour can be found in that direction.
    """
    tx, ty = ZONE_COORDS[zone]

    # Collect all tile-x values in the same tile-y row (±1 tile tolerance)
    xs_in_row = sorted(
        v[0] for k, v in ZONE_COORDS.items() if v[1] == ty and v[0] > tx
    )
    # Collect all tile-y values in the same tile-x column
    ys_in_col = sorted(
        v[1] for k, v in ZONE_COORDS.items() if v[0] == tx and v[1] > ty
    )

    width  = (xs_in_row[0] - tx) if xs_in_row  else 128
    height = (ys_in_col[0] - ty) if ys_in_col  else 128

    # Clamp to sensible multiple of CHUNK_TILES
    width  = max(CHUNK_TILES, (width  // CHUNK_TILES) * CHUNK_TILES)
    height = max(CHUNK_TILES, (height // CHUNK_TILES) * CHUNK_TILES)

    return width, height


def zone_chunk_grid(zone: str) -> tuple[int, int]:
    """Return (max_cx+1, max_cy+1) i.e. number of chunks in each direction."""
    w, h = derive_zone_extent(zone)
    return w // CHUNK_TILES, h // CHUNK_TILES


def build_entries_from_database() -> list[dict]:
    """
    Build all world-file entries directly from ZONE_COORDS without needing
    any local .tmx files.  Uses the derived chunk grid for each zone.
    """
    min_tx = min(v[0] for v in ZONE_COORDS.values())
    min_ty = min(v[1] for v in ZONE_COORDS.values())

    entries = []
    for zone in sorted(ZONE_COORDS):
        tx, ty = ZONE_COORDS[zone]
        nx, ny = zone_chunk_grid(zone)
        base_px_x = (tx - min_tx) * TILE_PX
        base_px_y = (ty - min_ty) * TILE_PX
        for cy in range(ny):
            for cx in range(nx):
                fname = f"level_0_{zone}_x{cx}_y{cy}.tmx"
                entries.append({
                    "fileName":  fname,
                    "x":  base_px_x + cx * CHUNK_PX,
                    "y":  base_px_y + cy * CHUNK_PX,
                    "width":  CHUNK_PX,
                    "height": CHUNK_PX,
                })
    return entries


def build_entries_from_directory(xml_dir: Path) -> list[dict]:
    """
    Build world-file entries for every level_0_*.tmx file found in xml_dir,
    skipping files whose zone is not in ZONE_COORDS (i.e. non-overworld zones).
    """
    min_tx = min(v[0] for v in ZONE_COORDS.values())
    min_ty = min(v[1] for v in ZONE_COORDS.values())

    entries = []
    skipped = []

    tmx_files = sorted(
        f for f in os.listdir(xml_dir)
        if f.lower().startswith("level_0_") and f.lower().endswith(".tmx")
        and not (xml_dir / "unused" / f).exists()   # ignore if already moved
    )

    for fname in tmx_files:
        parsed = extract_zone_and_chunk(fname)
        if not parsed:
            skipped.append(fname)
            continue
        zone, cx, cy = parsed
        if zone not in ZONE_COORDS:
            skipped.append(fname)
            continue

        tx, ty = ZONE_COORDS[zone]
        base_px_x = (tx - min_tx) * TILE_PX
        base_px_y = (ty - min_ty) * TILE_PX
        entries.append({
            "fileName":  fname,
            "x":  base_px_x + cx * CHUNK_PX,
            "y":  base_px_y + cy * CHUNK_PX,
            "width":  CHUNK_PX,
            "height": CHUNK_PX,
        })

    if skipped:
        print(f"  Skipped {len(skipped)} file(s) — non-overworld or unrecognised zone")

    return entries


def write_world_file(entries: list[dict], output_path: Path, dry_run: bool) -> None:
    world = {
        "type": "world",
        "onlyShowAdjacentMaps": False,
        "maps": entries,
    }
    content = json.dumps(world, indent=2)

    print(f"\n  World file : {output_path}")
    print(f"  Map entries: {len(entries)}")

    if dry_run:
        print("\n  DRY RUN — file not written.")
        print("  First 3 entries preview:")
        for e in entries[:3]:
            print(f"    {e}")
        return

    output_path.write_text(content, encoding="utf-8")
    print("  Written successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Tiled .world file for the Andor's Trail / jasias-quest overworld."
    )
    parser.add_argument(
        "xml_dir",
        nargs="?",
        help="Path to AndorsTrail/res/xml (default: ../../AndorsTrail/res/xml)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output .world file path (default: <xml_dir>/level_0_overworld.world or ./level_0_overworld.world)",
    )
    parser.add_argument(
        "--from-database",
        action="store_true",
        help="Generate entries purely from the built-in zone database; no local files needed.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview output without writing any files.",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  Tiled World File Generator — Andor's Trail Overworld")
    print("=" * 70)

    if args.from_database:
        print("  Mode: database-only (no local .tmx files required)")
        out_path = Path(args.output) if args.output else Path("level_0_overworld.world")
        entries = build_entries_from_database()
    else:
        script_dir = Path(__file__).resolve().parent
        xml_dir = Path(args.xml_dir).resolve() if args.xml_dir else \
                  (script_dir / ".." / "AndorsTrail" / "res" / "xml").resolve()

        if not xml_dir.is_dir():
            print(f"\n  ERROR: Directory not found: {xml_dir}", file=sys.stderr)
            print("  Usage:", file=sys.stderr)
            print("    python3 generate-world-file.py [path/to/AndorsTrail/res/xml]", file=sys.stderr)
            print("    python3 generate-world-file.py --from-database [output.world]", file=sys.stderr)
            sys.exit(1)

        print(f"  Mode      : directory scan")
        print(f"  XML dir   : {xml_dir}")
        entries = build_entries_from_directory(xml_dir)
        out_path = xml_dir / "level_0_overworld.world" if not args.output else Path(args.output)

    write_world_file(entries, out_path, args.dry_run)
    print("=" * 70)


if __name__ == "__main__":
    main()
