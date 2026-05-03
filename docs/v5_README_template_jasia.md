# README — template_jasia.tmx
**Jasias Quest — Comprehensive New Map Template**

This template extends `template.tmx` with every reusable layer type used across
the Jasias Quest fork of Andor's Trail.  Copy it, rename it, and fill in the
`REPLACE_*` placeholders before adding to `loadresources.xml`.

---

## Files in this package

| File | Purpose |
|------|---------|
| `template_jasia.tmx` | Main map template (Tiled 1.10 format, 32×32 tiles) |
| `monsterlist_newyears.json` | New Years Baby NPC definition |
| `conversationlist_newyears.json` | New Years Baby + door conversations |
| `README_template_jasia.md` | This file |

---

## Layer stack at a glance

```
Ground              tile layer — floor art
Ground_replace      tile layer — blank; painted with holiday floor art
Objects             tile layer — objects / furniture
Objects_replace     tile layer — blank; painted with holiday objects
Above               tile layer — overhead fringe / rooftops
Above_replace       tile layer — blank; painted with holiday overhead
Walkable            tile layer — collision / passability flags
─────────────────────────────────────────────────────
Mapevents           object layer — exits N / S / E / W
Spawn_animals       object layer — terrain animal area (beach by default)
Spawn_faction       object layer — human faction NPCs
Keys_door           object layer — locked door + key/lockpick/bash system
Keys_forage         object layer — foraging node examples
Keys_crafting       object layer — all crafting stations
Keys_mining         object layer — all mining vein tiers
Replace_newyears    object layer — New Year holiday event trigger
Spawn_replace       object layer — New Years Baby NPC (holiday only)
```

---

## 1. Map exits (Mapevents)

Each compass exit is a `MapChange` object spanning the full 1024 px edge of the map.

| Object name | x | y | width | height |
|-------------|---|---|-------|--------|
| exit_north  | 0 | 0 | 1024 | 32 |
| exit_south  | 0 | 992 | 1024 | 32 |
| exit_east   | 992 | 0 | 32 | 1024 |
| exit_west   | 0 | 0 | 32 | 1024 |

**Properties to replace on each exit object:**

```
destinationMapId  →  ID of the adjacent map file (no .tmx extension)
destinationX      →  tile X where the player appears in the destination map
destinationY      →  tile Y where the player appears in the destination map
```

Convention: an exit from the **north** edge deposits the player near the **south**
edge of the destination (`destinationY ≈ 30`), and vice-versa.

---

## 2. Spawn_animals — terrain spawn groups

Set `spawnGroup` on the `Spawn_animals` objectgroup to any terrain type below.
The engine fills the objectgroup's bounding rectangle with random animals from
that group on each respawn tick.

### Outdoor / surface terrain animals

| spawnGroup | Biome description | Animal IDs |
|------------|-------------------|-----------|
| `beach` | Sandy shoreline — coastal creatures | beach_01 – beach_25 |
| `sea` | Shallow coastal water | sea_01 – sea_25 (Dolphin → Spiny Lobster) |
| `ocean` | Deep open sea | ocean_01 – ocean_25 (Blue Whale → Fangtooth Fish) |
| `river` | Freshwater rivers and streams | river_01 – river_25 |
| `grassland` | Open grassy plains | grassland_01 – grassland_08 (Wild Horse → Grass Viper) |
| `shrubland` | Low brush and scrub | shrubland_01 – shrubland_25 |
| `forest` | Temperate woodland | forest_01 – forest_25 |
| `deepforest` | Dense old-growth forest | deepforest_01 – deepforest_25 |
| `rainforest` | Tropical / jungle | rainforest_01 – rainforest_25 |
| `desert` | Arid sandy wastes | desert_01 – desert_25 |
| `tundra` | Frozen northern plains | tundra_01 – tundra_25 |
| `swamp` | Boggy marshland | swamp_01 – swamp_25 |
| `mountain` | High rocky peaks | mountain_01 – mountain_25 |

### Cave / underground terrain animals

These groups are used on indoor cave maps.  They share a shorter respawn timer
(caves are enclosed) and include many insect / vermin type creatures.

