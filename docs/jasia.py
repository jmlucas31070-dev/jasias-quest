#!/usr/bin/env python3
# jasia.py — unified generator: crafting, jasia (castle/quests), jasia2 (faction/jail), beast

import os
import re
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VALUES = ROOT / "values"
RAW = ROOT / "raw"
XML = ROOT / "xml"

# All generators share these output dirs
os.chdir(ROOT)
RAW.mkdir(exist_ok=True)
VALUES.mkdir(exist_ok=True)
XML.mkdir(exist_ok=True)

os.environ["jasia_ORCHESTRATE"] = "1"

LOADRESOURCES_HEADER = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
LOADRESOURCES_FOOTER = "</resources>\n"

ARRAY_ORDER = [
    "loadresource_actorconditions",
    "loadresource_conversationlists",
    "loadresource_quests",
    "loadresource_droplists",
    "loadresource_itemcategories",
    "loadresource_items",
    "loadresource_monsters",
]


def normalize_item_line(line: str) -> str:
    """Normalize resource reference lines for deduplication."""
    line = line.strip()
    if not line:
        return line
    # @raw/foo.json</item> -> @raw/foo</item>
    line = re.sub(r"(@raw/[\w_]+)\.json(</item>)", r"\1\2", line)
    # @raw/foo/item> -> @raw/foo</item>  (beast quest typo)
    line = re.sub(r"(@raw/[\w_]+)/item>", r"\1</item>", line)
    return line


def parse_loadresources_xml(text: str) -> dict[str, list[str]]:
    arrays: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<array name="):
            match = re.search(r'name="([^"]+)"', stripped)
            if match:
                current = match.group(1)
                arrays.setdefault(current, [])
        elif current and "<item>" in stripped:
            item = normalize_item_line(stripped)
            if item and item not in arrays[current]:
                arrays[current].append(item)
        elif stripped == "</array>":
            current = None
    return arrays


def merge_arrays(*parts: dict[str, list[str]]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for part in parts:
        for name, items in part.items():
            bucket = merged.setdefault(name, [])
            for item in items:
                item = normalize_item_line(item)
                if item and item not in bucket:
                    bucket.append(item)
    return merged


def extract_lr_from_source(py_file: Path, const_name: str = "LOADRESOURCES_XML") -> dict[str, list[str]]:
    if not py_file.exists():
        return {}
    text = py_file.read_text(encoding="utf-8")
    match = re.search(rf'{const_name}\s*=\s*"""(.*?)"""', text, re.DOTALL)
    if not match:
        return {}
    return parse_loadresources_xml(match.group(1))


def write_loadresources(merged: dict[str, list[str]], path: Path) -> None:
    lines = [LOADRESOURCES_HEADER.strip(), ""]
    order = list(ARRAY_ORDER)
    for name in sorted(merged.keys()):
        if name not in order:
            order.append(name)
    for name in order:
        items = merged.get(name)
        if not items:
            continue
        lines.append(f'    <array name="{name}">')
        for item in items:
            if not item.startswith("<"):
                item = f"        <item>@raw/{item}</item>"
            elif not item.startswith("        "):
                item = f"        {item.strip()}"
            lines.append(item)
        lines.append("    </array>")
        lines.append("")
    lines.append("</resources>")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_stage(label: str, script: str) -> None:
    print("=" * 52)
    print(f" jasia: {label}")
    print("=" * 52)
    runpy.run_path(str(ROOT / script), run_name="__main__")


def build_jasia2_fragment() -> dict[str, list[str]]:
    """Build faction/jail resource lists from jasia2 fragment file if present."""
    fragment_path = VALUES / "loadresources_jasia2_fragment.xml"
    if fragment_path.exists():
        return parse_loadresources_xml(fragment_path.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    merged: dict[str, list[str]] = {}

    # 1. Crafting (guilds, regions, shops — writes loadresources.xml)
    run_stage("crafting.py", "crafting.py")
    lr_path = VALUES / "loadresources.xml"
    if lr_path.exists():
        merged = merge_arrays(
            merged,
            parse_loadresources_xml(lr_path.read_text(encoding="utf-8")),
        )

    # 2. Jasia castle / sunny / holiday / towers (skips loadresources write)
    run_stage("jasia1.py (castle + quests)", "jasia1.py")
    merged = merge_arrays(merged, extract_lr_from_source(ROOT / "jasia1.py"))

    # 3. Faction + pickpocket + jail (skips crafting; writes fragment xml)
    run_stage("jasia2.py (factions + jail)", "jasia2.py")
    merged = merge_arrays(merged, build_jasia2_fragment())

    # 4. Astral beasts (skips loadresources write)
    run_stage("beast.py", "beast.py")
    merged = merge_arrays(merged, extract_lr_from_source(ROOT / "beast.py"))

    write_loadresources(merged, lr_path)

    print("")
    print("=" * 52)
    print(" jasia: all generators finished")
    print("=" * 52)
    print(f"  Raw JSON files : {len(list(RAW.glob('*.json')))}")
    print(f"  TMX maps       : {len(list(XML.glob('*.tmx')))}")
    print(f"  loadresources  : {lr_path}")
    for name in ARRAY_ORDER:
        count = len(merged.get(name, []))
        if count:
            print(f"    {name}: {count} entries")
    extra = [n for n in merged if n not in ARRAY_ORDER]
    for name in extra:
        print(f"    {name}: {len(merged[name])} entries")
    print("=" * 52)
    return 0


if __name__ == "__main__":
    sys.exit(main())
