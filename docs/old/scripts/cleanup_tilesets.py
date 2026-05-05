#!/usr/bin/env python3
"""
cleanup_tilesets.py — Identifies and moves unused tileset PNG files.

Run from the scripts/ directory of the jasias-quest repository:

    python3 cleanup_tilesets.py

What it does
------------
1. Scans all level_0*.tmx maps in AndorsTrail/res/xml/ for referenced tilesets.
2. Scans all template maps (template*.tmx, jq*template*.tmx, jqa_template*.tmx)
   for referenced tilesets.
3. Identifies PNG files in AndorsTrail/res/drawable/ that are not referenced
   by ANY level_0 map AND not referenced by ANY template map.
4. Creates AndorsTrail/res/unused_tileset/ (if needed) and moves the unused
   PNG files there.
5. Writes unused_tileset/moved_files.txt listing every file that was moved.

Pass --dry-run to preview what would be moved without actually moving anything.
Pass --verbose to print every tileset name that is found as used.
"""

import argparse
import glob
import os
import re
import shutil
import sys

TILESET_NAME_RE = re.compile(r"<tileset\b[^>]*\bname=['\"]([^'\"]+)['\"]")

TEMPLATE_GLOBS = [
    "template*.tmx",
    "jq*template*.tmx",
    "jqa_template*.tmx",
    "jq_bank_template.tmx",
]


def get_tilesets_from_tmx(path: str, verbose: bool = False) -> set:
    """Return the set of tileset names referenced in a TMX file."""
    names: set = set()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        for m in TILESET_NAME_RE.finditer(content):
            names.add(m.group(1))
            if verbose:
                print(f"    [tileset] {m.group(1)}  ← {os.path.basename(path)}")
    except OSError as exc:
        print(f"  WARNING: could not read {path}: {exc}", file=sys.stderr)
    return names