| spawnGroup | Environment description | Notes |
|------------|------------------------|-------|
| `dry_cave` | Dry cavern — bats, rats, cave spiders | Weakest cave tier |
| `damp_cave` | Damp cavern — slugs, cave fish, fungi-dwellers | Mid tier |
| `dark_cave` | Deep lightless cave — giant centipedes, blind salamanders | Strong tier |
| `crystal_cave` | Crystal-lit grotto — luminous beetles, crystal golems | Rare spawns |
| `hell_cave` | Volcanic / hellfire cavern — magma lizards, fire beetles | Strongest cave tier |

### Cave forage items (reference)

Forage nodes can be placed on cave maps using the same `Keys_forage` pattern.
Replace the `id` / `spawnGroup` with the cave-specific forage types below.

| Forage node id | Conversation id | Cave terrain | Notable drops |
|----------------|-----------------|-------------|---------------|
| `fm_node_forage_cave_common` | `fm_forage_cave_common_pick` | dry/damp | Bat guano, cave moss, pebbles |
| `fm_node_forage_cave_fungus` | `fm_forage_cave_fungus_pick` | damp/dark | Glowing mushroom, spore powder |
| `fm_node_forage_cave_crystal` | `fm_forage_cave_crystal_pick` | crystal_cave | Crystal shard, quartz dust |
| `fm_node_forage_cave_sulfur` | `fm_forage_cave_sulfur_pick` | hell_cave | Sulfur chunk, fire salt |

---

## 3. Spawn_faction — faction races

Replace the NPC `id` and `spawnGroup` values to switch to a different race.
Set `factionID` in the NPC's monsterlist entry to control alignment.

### Available faction races

| Race key | monsterlist file | NPC id prefix | spawnGroup prefix |
|----------|-----------------|--------------|------------------|
| **Human** | `monsterlist_human.json` | `npc_human_XXX` | `spawngroup_human_XXX` |
| **Elf** | `monsterlist_elf.json` | `npc_elf_XXX` | `spawngroup_elf_XXX` |
| **Wood Elf** | `monsterlist_woodelf.json` | `npc_woodelf_XXX` | `spawngroup_woodelf_XXX` |
| **Sea Elf** | `monsterlist_seaelf.json` | `npc_seaelf_XXX` | `spawngroup_seaelf_XXX` |
| **Half Elf** | `monsterlist_halfelf.json` | `npc_halfelf_XXX` | `spawngroup_halfelf_XXX` |
| **Dwarf** | `monsterlist_dwarf.json` | `npc_dwarf_XXX` | `spawngroup_dwarf_XXX` |
| **Gnome** | `monsterlist_gnome.json` | `npc_gnome_XXX` | `spawngroup_gnome_XXX` |
| **Halfling** | `monsterlist_halfling.json` | `npc_halfling_XXX` | `spawngroup_halfling_XXX` |
| **Orc** | `monsterlist_orc.json` | `npc_orc_XXX` | `spawngroup_orc_XXX` |
| **Goblin** | `monsterlist_goblin.json` | `npc_goblin_XXX` | `spawngroup_goblin_XXX` |
| **Hobgoblin** | `monsterlist_hobgoblin.json` | `npc_hobgoblin_XXX` | `spawngroup_hobgoblin_XXX` |
| **Ogre** | `monsterlist_ogre.json` | `npc_ogre_XXX` | `spawngroup_ogre_XXX` |
| **Dragon** | `monsterlist_dragon.json` | `npc_dragon_XXX` | `spawngroup_dragon_XXX` |
| **Drowelf** | `monsterlist_drowelf.json` | `npc_drowelf_XXX` | `spawngroup_drowelf_XXX` |

### Faction alignment IDs (faction property on monster)

| factionID | Behaviour |
|-----------|-----------|
| `faction_human` | Friendly to player unless attacked |
| `faction_elf` | Friendly to player unless attacked |
| `faction_dwarf` | Friendly to player unless attacked |
| `faction_orc` | Hostile by default |
| `faction_goblin` | Hostile by default |
| `faction_player` | Full ally — will assist in combat |
| `friendly` | Never attacks; used for quest NPCs |
| `neutral` | Passive; attacks only if struck |

---

## 4. Keys_door — door ability system

The `Keys_door` layer provides three interaction objects.  Place the appropriate
one on the visual door tile.

### Door objects

| Object name | type | conversationId | When to use |
|-------------|------|---------------|-------------|
| `LockedDoor` | interactable | `door_approach` | Standard locked door (key + lockpick + bash) |
| `LockedDoor_KeyOnly` | interactable | `door_key_only` | Single-use key door (key consumed on open) |
| `DoorLockControl` | interactable | `door_guard_lock` | Guard/lever that re-locks a door |

