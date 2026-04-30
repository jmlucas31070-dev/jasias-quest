#!/usr/bin/env python3
"""
Generate Tiled .world files for every "region" of TMX maps in res/xml/.

A region is the part of a TMX filename before the trailing _x{X}_y{Y} suffix.
For example, "level_0_ados_city_x2_y3.tmx" belongs to region "level_0_ados_city".

For each region with at least one map, this writes
    <region>.world
into the output directory in Tiled's standard JSON format. Each entry contains
the map's filename and its pixel position in the world (X * tile_w * map_w,
Y * tile_h * map_h). All Andor's Trail maps are 32x32 tiles at 32 px each, so
each map takes a 1024x1024 pixel slot.

Maps that don't have an _x_y suffix get placed at (0, 0).

Usage:
    python3 generate_worlds.py \\
        --maps-in  AndorsTrail/res/xml \\
        --out-dir  AndorsTrail/res/xml
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

COORD_RE = re.compile(r"^(?P<region>.+?)_x(?P<x>\d+)_y(?P<y>\d+)$")
DEFAULT_TILE_W = 32
DEFAULT_TILE_H = 32
DEFAULT_MAP_W = 32
DEFAULT_MAP_H = 32


def read_map_dims(tmx_path: Path) -> tuple[int, int, int, int]:
    """Return (width_tiles, height_tiles, tilewidth, tileheight) from a TMX."""
    try:
        tree = ET.parse(tmx_path)
        root = tree.getroot()
        return (
            int(root.get("width", DEFAULT_MAP_W)),
            int(root.get("height", DEFAULT_MAP_H)),
            int(root.get("tilewidth", DEFAULT_TILE_W)),
            int(root.get("tileheight", DEFAULT_TILE_H)),
        )
    except (ET.ParseError, OSError):
        return DEFAULT_MAP_W, DEFAULT_MAP_H, DEFAULT_TILE_W, DEFAULT_TILE_H


def parse_region(name_no_ext: str) -> tuple[str, int, int]:
    """Split a TMX filename (no extension) into (region, x, y)."""
    m = COORD_RE.match(name_no_ext)
    if m:
        return m.group("region"), int(m.group("x")), int(m.group("y"))
    return name_no_ext, 0, 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--maps-in", required=True, type=Path,
                    help="Directory containing the .tmx files.")
    ap.add_argument("--out-dir", required=True, type=Path,
                    help="Directory to write .world files into.")
    ap.add_argument("--prefix", default="",
                    help="Only include maps whose filename starts with this "
                         "prefix (e.g. 'level_' to skip interiors).")
    ap.add_argument("--min-maps", type=int, default=1,
                    help="Skip regions with fewer than this many maps.")
    args = ap.parse_args()

    if not args.maps_in.is_dir():
        print(f"ERROR: --maps-in not a directory: {args.maps_in}", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)

    regions: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    sample_dims: dict[str, tuple[int, int, int, int]] = {}

    for tmx in sorted(args.maps_in.glob("*.tmx")):
        if args.prefix and not tmx.name.startswith(args.prefix):
            continue
        stem = tmx.stem
        region, x, y = parse_region(stem)
        regions[region].append((tmx.name, x, y))
        if region not in sample_dims:
            sample_dims[region] = read_map_dims(tmx)

    written = 0
    for region, entries in sorted(regions.items()):
        if len(entries) < args.min_maps:
            continue
        w_tiles, h_tiles, tw, th = sample_dims[region]
        pw, ph = w_tiles * tw, h_tiles * th
        maps = [
            {
                "fileName": fname,
                "x": x * pw,
                "y": y * ph,
                "width": pw,
                "height": ph,
            }
            for fname, x, y in sorted(entries, key=lambda t: (t[2], t[1], t[0]))
        ]
        world = {"type": "world", "onlyShowAdjacentMaps": False, "maps": maps}
        out = args.out_dir / f"{region}.world"
        out.write_text(json.dumps(world, indent=2) + "\n", encoding="utf-8")
        written += 1

    print(f"Wrote {written} .world files into {args.out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
