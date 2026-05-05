# Jasia's Quest — "Search for Sunny" Content Overlay

A content overlay for the [jasias-quest](https://github.com/jmlucas31070-dev/jasias-quest)
fork of Andor's Trail. Adds a full main quest, supporting cast, central
narrative maps, and 7 colored moons (each a 3×3 region grid).

## What's inside

```
res/
  values/
    loadresources.xml   # registers every JSON file in this pack
    strings.xml         # all NPC names, signs, and quest titles
  xml/
    worldmap.xml        # worldmap layout for every new map
    home.tmx            # patched: west door now opens onto Servants' Hall
    jq_*.tmx            # 88 new TMX maps (central + 63 moon cells)
  raw/
    jq_items.json
    jq_droplists.json
    jq_monsters.json
    jq_conversationlists.json
    jq_quests.json
    jq_maps.json
    jq_actorconditions.json
    jq_itemcategories.json
```

## Installation

1. Copy this `res/` tree on top of `AndorsTrail/res/` in your fork.
   - `home.tmx` is overwritten — its west door now opens onto the Servants'
     Hall (where Maid Maelyn starts the quest), which then leads on to
     `castle_entry`. All other doors are unchanged.
2. Merge `values/loadresources.xml` into your existing one — append every
   `<item>` from this pack into the matching `<array>` in the base file.
3. Merge `xml/worldmap.xml` into your existing worldmap.xml (add this pack's
   `<map>` entries under `<worldmap>`).
4. Merge the new `<string>` entries from `values/strings.xml` into your base
   `strings.xml`.
5. Rebuild the APK from Android Studio. Resource IDs all carry the `jq_`
   prefix to avoid collisions with `wg_` (existing) content.

## Story summary (Search for Sunny)

You are **Princess Jasia**, daughter of King Ozzy and Queen Nymph. Your sister
Sunny vanished. The trail begins with a maid at the door of your home and
runs through the prison guard, the witch Morwenna, the city's thieves'
guild, the party Sunny rode with (Steve, Cara, Sam), Semos Mountain,
the drow under it, Matron Lloth, the dragons of the volcano, the mountain
top, the ring tent world, and the seven colored moons — Silver, Crimson,
Azure, Gold, Emerald, Violet, and Pearl.

## Stats

- 89 new maps (1 servants' hall, 1 rumor board, 1 witch hut, 1 thief guild,
  1 Semos city, 2 drow caves + council, 1 dragon central + 1 thrones
  + 10 dragon chambers, 1 mountain top, 5 ring world maps, 63 moon maps)
- 195 NPCs and monsters
- 263 conversations
- 59 quests (main + dragon council + 25 region quests + 7 moon-elder quests
  + 3 party-member side quests + 12 party-tale quests + 10 dragon-court
  quests + 1 dragon council)
- 47 quest items (locket, wand, cloak, ring, sigil, tent ring, moon
  rocket tickets ×7, region clues ×25, etc.)
- 27 droplists, 326 string resources

## Conventions

- Every new id uses the `jq_` prefix (Jasia's Quest).
- TMX maps use the standard 16×12 / 32px tile grid the existing castle maps
  use, and reference `indoor1.tsx`, `outdoor1/2.tsx`, `objects1.tsx`,
  `cave1.tsx` from your existing tilesets.
- Per-moon spawn groups are named `jq_moon_<color>_<x>_<y>_wild` /
  `_city` / `_path` / `_town`.
- The "rumor board" archivist gives one quest per region (25 in total),
  carefully written to NOT duplicate any task Sunny is said to have done.

## What's intentionally minimal

- The 63 moon TMX files are templated 16×12 single-tile maps with proper
  doors, NPCs, containers and spawn nodes. They are playable as-is and ready
  for art passes (replace the single-tile `csv` with a real Tiled-painted
  ground layer).
- The dragon chamber maps follow the same pattern.
- For region quest givers, instead of patching 25 existing region TMX files,
  the pack adds a single `jq_rumor_board` map (Archivist Yelda) reachable
  from the Servants' Hall, which routes all 25 region quests in one place.
