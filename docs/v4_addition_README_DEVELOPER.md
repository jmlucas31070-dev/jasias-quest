# Jasias Quest — Grand Addition Pack
## Developer README

---

## Overview

This addition pack expands jasias-quest with:

- **10 Libraries** with Scholar NPCs who teach crafting skills
- **5 Guild Systems** (Fighter, Thief, Mage, Cleric, Druid) with tiered rank progression and persistent skills
- **7 Crafting Skills** (Foraging, Mining, Cooking, Sewing, Gardening, Weapon Forging, Armor Forging)
- **200 Pickpocketable Townspeople** spread across existing maps
- **Full Crafting System** with recipes for weapons, armor, cloth, food, potions, scrolls, wands, and staffs
- **Wands and Staffs** for all player-craftable spells
- **Recall Scrolls** for Mage, Cleric, Druid, and Adventurer's guilds
- **Home Furnishings** system (computer, game console, writing desk, cauldron, wand/staff crafting tables)
- **Astral Beast World** logout matching the MUD logout procedure
- **Template maps** for loot houses and crafting rooms

---

## File Structure

```
res/
  values/
    loadresources.xml     ← Merge into existing loadresources.xml
    strings.xml           ← Merge into existing strings.xml
  xml/
    worldmap_addition.xml ← Merge <map> entries into existing worldmap.xml
    jqa_library_01.tmx    ← Drop all .tmx files into res/xml/
    jqa_library_02.tmx
    ... (18 total TMX files)
  raw/
    jqa_addition_items.json
    jqa_skills.json
    jqa_scholars.json
    jqa_guilds.json
    jqa_shops.json
    jqa_crafting.json
    jqa_loot_tables.json
    jqa_maps.json
    jqa_placements.json
    jqa_connections.json
    jqa_townspeople.json
    jqa_home_furnishings.json
    jqa_astral_logout.json
    jqa_quests.json
```

---

## Installation Instructions

1. **Copy all `.json` files** from `res/raw/` into `AndorsTrail/res/raw/`
2. **Copy all `.tmx` files** from `res/xml/` into `AndorsTrail/res/xml/`
3. **Merge `loadresources.xml`**: open the existing `res/values/loadresources.xml` and add the `<resource>`, `<map>`, `<skill>`, `<npc>`, `<shop>`, and `<guild>` entries from this pack's `loadresources.xml`
4. **Merge `strings.xml`**: open the existing `res/values/strings.xml` and add all `<string>` entries from this pack's `strings.xml`
5. **Merge `worldmap_addition.xml`**: open `res/xml/worldmap.xml` and add the 18 `<map>` entries from `worldmap_addition.xml` before the closing `</worldmap>` tag

---

## Map Changes & Story Layout

### New Region: Scholar's Quarter (worldmap x=500–670)
All new maps are placed at x=500 and above in the worldmap to avoid conflicts with existing jasias-quest maps.

**Libraries** (x=500–650, y=0–55):
- Accessed from existing jq_harbor and jq_plains_center via new door connections defined in jqa_connections.json
- Each library contains a Scholar NPC at a desk, two searchable bookshelves, and a shop offering skill manuals and related crafting materials

**Guild Halls** (x=500–665, y=60):
- Fighter's Guild: accessed from jq_harbor. Contains guildmaster, armory shop, training dummies (decorative objects)
- Thieves' Guild: hidden entrance from jq_harbor. Dark interior, wanted posters, guildmaster at back
- Mage's Guild: tower entrance at jq_harbor. Arcane shop, bookshelves, potion stands
- Cleric's Guild: holy hall with altar. Sacred shop, prayer area
- Druid's Grove: open-roofed hall of living trees. Nature shop, grove pool

**Template Maps** (x=500–565, y=95):
- `jqa_template_loot_house` — standard home usable for lootable NPC houses
- `jqa_template_loot_house_wealthy` — larger wealthy home with better loot
- `jqa_template_crafting_room` — contains forge, sewing table, cooking fire, writing desk, heavy cauldron, wand crafting table, staff crafting table

---

## Mechanic Details

