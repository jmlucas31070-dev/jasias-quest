#!/usr/bin/env python3
"""
stendhal_to_andorstrail_v2.py
=============================
Converts Stendhal overworld (level 0) maps into Andor's Trail-compatible
30×30-tile TMX maps, named after the Stendhal zone they originate from.

Naming convention  (per-zone chunking):
  {zone_name}_x{cx}_y{cy}.tmx
  e.g.  0_deniran_forest_n2_w_x0_y0.tmx
        0_deniran_forest_n2_w_x4_y0.tmx   <- carry-over chunk for a 128-wide zone

Chunk size = 30×30 tiles (Andor's Trail standard).
Each Stendhal zone independently generates ceil(zone_w / 30) ×
ceil(zone_h / 30) chunks.  For a 128-tile-wide zone:
  cx=0–3  cover source tiles 0–119   (4 full 30-tile chunks = 120 tiles)
  cx=4    covers source tiles 120–127  (8 col carry-over, padded to 30)
The last chunk is padded to full 30×30 with empty tiles / blocked walkable.
Both right (x) and down (y) carry-over work identically.

Run from the Stendhal project ROOT directory (the one containing data/, tiled/).

Outputs
-------
  res/xml/{zone_name}_x{cx}_y{cy}.tmx   – Andor's Trail map files
  res/drawable/<flat_name>.png           – Tileset images (directory-flattened)
  res/xml/worldmap.xml                   – Andor's Trail world map manifest
  res/values/loadresources.xml           – Android string-array resource file
  stendhal_world.world                   – Tiled Editor .world file

Requirements: Python 3.6+  (no third-party packages needed)
"""

import os, sys, re, shutil, base64, zlib, struct, math
import glob, json
import xml.etree.ElementTree as ET
from pathlib import Path

# ─── tuneable constants ────────────────────────────────────────────────────────
STENDHAL_ZONE_CONF   = "data/conf/zones"
DATA_MAPS_BASE       = "data/maps"
OUTPUT_XML           = os.path.join("res", "xml")
OUTPUT_DRAWABLE      = os.path.join("res", "drawable")
OUTPUT_VALUES        = os.path.join("res", "values")
WORLD_FILE           = "stendhal_world.world"

ZONE_NS   = "stendhal"
ZONE_TAG  = f"{{{ZONE_NS}}}zone"

# AT map chunk dimensions in tiles.
# 30×30 matches Andor's Trail standard.
# A 128-wide Stendhal zone → 4 full 30-tile chunks (4×30=120 tiles) + 1 carry-over
# chunk holding the remaining 8 tiles (padded to 30), named {zone}_x4_y* etc.
AT_MAP_WIDTH  = 30
AT_MAP_HEIGHT = 30
TILE_PX       = 32
STENDHAL_SECTOR_SIZE = 32   # stendhal world-coord units per tile

LAYER_MAP = {
    "0_floor"   : "Ground",
    "1_terrain" : "Object",
    "2_object"  : "Object2",
    "3_roof"    : "Above",
    "4_roof_add": "Above2",
    "collision" : "Walkable",
}
AT_LAYER_ORDER = ["Ground", "Object", "Object2", "Above", "Above2", "Walkable"]
AT_MAPEVENTS   = "MapEvents"

FLIP_H    = 0x80000000
FLIP_V    = 0x40000000
FLIP_D    = 0x20000000
FLIP_MASK = FLIP_H | FLIP_V | FLIP_D


# ─── helpers ──────────────────────────────────────────────────────────────────

def flatten_image_name(raw_path: str) -> str:
    p = raw_path.replace("\\", "/")
    p = re.sub(r"^[./]+", "", p)
    parts = [s for s in p.split("/") if s and s != ".."]
    return "_".join(parts)


def decode_layer_data(data_el: ET.Element):
    enc  = data_el.get("encoding", "xml")
    comp = data_el.get("compression", "")
    text = (data_el.text or "").strip()
    if enc == "base64":
        raw = base64.b64decode(text)
        if comp == "zlib":
            raw = zlib.decompress(raw)
        elif comp == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        n = len(raw) // 4
        return list(struct.unpack("<" + "I" * n, raw))
    elif enc == "csv":
        return [int(v.strip()) for v in text.split(",") if v.strip()]
    else:
        return [int(t.get("gid", "0")) for t in data_el.findall("tile")]