def collect_tilesets(tmx_paths: list, label: str, verbose: bool) -> set:
    """Collect the union of all tileset names across a list of TMX files."""
    result: set = set()
    for path in tmx_paths:
        result |= get_tilesets_from_tmx(path, verbose)
    print(
        f"  {label}: {len(tmx_paths)} map(s) → {len(result)} unique tileset name(s) found."
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Move unused tileset PNGs to AndorsTrail/res/unused_tileset/"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving anything.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every tileset name as it is found.",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    xml_dir = os.path.join(repo_root, "AndorsTrail", "res", "xml")
    drawable_dir = os.path.join(repo_root, "AndorsTrail", "res", "drawable")
    unused_dir = os.path.join(repo_root, "AndorsTrail", "res", "unused_tileset")

    for d, label in [(xml_dir, "xml"), (drawable_dir, "drawable")]:
        if not os.path.isdir(d):
            print(f"ERROR: required directory not found: {d}", file=sys.stderr)
            print(
                f"  Make sure you are running this script from the scripts/ directory "
                f"and that the repo structure is intact.",
                file=sys.stderr,
            )
            sys.exit(1)

    print("=== Tileset Cleanup Script ===")
    print(f"  Repository root : {repo_root}")
    print(f"  XML map dir     : {xml_dir}")
    print(f"  Drawable dir    : {drawable_dir}")
    print(f"  Unused dir      : {unused_dir}")
    if args.dry_run:
        print("  Mode            : DRY RUN (nothing will be moved)\n")
    else:
        print()

    # ── 1. Level-0 maps ────────────────────────────────────────────────────
    print("Step 1: Scanning level_0 maps …")
    level0_maps = sorted(glob.glob(os.path.join(xml_dir, "level_0*.tmx")))
    if not level0_maps:
        print("  WARNING: No level_0*.tmx files found in xml dir.", file=sys.stderr)
    level0_tilesets = collect_tilesets(level0_maps, "level_0 maps", args.verbose)

    # ── 2. Template maps ───────────────────────────────────────────────────
    print("\nStep 2: Scanning template maps …")
    template_map_paths: set = set()
    for pattern in TEMPLATE_GLOBS:
        template_map_paths.update(glob.glob(os.path.join(xml_dir, pattern)))
    template_maps = sorted(template_map_paths)
    if not template_maps:
        print("  WARNING: No template TMX files found in xml dir.", file=sys.stderr)
    template_tilesets = collect_tilesets(template_maps, "template maps", args.verbose)

    # ── 3. All drawable PNGs ───────────────────────────────────────────────
    print("\nStep 3: Scanning drawable directory …")
    all_pngs = sorted(
        f for f in os.listdir(drawable_dir) if f.lower().endswith(".png")
    )
    print(f"  Found {len(all_pngs)} PNG file(s) in drawable.")

    # ── 4. Compute unused set ──────────────────────────────────────────────
    print("\nStep 4: Computing unused tilesets …")
    used_tilesets = level0_tilesets | template_tilesets

    def png_basename(filename: str) -> str:
        """Return the PNG filename without the .png extension."""
        return os.path.splitext(filename)[0]

    unused_pngs = sorted(
        f for f in all_pngs if png_basename(f) not in used_tilesets
    )

    print(f"  Level-0 tilesets used  : {len(level0_tilesets)}")
    print(f"  Template tilesets used : {len(template_tilesets)}")
    print(f"  Total used (union)     : {len(used_tilesets)}")
    print(f"  Total drawable PNGs    : {len(all_pngs)}")
    print(f"  Unused PNGs to move    : {len(unused_pngs)}")

    if not unused_pngs:
        print("\nNo unused tilesets found — nothing to move.")
        return

    print("\nUnused tileset files:")
    for f in unused_pngs:
        print(f"  {f}")

    # ── 5. Move (or dry-run) ───────────────────────────────────────────────
    if args.dry_run:
        print(f"\nDRY RUN complete. {len(unused_pngs)} file(s) would be moved to:")
        print(f"  {unused_dir}")
        return

    print(f"\nStep 5: Moving {len(unused_pngs)} file(s) to unused_tileset/ …")
    os.makedirs(unused_dir, exist_ok=True)

    moved: list = []
    errors: list = []
    for png in unused_pngs:
        src = os.path.join(drawable_dir, png)
        dst = os.path.join(unused_dir, png)
        try:
            shutil.move(src, dst)
            moved.append(png)
            print(f"  Moved: {png}")
        except OSError as exc:
            errors.append((png, str(exc)))
            print(f"  ERROR moving {png}: {exc}", file=sys.stderr)

    # ── 6. Write log file ─────────────────────────────────────────────────
    log_path = os.path.join(unused_dir, "moved_files.txt")
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write("Unused tileset PNG files moved by cleanup_tilesets.py\n")
        fh.write("=" * 54 + "\n\n")
        fh.write(f"Repository root : {repo_root}\n")
        fh.write(f"Source dir      : {drawable_dir}\n")
        fh.write(f"Destination dir : {unused_dir}\n\n")
        fh.write(f"Level-0 maps scanned    : {len(level0_maps)}\n")
        fh.write(f"Template maps scanned   : {len(template_maps)}\n")
        fh.write(f"Tilesets used (total)   : {len(used_tilesets)}\n")
        fh.write(f"Drawable PNGs total     : {len(all_pngs)}\n")
        fh.write(f"Files moved             : {len(moved)}\n\n")
        fh.write("Moved files\n-----------\n")
        for name in moved:
            fh.write(f"  {name}\n")
        if errors:
            fh.write("\nErrors (files NOT moved)\n------------------------\n")
            for name, msg in errors:
                fh.write(f"  {name}: {msg}\n")

    print(f"\nDone.")
    print(f"  Moved  : {len(moved)} file(s)")
    if errors:
        print(f"  Errors : {len(errors)} file(s) — see {log_path}")
    print(f"  Log    : {log_path}")


if __name__ == "__main__":
    main()