### door_approach interaction tree

```
door_approach
├── Pick the lock (Thief class only)
│   ├── Crude Lockpick     — 20 % success  (lockpick_crude consumed)
│   ├── Standard Lockpick  — 50 % success  (lockpick_standard consumed)
│   └── Masterwork Lockpick— 85 % success  (lockpick_masterwork consumed)
├── Bash it open (Fighter class only)
│   ├── No shield          — refused (text only)
│   ├── Cloth shield       — 30 % success
│   └── Metal shield       — 75 % success
└── Use a key (any class — requireItem: REPLACE_KEY_ID)
    └── Opens door / teleports player to destinationMapId
```

### Properties to fill in on each door object

```
requireItem       →  ID of the key item from itemlist (e.g. "key_iron_01")
consumeKey        →  true  if the key is destroyed on use, false to keep it
destinationMapId  →  ID of the room / inner map the door leads to
destinationX/Y    →  tile coords the player appears at in the destination
```

---

## 5. Keys_forage — foraging system

Each forage node is a zero-attack "monster" that the player interacts with.
A cooldown timer (`timerElapsed` check) prevents repeated harvesting.

### Forage node reference

| Object name | monsterType id | conversationId | Cooldown | Key drops |
|-------------|---------------|----------------|----------|-----------|
| `forage_common` | `fm_node_forage_common` | `fm_forage_common_pick` | 3456 s | Twigs, herbs, dandelion, mushrooms |
| `forage_berry` | `fm_node_forage_berry` | `fm_forage_berry_pick` | 3456 s | Red/blue/black berry, apple, pear, plum |
| `forage_nut` | `fm_node_forage_nut` | `fm_forage_nut_pick` | 3456 s | Acorns, walnuts, chestnuts, twigs |

### How to add a new forage spot

1. Add a `Spawn` object to the `Keys_forage` layer.
2. Set `id` and `spawnGroup` to the monsterType ID (e.g. `fm_node_forage_berry`).
3. Ensure the matching conversation, drop table, and cooldown timer IDs exist
   in `conversationlist_foraging.json` and `droplist_foraging.json`.

---

## 6. Keys_crafting — crafting stations

All crafting objects are `interactable` type.  The engine checks `guildRestriction`
and shows only the recipes the player is qualified for.

### Crafting station reference

| Object name | conversationId | guildRestriction | Products |
|-------------|---------------|-----------------|---------|
| `WritingDesk` | `crafting_scroll_start` | mage, cleric, druid | Spell / prayer scrolls |
| `BrewingCauldron` | `crafting_potion_start` | mage, cleric, druid | Potions (minor and greater) |
| `Forge` | `crafting_forge_start` | fighter | Weapons, armour, shields |
| `CookingFire` | `crafting_cooking_start` | *(open)* | Meals, dried herbs, smoked fish |
| `Loom` | `crafting_loom_start` | *(open)* | Cloth bolts, clothing, bandages |
| `AlchemyTable` | `crafting_alchemy_start` | mage, druid | Elixirs, transmutation potions |
| `JewellerBench` | `crafting_jeweller_start` | *(open)* | Rings, amulets, gem-set items |

### Guild restriction values

Set `guildRestriction` to a comma-separated list of guild IDs, or leave it empty
for no restriction.

| Guild ID | Class |
|----------|-------|
| `mage` | Mage |
| `cleric` | Cleric |
| `druid` | Druid |
| `fighter` | Fighter |
| `thief` | Thief |
| `ranger` | Ranger |

---

## 7. Keys_mining — mining node system

Mining nodes work identically to forage nodes.  The player must have the correct
pickaxe **equipped** (not just in the inventory) for the tier.

### Mining tier reference

| Object name | monsterType id | conversationId | Pickaxe required | Key drops |
|-------------|---------------|----------------|-----------------|-----------|
| `mine_low` | `fm_node_mine_low` | `fm_mine_low_strike` | `fm_pickaxe_wood` (or better) | Pebble, stone, copper ore, tin ore, quartz |
| `mine_mid` | `fm_node_mine_mid` | `fm_mine_mid_strike` | `fm_pickaxe_iron` (or better) | Stone, copper/tin/iron ore, silver, quartz, amethyst |
| `mine_high` | `fm_node_mine_high` | `fm_mine_high_strike` | `fm_pickaxe_steel` | Stone, iron/silver/gold/platinum ore, crystals |
| `mine_gem` | `fm_node_mine_gem` | `fm_mine_gem_strike` | `fm_pickaxe_steel` | Stone, quartz, amethyst, obsidian, topaz, emerald, sapphire, ruby, diamond |