def encode_layer_data(tiles) -> str:
    raw = struct.pack("<" + "I" * len(tiles), *tiles)
    return base64.b64encode(zlib.compress(raw)).decode("ascii")


def tile_at(tiles, x, y, w):
    i = y * w + x
    return tiles[i] if 0 <= i < len(tiles) else 0


def png_dimensions(path: str):
    try:
        with open(path, "rb") as f:
            hdr = f.read(24)
        if hdr[:8] == b"\x89PNG\r\n\x1a\n":
            w = struct.unpack(">I", hdr[16:20])[0]
            h = struct.unpack(">I", hdr[20:24])[0]
            return w, h
    except Exception:
        pass
    return 0, 0


def indent_xml(el: ET.Element, level=0):
    pad = "\n" + "  " * level
    if len(el):
        if not (el.text and el.text.strip()):
            el.text = pad + "  "
        for child in el:
            indent_xml(child, level + 1)
            if not (child.tail and child.tail.strip()):
                child.tail = pad + "  "
        child.tail = pad
    if level and not (el.tail and el.tail.strip()):
        el.tail = pad


# ─── zone config ──────────────────────────────────────────────────────────────

class ZoneInfo:
    __slots__ = ("name", "level", "wx", "wy", "width", "height", "tmx_rel")

    def __init__(self, name, level, wx, wy, tmx_rel, width=0, height=0):
        self.name    = name
        self.level   = level
        self.wx      = wx       # world-tile x origin (normalised to 0-based)
        self.wy      = wy
        self.width   = width    # zone width in tiles (filled from TMX)
        self.height  = height
        self.tmx_rel = tmx_rel


def load_zone_configs(conf_dir: str):
    zones = []
    files  = glob.glob(os.path.join(conf_dir, "**", "*.xml"), recursive=True)
    files += glob.glob(os.path.join(conf_dir, "*.xml"))
    files  = sorted(set(files))
    if not files:
        print(f"  [WARN] No XML files found under {conf_dir}")
        return zones
    for f in files:
        try:
            tree = ET.parse(f)
        except ET.ParseError as e:
            print(f"  [WARN] XML parse error in {f}: {e}")
            continue
        root = tree.getroot()
        elements = list(root.iter(ZONE_TAG))
        if not elements:
            elements = list(root.iter("zone"))
        for z in elements:
            lvl_str  = z.get("level", "")
            name     = z.get("name",  "")
            is_level0 = (lvl_str == "0") or (lvl_str == "" and name.startswith("0_"))
            if not is_level0:
                continue
            x_str   = z.get("x", "0")
            y_str   = z.get("y", "0")
            tmx_rel = z.get("file", "")
            if not tmx_rel:
                continue
            try:
                wx = int(x_str) // STENDHAL_SECTOR_SIZE
                wy = int(y_str) // STENDHAL_SECTOR_SIZE
            except ValueError:
                continue
            zones.append(ZoneInfo(name, 0, wx, wy, tmx_rel))
    return zones


