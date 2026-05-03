#!/usr/bin/env python3
"""
generate_nodes.py
=================

Injects forage and mining spawn areas into Andor's Trail / jasias-quest TMX maps.

Read a JSON config of the form:

    {
      "level_1_ados_caves_x0_y0": [
        {"x": 6,  "y": 8,  "tier": "mine_low"},
        {"x": 12, "y": 14, "tier": "mine_mid"},
        {"x": 22, "y": 22, "tier": "mine_gem"}
      ],
      "level_1_crossglen_outside_x0_y0": [
        {"x": 5,  "y": 7,  "tier": "forage_common"},
        {"x": 18, "y": 11, "tier": "forage_berry"}
      ]
    }

x and y are tile coordinates (0..31 by default for 32x32 maps).
Tiers map to spawngroup names defined in the monsterlist_*.json content packs.

Usage:
    python3 generate_nodes.py \\
        --config nodes_config.json \\
        --maps-in  /path/to/AndorsTrail/res/xml \\
        --maps-out /path/to/output/res/xml
"""

import argparse
import json
import os
import re
import sys

TIER_TO_SPAWNGROUP = {
    "forage_common": "fm_node_forage_common",
    "forage_berry":  "fm_node_forage_berry",
    "forage_nut":    "fm_node_forage_nut",
    "mine_low":      "fm_node_mine_low",
    "mine_mid":      "fm_node_mine_mid",
    "mine_high":     "fm_node_mine_high",
    "mine_gem":      "fm_node_mine_gem",
}

TILE_PX = 32  # Andor's Trail uses 32x32 tile pixels.

# Regex matches both <objectgroup name="Spawn" .../> (self-closing)
# and <objectgroup name="Spawn" ...> ... </objectgroup> (open form).
SPAWN_GROUP_RE = re.compile(
    r'(<objectgroup\b[^>]*\bname="Spawn"[^>]*?)'
    r'(\s*/>|>(.*?)</objectgroup>)',
    re.DOTALL,
)


def build_object_xml(node_idx: int, tier: str, x_tile: int, y_tile: int) -> str:
    """Render a single spawn <object> XML block for a node."""
    spawngroup = TIER_TO_SPAWNGROUP[tier]
    name = f"fm_node_{tier}_{node_idx}"
    px = x_tile * TILE_PX
    py = y_tile * TILE_PX
    return (
        f'  <object name="{name}" type="spawn" '
        f'x="{px}" y="{py}" width="{TILE_PX}" height="{TILE_PX}">\n'
        f'   <properties>\n'
        f'    <property name="spawngroup" value="{spawngroup}"/>\n'
        f'    <property name="quantity" value="1"/>\n'
        f'   </properties>\n'
        f'  </object>\n'
    )


def inject_into_tmx(tmx_text: str, nodes: list) -> str:
    """Return modified TMX text with the given nodes added to its Spawn group."""
    if not nodes:
        return tmx_text

    objects_xml = "".join(
        build_object_xml(i + 1, n["tier"], n["x"], n["y"])
        for i, n in enumerate(nodes)
    )

    def replace(match: "re.Match") -> str:
        head = match.group(1)        # opening <objectgroup ...
        suffix = match.group(2)      # either "/>" or ">...children...</objectgroup>"
        existing_children = match.group(3) or ""
        return (
            f'{head}>\n'
            f'{existing_children}'
            f'{objects_xml}'
            f' </objectgroup>'
        )

    new_text, n_subs = SPAWN_GROUP_RE.subn(replace, tmx_text, count=1)
    if n_subs == 0:
        raise RuntimeError(
            "No <objectgroup name=\"Spawn\"> element found. "
            "Add an empty <objectgroup name=\"Spawn\" .../> to the TMX first."
        )
    return new_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",    required=True, help="Path to nodes_config.json.")
    parser.add_argument("--maps-in",   required=True, help="Input res/xml directory.")
    parser.add_argument("--maps-out",  required=True, help="Output res/xml directory.")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as fh:
        config = json.load(fh)

    os.makedirs(args.maps_out, exist_ok=True)

    n_written = 0
    n_skipped = 0
    for map_id, nodes in config.items():
        src = os.path.join(args.maps_in, f"{map_id}.tmx")
        dst = os.path.join(args.maps_out, f"{map_id}.tmx")
        if not os.path.isfile(src):
            print(f"  SKIP {map_id}: source TMX not found at {src}", file=sys.stderr)
            n_skipped += 1
            continue

        # Validate tiers up front.
        for n in nodes:
            if n["tier"] not in TIER_TO_SPAWNGROUP:
                raise SystemExit(
                    f"Unknown tier '{n['tier']}' in map '{map_id}'. "
                    f"Known: {sorted(TIER_TO_SPAWNGROUP)}"
                )

        with open(src, "r", encoding="utf-8") as fh:
            tmx = fh.read()
        new_tmx = inject_into_tmx(tmx, nodes)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(new_tmx)
        n_written += 1
        print(f"  WROTE {map_id}.tmx  ({len(nodes)} nodes)")

    print(f"\nDone. {n_written} maps written, {n_skipped} skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