### Crafting Skills (Taught by Scholars)
Skills have 3 ranks each. Players buy skill manuals from the library shop or pay the scholar directly. Skills gate crafting recipes.

### Guild Skill Persistence
Fighter and Thief guild skills (`jqa_skill_fighter_*`, `jqa_skill_thief_*`) are flagged `"persistent": true`. Once learned, they remain in the player's skill list even if they join a different guild. Implement this by checking the `persistent` field in the skill JSON during guild change events.

### Backstab Mechanic
On backstab, calculate `player.maxHP` as the damage. If this kills the target (`target.hp <= 0`), skip combat and drop the monster's loot table directly. Otherwise start combat with the enemy already damaged.

### Thief Use Magic Items
Gate the use of `jqa_scroll_*`, `jqa_wand_*`, and `jqa_potion_*` items by checking if the player has `jqa_skill_thief_use_magic` OR belongs to mage/cleric/druid guild. The skill allows thieves to bypass the guild check.

### 200 Townspeople
All defined in `jqa_townspeople.json`. Each has `"pickpocketable": true` and a `pickpocketLoot` array. Attempting to steal requires `jqa_skill_thief_steal`. Failure triggers an "alert" flag on the NPC and they will no longer trade with the player.

### Home Furnishings
- 1-room+ homes: can purchase computer and game console (mimics objects in home.tmx)
- 4-room homes: additionally can purchase writing desk, heavy cauldron, wand crafting table, staff crafting table
- Placed furnishings function as crafting stations (same interactions as guild/library stations)

### Astral Beast World Logout
The astral logout matches MUD behavior: player must interact with `jqa_astral_gate_keeper` NPC to safely exit. Unsafe exit (app close) applies a 10% XP penalty on next login. Gate is locked during combat.

### Recall Scrolls
Teleport the player to the target mapId using the existing teleport mechanism. Mage/cleric/druid can craft their own guild's recall scroll at a writing desk. Recall scroll for Adventurer's Guild is available at the Adventurer's Guild shop and craftable by any scribe-skilled character.

---

## NPC IDs Reference

| ID | Name | Location |
|----|------|----------|
| jqa_scholar_01 | Scholar Aldwin | Library 01 — Foraging |
| jqa_scholar_02 | Scholar Berta | Library 02 — Mining |
| jqa_scholar_03 | Scholar Corvin | Library 03 — Cooking |
| jqa_scholar_04 | Scholar Delia | Library 04 — Sewing |
| jqa_scholar_05 | Scholar Emeric | Library 05 — Gardening |
| jqa_scholar_06 | Scholar Fara | Library 06 — Weapon Forging |
| jqa_scholar_07 | Scholar Gorm | Library 07 — Armor Forging |
| jqa_scholar_08 | Scholar Hilde | Grand Library 08 — Nature |
| jqa_scholar_09 | Scholar Ivar | Grand Library 09 — Smith |
| jqa_scholar_10 | Scholar Jona | Grand Library 10 — Home |
| jqa_fighter_guildmaster | Guildmaster Brogan | Fighter's Guild Hall |
| jqa_thief_guildmaster | Shadowmaster Vex | Thieves' Guild Den |
| jqa_mage_guildmaster | Archmage Seraphel | Mage's Guild Hall |
| jqa_cleric_guildmaster | High Priest Aldric | Cleric's Guild Hall |
| jqa_druid_guildmaster | Elder Sylvara | Druid's Grove Hall |
| jqa_astral_gate_keeper | Astral Gate Keeper | Astral Beast World maps |
| jqa_townsperson_001 to _200 | Various names | Spread across harbor, pub, libraries, guild, bank |

---

## Crafting Station Types
| Station ID | Used For |
|------------|----------|
| forge | Weapon forging, armor forging, smelting ingots |
| sewing_table | Cloth armor crafting |
| cooking_fire | Food preparation |
| writing_desk | Scroll scribing (requires scribe skill) |
| cauldron | Potion brewing (requires brew skill) |
| wand_crafting_table | Wand creation (requires craft wand skill) |
| staff_crafting_table | Staff creation (requires craft wand skill) |

---

*This addition was built to integrate cleanly with jasias-quest without modifying any existing file content — only additions and merges.*