def resolve_tmx_path(tmx_rel: str) -> str:
    candidates = [
        os.path.join(DATA_MAPS_BASE, tmx_rel),
        tmx_rel,
        os.path.join(DATA_MAPS_BASE, tmx_rel.replace(" ", "_")),
        os.path.join("tiled", tmx_rel),
        os.path.join("tiled", tmx_rel.replace(" ", "_")),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return ""


# ─── Stendhal TMX reader ──────────────────────────────────────────────────────

class StendhalTMX:
    def __init__(self, path: str):
        self.path   = path
        self.dir    = os.path.dirname(os.path.abspath(path))
        tree        = ET.parse(path)
        root        = tree.getroot()
        self.width  = int(root.get("width",  0))
        self.height = int(root.get("height", 0))
        self.tw     = int(root.get("tilewidth",  TILE_PX))
        self.th     = int(root.get("tileheight", TILE_PX))
        self.tilesets = []
        self.layers   = {}
        self._parse(root)

    def _parse(self, root: ET.Element):
        for ts_el in root.findall("tileset"):
            fg        = int(ts_el.get("firstgid", 1))
            src       = ts_el.get("source", "")
            name      = ts_el.get("name",   "")
            tilecount = int(ts_el.get("tilecount", 0))
            columns   = int(ts_el.get("columns",   0))
            img_src   = ""
            if src:
                tsx = os.path.normpath(os.path.join(self.dir, src))
                if os.path.isfile(tsx):
                    try:
                        t = ET.parse(tsx).getroot()
                        img_el = t.find("image")
                        if img_el is not None:
                            img_src = img_el.get("source", "")
                        name      = t.get("name",      name)
                        tilecount = int(t.get("tilecount", tilecount))
                        columns   = int(t.get("columns",   columns))
                    except Exception:
                        pass
            else:
                img_el = ts_el.find("image")
                if img_el is not None:
                    img_src = img_el.get("source", "")
            self.tilesets.append({
                "firstgid":  fg,
                "name":      name,
                "image":     img_src,
                "tilecount": tilecount,
                "columns":   columns,
            })
        self.tilesets.sort(key=lambda t: t["firstgid"])
        for layer_el in root.findall("layer"):
            lname   = layer_el.get("name", "")
            data_el = layer_el.find("data")
            if data_el is not None:
                self.layers[lname] = decode_layer_data(data_el)

    def resolve_image(self, ts: dict) -> str:
        img = ts["image"]
        if not img:
            return ""
        p = os.path.normpath(os.path.join(self.dir, img))
        if os.path.isfile(p):
            return p
        clean = re.sub(r"^[./]+", "", img)
        for base in (DATA_MAPS_BASE, "tiled", "."):
            p2 = os.path.normpath(os.path.join(base, clean))
            if os.path.isfile(p2):
                return p2
        return ""

    def gid_to_tileset(self, gid: int):
        if gid == 0:
            return None, 0
        clean = gid & ~FLIP_MASK
        ts_found = None
        for ts in reversed(self.tilesets):
            if clean >= ts["firstgid"]:
                ts_found = ts
                break
        if ts_found is None:
            return None, 0
        return ts_found, clean - ts_found["firstgid"]


# ─── tileset registry ─────────────────────────────────────────────────────────

class TilesetRegistry:
    def __init__(self):
        self._img_to_info = {}
        self._next_gid    = 1

    def register(self, abs_img: str, flat_name: str,
                 hint_tilecount=0, hint_columns=0):
        if abs_img not in self._img_to_info:
            w, h = png_dimensions(abs_img) if abs_img else (0, 0)
            if hint_columns > 0 and hint_tilecount > 0:
                cols      = hint_columns
                tilecount = hint_tilecount
            else:
                cols      = max(1, w  // TILE_PX) if w  else max(1, hint_columns)
                rows      = max(1, h  // TILE_PX) if h  else 1
                tilecount = cols * rows if (w or h) else max(256, hint_tilecount)
            stem = os.path.splitext(flat_name)[0]
            self._img_to_info[abs_img] = {
                "firstgid":  self._next_gid,
                "flat_name": flat_name,
                "name":      stem,
                "w": w, "h": h,
                "cols": cols,
                "tilecount": tilecount,
            }
            self._next_gid += max(1, tilecount)

    def remap_gid(self, raw_gid: int, src_tmx: StendhalTMX,
                  abs_img_cache: dict) -> int:
        if raw_gid == 0:
            return 0
        flags   = raw_gid &  FLIP_MASK
        clean   = raw_gid & ~FLIP_MASK
        ts, lid = src_tmx.gid_to_tileset(clean)
        if ts is None:
            return 0
        abs_img = abs_img_cache.get(ts["image"], "")
        if not abs_img or abs_img not in self._img_to_info:
            return 0
        return (self._img_to_info[abs_img]["firstgid"] + lid) | flags

    def tilesets_list(self):
        return sorted(self._img_to_info.values(), key=lambda d: d["firstgid"])


# ─── copy tilesets ────────────────────────────────────────────────────────────

_copied: set = set()

def ensure_tileset_copied(abs_img: str, flat_name: str):
    if flat_name not in _copied and abs_img and os.path.isfile(abs_img):
        os.makedirs(OUTPUT_DRAWABLE, exist_ok=True)
        shutil.copy2(abs_img, os.path.join(OUTPUT_DRAWABLE, flat_name))
        _copied.add(flat_name)


# ─── AT TMX writer ────────────────────────────────────────────────────────────

def build_at_tmx(layer_tiles: dict, registry: TilesetRegistry,
                 exits: list, next_obj_id: int) -> str:
    root = ET.Element("map")
    root.set("version",      "1.0")
    root.set("orientation",  "orthogonal")
    root.set("renderorder",  "right-down")
    root.set("width",        str(AT_MAP_WIDTH))
    root.set("height",       str(AT_MAP_HEIGHT))
    root.set("tilewidth",    str(TILE_PX))
    root.set("tileheight",   str(TILE_PX))
    root.set("nextobjectid", str(max(next_obj_id, len(exits) + 1)))

    for ts in registry.tilesets_list():
        ts_el = ET.SubElement(root, "tileset")
        ts_el.set("firstgid",   str(ts["firstgid"]))
        ts_el.set("name",       ts["name"])
        ts_el.set("tilewidth",  str(TILE_PX))
        ts_el.set("tileheight", str(TILE_PX))
        ts_el.set("tilecount",  str(ts["tilecount"]))
        ts_el.set("columns",    str(ts["cols"]))
        img_el = ET.SubElement(ts_el, "image")
        img_el.set("source", f"../drawable/{ts['flat_name']}")
        if ts["w"]: img_el.set("width",  str(ts["w"]))
        if ts["h"]: img_el.set("height", str(ts["h"]))

    for lname in AT_LAYER_ORDER:
        tiles = layer_tiles.get(lname, [0] * (AT_MAP_WIDTH * AT_MAP_HEIGHT))
        ly_el   = ET.SubElement(root, "layer")
        ly_el.set("name",   lname)
        ly_el.set("width",  str(AT_MAP_WIDTH))
        ly_el.set("height", str(AT_MAP_HEIGHT))
        data_el = ET.SubElement(ly_el, "data")
        data_el.set("encoding",    "base64")
        data_el.set("compression", "zlib")
        data_el.text = "\n   " + encode_layer_data(tiles) + "\n  "

    og_el = ET.SubElement(root, "objectgroup")
    og_el.set("name", AT_MAPEVENTS)
    for i, ex in enumerate(exits):
        obj = ET.SubElement(og_el, "object")
        obj.set("id",     str(i + 1))
        obj.set("name",   ex["name"])
        obj.set("type",   "mapExit")
        obj.set("x",      str(ex["x"] * TILE_PX))
        obj.set("y",      str(ex["y"] * TILE_PX))
        obj.set("width",  str(ex["w"] * TILE_PX))
        obj.set("height", str(ex["h"] * TILE_PX))
        props = ET.SubElement(obj, "properties")
        for k, v in [("map", ex["target_map"]),
                     ("x",   str(ex["target_x"])),
                     ("y",   str(ex["target_y"]))]:
            p = ET.SubElement(props, "property")
            p.set("name",  k)
            p.set("value", str(v))

    indent_xml(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


# ─── exit generation ──────────────────────────────────────────────────────────

def _consecutive_groups(positions):
    if not positions:
        return []
    groups, start, prev = [], positions[0], positions[0]
    for p in positions[1:]:
        if p != prev + 1:
            groups.append((start, prev - start + 1))
            start = p
        prev = p
    groups.append((start, prev - start + 1))
    return groups


def generate_exits(map_id: str, walkable_tiles: list,
                   all_map_ids: set, neighbor_fn) -> list:
    W, H = AT_MAP_WIDTH, AT_MAP_HEIGHT
    edges = {
        "north": ([x for x in range(W) if tile_at(walkable_tiles, x, 0,   W) == 0],
                  lambda s, l: (s, 0,   l, 1), lambda s, l: (s, H-2)),
        "south": ([x for x in range(W) if tile_at(walkable_tiles, x, H-1, W) == 0],
                  lambda s, l: (s, H-1, l, 1), lambda s, l: (s, 1)),
        "west":  ([y for y in range(H) if tile_at(walkable_tiles, 0,   y, W) == 0],
                  lambda s, l: (0,   s, 1, l), lambda s, l: (W-2, s)),
        "east":  ([y for y in range(H) if tile_at(walkable_tiles, W-1, y, W) == 0],
                  lambda s, l: (W-1, s, 1, l), lambda s, l: (1, s)),
    }
    exits = []
    for direction, (open_pos, rect_fn, target_fn) in edges.items():
        if not open_pos:
            continue
        nbr = neighbor_fn(map_id, direction)
        if nbr is None or nbr not in all_map_ids:
            continue
        for i, (start, length) in enumerate(_consecutive_groups(open_pos)):
            suffix = "" if i == 0 else str(i + 1)
            ex, ey, ew, eh = rect_fn(start, length)
            tx, ty = target_fn(start, length)
            exits.append({
                "name":       direction + suffix,
                "x": ex, "y": ey, "w": ew, "h": eh,
                "target_map": nbr,
                "target_x":   tx,
                "target_y":   ty,
            })
    return exits


# ─── chunk plan (per-zone) ────────────────────────────────────────────────────

def build_chunk_plan(zones_with_tmx: list):
    """
    Per-zone chunking strategy:
      For each Stendhal zone, independently split into AT_MAP_WIDTH × AT_MAP_HEIGHT
      tiles and name each chunk  {zone.name}_x{cx}_y{cy}.

      The "world position" of chunk (cx, cy) in zone Z is:
          world_tile_x = Z.wx + cx * AT_MAP_WIDTH
          world_tile_y = Z.wy + cy * AT_MAP_HEIGHT

      This world position is used solely for exit adjacency detection.

    Returns (chunks, map_id→(world_cx, world_cy)) where world_cx/cy are in
    AT-chunk units (not tile units).
    """
    # First pass: record zone tile dimensions from TMX
    zone_list = []
    for z, stmx in zones_with_tmx:
        z.width  = stmx.width
        z.height = stmx.height
        zone_list.append((z, stmx))

    # Normalise world tile origins to 0-based
    min_wx = min(z.wx for z, _ in zone_list)
    min_wy = min(z.wy for z, _ in zone_list)
    for z, _ in zone_list:
        z.wx -= min_wx
        z.wy -= min_wy

    chunks = []   # list of dicts
    # map_id → (world_chunk_x, world_chunk_y) for adjacency lookup
    id_to_world: dict = {}
    # world_chunk_pos → map_id for adjacency lookup
    world_to_id: dict = {}

    for z, stmx in zone_list:
        n_cx = max(1, math.ceil(stmx.width  / AT_MAP_WIDTH))
        n_cy = max(1, math.ceil(stmx.height / AT_MAP_HEIGHT))
        for cy in range(n_cy):
            for cx in range(n_cx):
                # Name
                map_id = f"{z.name}_x{cx}_y{cy}"

                # Source tile offset within this zone's TMX
                ox = cx * AT_MAP_WIDTH
                oy = cy * AT_MAP_HEIGHT

                # World chunk position (in AT-chunk units, used for adjacency)
                # We convert zone world-tile origin + chunk tile offset → chunk units
                # by dividing by AT_MAP_WIDTH (integer, so positions may share
                # a world-chunk slot if zones overlap).
                wcx = (z.wx + ox) // AT_MAP_WIDTH
                wcy = (z.wy + oy) // AT_MAP_HEIGHT

                # Resolve collision: if slot already taken, keep existing entry
                # but still register under an alternate key so exits can link
                if (wcx, wcy) in world_to_id:
                    # Use a sub-slot approach: find first free offset
                    offset = 1
                    while (wcx * 100 + offset, wcy) in world_to_id:
                        offset += 1
                    world_to_id[(wcx * 100 + offset, wcy)] = map_id
                else:
                    world_to_id[(wcx, wcy)] = map_id

                id_to_world[map_id] = (wcx, wcy)

                chunks.append({
                    "map_id": map_id,
                    "zone":   z,
                    "stmx":   stmx,
                    "ox":     ox,
                    "oy":     oy,
                    "wcx":    wcx,
                    "wcy":    wcy,
                })

    return chunks, id_to_world, world_to_id


def make_neighbor_fn(id_to_world: dict, world_to_id: dict):
    """Return neighbor(map_id, direction) → neighbor_map_id | None."""
    deltas = {"north": (0,-1), "south": (0,1), "west": (-1,0), "east": (1,0)}

    def neighbor(map_id: str, direction: str):
        pos = id_to_world.get(map_id)
        if pos is None:
            return None
        dx, dy = deltas[direction]
        return world_to_id.get((pos[0] + dx, pos[1] + dy))

    return neighbor


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  Stendhal → Andor's Trail Converter  (zone-named, 120-tile maps)")
    print("=" * 65)

    if not os.path.isdir(STENDHAL_ZONE_CONF) and not os.path.isdir(DATA_MAPS_BASE):
        print(f"\n[ERROR] Neither '{STENDHAL_ZONE_CONF}' nor '{DATA_MAPS_BASE}' found.")
        print("Run this script from the Stendhal project root directory.")
        sys.exit(1)

    os.makedirs(OUTPUT_XML,      exist_ok=True)
    os.makedirs(OUTPUT_DRAWABLE, exist_ok=True)
    os.makedirs(OUTPUT_VALUES,   exist_ok=True)

    # ── 1. Zone configs ────────────────────────────────────────────
    print(f"\n[1/6] Loading zone configs from {STENDHAL_ZONE_CONF} ...")
    zones = load_zone_configs(STENDHAL_ZONE_CONF)
    print(f"      Found {len(zones)} level-0 zones")
    if not zones:
        zones = _fallback_scan_tmx()
        if not zones:
            print("[ERROR] No maps found. Aborting.")
            sys.exit(1)

    # ── 2. Load TMX files ──────────────────────────────────────────
    print(f"\n[2/6] Resolving {len(zones)} TMX files ...")
    zones_with_tmx = []
    missing = []
    for z in zones:
        path = resolve_tmx_path(z.tmx_rel)
        if not path:
            missing.append(z.tmx_rel)
            continue
        try:
            zones_with_tmx.append((z, StendhalTMX(path)))
        except Exception as e:
            print(f"  [WARN] {path}: {e}")
    if missing:
        print(f"  [WARN] {len(missing)} TMX file(s) not found")
    print(f"  Loaded {len(zones_with_tmx)} maps successfully")

    # ── 3. Per-zone chunk plan ─────────────────────────────────────
    print("\n[3/6] Building per-zone AT chunk plan ...")
    chunks, id_to_world, world_to_id = build_chunk_plan(zones_with_tmx)

    total_chunks = len(chunks)
    all_map_ids  = set(cd["map_id"] for cd in chunks)
    neighbor_fn  = make_neighbor_fn(id_to_world, world_to_id)

    # Diagnostic: show per-zone breakdown
    zone_chunk_counts: dict = {}
    for cd in chunks:
        zname = cd["zone"].name
        zone_chunk_counts[zname] = zone_chunk_counts.get(zname, 0) + 1
    multi = {k: v for k, v in zone_chunk_counts.items() if v > 1}

    print(f"  {total_chunks} AT chunks from {len(zones_with_tmx)} zones")
    if multi:
        print(f"  Zones split into multiple chunks ({len(multi)} zones):")
        for zn, cnt in sorted(multi.items()):
            print(f"    {zn}  → {cnt} chunks")

    # ── 4. Write AT TMX chunks ─────────────────────────────────────
    print(f"\n[4/6] Writing {total_chunks} AT map chunks ...")
    output_maps = []

    for cd in chunks:
        map_id = cd["map_id"]
        stmx   = cd["stmx"]
        ox, oy = cd["ox"], cd["oy"]
        wcx    = cd["wcx"]
        wcy    = cd["wcy"]

        # Absolute image path cache
        abs_img_cache = {}
        for ts in stmx.tilesets:
            img = ts["image"]
            if img:
                abs_img_cache[img] = stmx.resolve_image(ts)

        # Tileset registry for this chunk
        registry = TilesetRegistry()
        for ts in stmx.tilesets:
            img       = ts["image"]
            abs_img   = abs_img_cache.get(img, "")
            flat_name = flatten_image_name(img) if img else ""
            if flat_name:
                registry.register(abs_img, flat_name,
                                  hint_tilecount=ts.get("tilecount", 0),
                                  hint_columns=ts.get("columns",   0))
                ensure_tileset_copied(abs_img, flat_name)

        # Extract, remap and pad tile data
        layer_tiles = {}
        for st_lname, at_lname in LAYER_MAP.items():
            src = stmx.layers.get(st_lname, [])
            out = []
            for ty in range(AT_MAP_HEIGHT):
                for tx in range(AT_MAP_WIDTH):
                    sx, sy  = ox + tx, oy + ty
                    # Out-of-bounds source tiles become empty (0) — the padding/carry
                    gid     = tile_at(src, sx, sy, stmx.width) if src else 0
                    new_gid = registry.remap_gid(gid, stmx, abs_img_cache)
                    if at_lname == "Walkable":
                        # Out-of-bounds = blocked (1); in-bounds empty = passable (0)
                        if sx >= stmx.width or sy >= stmx.height:
                            new_gid = 1   # out-of-zone → blocked
                        else:
                            new_gid = 1 if new_gid != 0 else 0
                    out.append(new_gid)
            layer_tiles[at_lname] = out

        exits = generate_exits(map_id, layer_tiles["Walkable"],
                               all_map_ids, neighbor_fn)

        tmx_str  = build_at_tmx(layer_tiles, registry, exits, len(exits) + 1)
        fname    = f"{map_id}.tmx"
        out_path = os.path.join(OUTPUT_XML, fname)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(tmx_str)

        output_maps.append({
            "map_id":   map_id,
            "filename": fname,
            "wcx":      wcx,
            "wcy":      wcy,
        })
        print(f"  wrote  {fname}  ({len(exits)} exits)")

    # ── 5. worldmap.xml ───────────────────────────────────────────
    print(f"\n[5/6] Writing resource files ...")
    wm_root = ET.Element("WorldMap")
    for m in output_maps:
        me = ET.SubElement(wm_root, "map")
        me.set("id",       m["map_id"])
        me.set("filename", m["filename"])
        me.set("x",        str(m["wcx"]))
        me.set("y",        str(m["wcy"]))
    indent_xml(wm_root)
    wm_path = os.path.join(OUTPUT_XML, "worldmap.xml")
    with open(wm_path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 + ET.tostring(wm_root, encoding="unicode"))
    print(f"  wrote {wm_path}")

    # loadresources.xml
    lr_root  = ET.Element("resources")
    arr_maps = ET.SubElement(lr_root, "string-array"); arr_maps.set("name", "map_files")
    for m in output_maps:
        ET.SubElement(arr_maps, "item").text = m["filename"]
    arr_tiles = ET.SubElement(lr_root, "string-array"); arr_tiles.set("name", "tile_files")
    for fname in sorted(_copied):
        ET.SubElement(arr_tiles, "item").text = fname
    indent_xml(lr_root)
    lr_path = os.path.join(OUTPUT_VALUES, "loadresources.xml")
    with open(lr_path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 + ET.tostring(lr_root, encoding="unicode"))
    print(f"  wrote {lr_path}")

    # Tiled .world file
    world_maps = [{
        "fileName": f"../xml/{m['filename']}",
        "x":        m["wcx"] * AT_MAP_WIDTH  * TILE_PX,
        "y":        m["wcy"] * AT_MAP_HEIGHT * TILE_PX,
        "width":    AT_MAP_WIDTH  * TILE_PX,
        "height":   AT_MAP_HEIGHT * TILE_PX,
    } for m in output_maps]
    with open(WORLD_FILE, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "world", "maps": world_maps}, indent=2))
    print(f"  wrote {WORLD_FILE}")

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  Conversion complete!")
    print(f"  Maps   : {OUTPUT_XML}/   ({len(output_maps)} files)")
    print(f"  Tiles  : {OUTPUT_DRAWABLE}/  ({len(_copied)} images)")
    print(f"  Chunks : {AT_MAP_WIDTH}×{AT_MAP_HEIGHT} tiles each  (128-wide zone → 4 full + 1 carry-over chunk)")
    print(f"  Naming : {{stendhal_zone_name}}_x{{cx}}_y{{cy}}.tmx")
    print("=" * 65)


# ─── fallback: scan data/maps/Level 0/ ───────────────────────────────────────

def _fallback_scan_tmx():
    for candidate in [
        os.path.join(DATA_MAPS_BASE, "Level 0"),
        os.path.join(DATA_MAPS_BASE, "Level_0"),
        os.path.join("tiled", "Level 0"),
        os.path.join("tiled", "Level_0"),
        DATA_MAPS_BASE,
    ]:
        if os.path.isdir(candidate):
            base = candidate
            break
    else:
        return []
    print(f"  Scanning fallback directory: {base}")
    tmx_files = sorted(glob.glob(os.path.join(base, "**", "*.tmx"), recursive=True))
    zones = []
    coord_pattern = re.compile(r"(-?\d+)_(-?\d+)(?:\.tmx)?$")
    for f in tmx_files:
        stem = Path(f).stem
        m    = coord_pattern.search(stem)
        if m:
            wx, wy = int(m.group(1)), int(m.group(2))
        else:
            idx    = len(zones)
            grid_w = max(1, int(math.sqrt(len(tmx_files))) + 1)
            wx, wy = idx % grid_w, idx // grid_w
        zones.append(ZoneInfo(stem, 0, wx, wy, os.path.relpath(f, DATA_MAPS_BASE)))
    return zones


if __name__ == "__main__":
    main()