### Pickaxe items

| itemID | Name | Tiers usable |
|--------|------|-------------|
| `fm_pickaxe_wood` | Wooden pickaxe | low only |
| `fm_pickaxe_iron` | Iron pickaxe | low, mid |
| `fm_pickaxe_steel` | Steel pickaxe | all tiers |

All mining nodes share a **3456 second** (≈ 57 min) cooldown timer.

---

## 8. Replace_newyears — holiday event layer group

The `Replace_newyears` objectgroup is the engine signal for a holiday event.
During the active window (Dec 31 – Jan 1) the engine:

1. Sets the map title to **New Year Celebration** and plays `music_newyears_festival`.
2. Swaps `Ground_replace`, `Objects_replace`, and `Above_replace` tile layers in,
   covering the base layers with seasonal decoration art.
3. Activates the `Spawn_replace` objectgroup, spawning the New Years Baby NPC.

### Key properties

| Property | Value | Meaning |
|----------|-------|---------|
| `holidayID` | `newyears` | Links to engine holiday calendar |
| `eventStartOffset` | `-1` | Activate 1 day before Jan 1 (Dec 31) |
| `eventEndOffset` | `1` | Deactivate 1 day after Jan 1 |
| `musicID` | `music_newyears_festival` | Seasonal music track |
| `ambientLightOnEnter` | `255` | Full brightness (festive lighting) |

### How to add another holiday event

1. Duplicate the `Replace_newyears` layer and rename it (e.g. `Replace_halloween`).
2. Change `holidayID` and `eventStartOffset` / `eventEndOffset`.
3. Paint the `_replace` tile layers with the new seasonal art.
4. Add an NPC to `Spawn_replace` or leave it empty.

---

## 9. New Years Baby NPC

**monsterlist_newyears.json** — add this file to `loadresources.xml`:

```xml
<monsterlist filename="res/raw/monsterlist_newyears.json"/>
```

**conversationlist_newyears.json** — add this file to `loadresources.xml`:

```xml
<conversationlist filename="res/raw/conversationlist_newyears.json"/>
```

### NPC stats

| Field | Value |
|-------|-------|
| id | `npc_new_years_baby` |
| name | Baby New Year |
| iconID | `ic_npc_human_child` |
| maxHP | 5 |
| faction | friendly |
| spawnGroup | `spawngroup_newyears_npc` |
| conversationID | `conv_npc_new_years_baby` |
| spawnRespawnTimer | 86400 s (24 h) |

### Conversation tree

```
conv_npc_new_years_baby
├── "Happy New Year, little one!"
│   └── → node_happy  →  grants ac_newyears_blessing
├── "What are you doing here?"
│   └── → node_explain
│       └── "Of course — Happy New Year!"  →  node_happy
└── "Goodbye."
```

The actor condition `ac_newyears_blessing` must be defined in an
`actorconditions_*.json` file loaded before the conversation runs.

---

## 10. Checklist before use

- [ ] Replace every `REPLACE_MAP_NORTH/SOUTH/EAST/WEST` in Mapevents
- [ ] Replace `REPLACE_MAP_*` and `REPLACE_INNER_MAP` in Keys_door
- [ ] Replace `REPLACE_KEY_ID` with the actual key item ID for each door
- [ ] Paint Ground / Objects / Above tile layers with real art
- [ ] Paint Ground_replace / Objects_replace / Above_replace for New Year holiday
- [ ] Add `monsterlist_newyears.json` to `loadresources.xml`
- [ ] Add `conversationlist_newyears.json` to `loadresources.xml`
- [ ] Define `ac_newyears_blessing` actor condition
- [ ] Add `crafting_forge_start`, `crafting_cooking_start`, `crafting_loom_start`,
      `crafting_alchemy_start`, `crafting_jeweller_start` conversations if using
      those crafting stations
- [ ] Rename the map file (e.g. `level_0_mymap_x0_y0.tmx`) and register it
      in the appropriate `*_maps.json` and `*_connections.json` files
