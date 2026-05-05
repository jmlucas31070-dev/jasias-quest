# Jasias Quest — Resource Pack: Developer README

## Overview

This package contains all JSON data files for the `res/raw/` directory
of the [jasias-quest](https://github.com/jmlucas31070-dev/jasias-quest)
fork of Andor's Trail, along with the matching `res/values/loadresources.xml`.

The files in this package have been cleaned up to follow a consistent
naming convention: all files are prefixed with the data type they contain,
matching the Andor's Trail resource loader array names.

---

## How to Install

Copy the two folders directly into `AndorsTrail/` (the Android project root):

```
AndorsTrail/
  res/
    raw/           ← replace/merge all .json files here
    values/
      loadresources.xml   ← REPLACE (do not merge; this is the full updated version)
```

> **Note:** `loadresources.xml` is a complete replacement.
> It already contains all resource array entries updated to reflect
> the renamed files. Do **not** merge it — overwrite the existing one.

---

## What Changed

### File Renaming Convention

All JSON files in `res/raw/` now follow the pattern:

```
<type>_<pack_or_content>.json
```

Where `<type>` is one of:
| Prefix | Data type |
|---|---|
| `actorconditions_` | Actor conditions, abilities, spells, guild/skill state |
| `conversationlist_` | NPC dialogue trees and conversations |
| `droplist_` | Monster/container loot tables |
| `itemcategories_` | Item category definitions |
| `itemlist_` | Item definitions, crafting recipes, shop inventories |
| `monsterlist_` | Monster/NPC definitions |
| `questlist_` | Quest and script definitions |

### Renamed Files (89 total)

Below is the complete rename log. Files not listed were already
correctly named and were left unchanged.

| Old name | New name |
|---|---|
| `ab_actorconditions.json` | `actorconditions_ab.json` |
| `ab_conversationlists.json` | `conversationlist_ab.json` |
| `ab_droplists.json` | `droplist_ab.json` |
| `ab_itemcategories.json` | `itemcategories_ab.json` |
| `ab_items.json` | `itemlist_ab.json` |
| `ab_monsters.json` | `monsterlist_ab.json` |
| `ab_quests.json` | `questlist_ab.json` |
| `abilities_faction.json` | `actorconditions_faction.json` |
| `castle_conversationlists.json` | `conversationlist_castle.json` |
| `castle_droplists.json` | `droplist_castle.json` |
| `castle_items.json` | `itemlist_castle.json` |
| `castle_monsters.json` | `monsterlist_castle.json` |
| `castle_quests.json` | `questlist_castle.json` |
| `conversations_crafting.json` | `conversationlist_crafting.json` |
| `conversations_door.json` | `conversationlist_door.json` |
| `conversations_factions.json` | `conversationlist_factions.json` |
| `conversations_magetowers.json` | `conversationlist_magetowers.json` |
| `conversations_trainers.json` | `conversationlist_trainers.json` |
| `droplists_debug.json` | `droplist_debug.json` |
| `droplists_faction.json` | `droplist_faction.json` |
| `droplists_foraging.json` | `droplist_foraging.json` |
| `droplists_magetowers.json` | `droplist_magetowers.json` |
| `droplists_mining.json` | `droplist_mining.json` |
| `droplists_regions.json` | `droplist_regions.json` |
| `factions.json` | `actorconditions_factions.json` |
| `items_faction.json` | `itemlist_faction.json` |
| `items_magetowers.json` | `itemlist_magetowers.json` |
| `jq_actorconditions.json` | `actorconditions_jq.json` |
| `jq_actors.json` | `monsterlist_jq_actors.json` |
| `jq_bank_actorconditions.json` | `actorconditions_jq_bank.json` |
| `jq_bank_conversationlists.json` | `conversationlist_jq_bank.json` |
| `jq_bank_droplists.json` | `droplist_jq_bank.json` |
| `jq_bank_itemcategories.json` | `itemcategories_jq_bank.json` |
| `jq_bank_items.json` | `itemlist_jq_bank.json` |
| `jq_bank_monsters.json` | `monsterlist_jq_bank.json` |
| `jq_bank_quests.json` | `questlist_jq_bank.json` |
| `jq_conversationlists.json` | `conversationlist_jq.json` |
| `jq_droplists.json` | `droplist_jq.json` |
| `jq_inns.json` | `conversationlist_jq_inns.json` |
| `jq_itemcategories.json` | `itemcategories_jq.json` |
| `jq_items.json` | `itemlist_jq.json` |
| `jq_items2.json` | `itemlist_jq2.json` |
| `jq_monsters.json` | `monsterlist_jq.json` |
| `jq_mud_logout.json` | `conversationlist_jq_mud_logout.json` |
| `jq_npcs.json` | `monsterlist_jq_npcs.json` |
| `jq_party_actors.json` | `monsterlist_jq_party.json` |
| `jq_party_conversations.json` | `conversationlist_jq_party.json` |
| `jq_party_items.json` | `itemlist_jq_party.json` |
| `jq_party_quests.json` | `questlist_jq_party.json` |
| `jq_party_system.json` | `actorconditions_jq_party_system.json` |
| `jq_quests.json` | `questlist_jq.json` |
| `jq_quests2.json` | `questlist_jq2.json` |
| `jq_shops.json` | `itemlist_jq_shops.json` |
| `jq_spells.json` | `actorconditions_jq_spells.json` |
| `jqa_addition_items.json` | `itemlist_jqa_addition.json` |
| `jqa_astral_logout.json` | `conversationlist_jqa_astral_logout.json` |
| `jqa_crafting.json` | `itemlist_jqa_crafting.json` |
| `jqa_guilds.json` | `actorconditions_jqa_guilds.json` |
| `jqa_home_furnishings.json` | `actorconditions_jqa_guilds.json` |
| `jqa_home_furnishings.json` | `itemlist_jqa_furnishings.json` |
| `jqa_loot_tables.json` | `droplist_jqa.json` |
| `jqa_quests.json` | `questlist_jqa.json` |
| `jqa_scholars.json` | `monsterlist_jqa_scholars.json` |
| `jqa_shops.json` | `itemlist_jqa_shops.json` |
| `jqa_skills.json` | `actorconditions_jqa_skills.json` |
| `jqa_townspeople.json` | `monsterlist_jqa_townspeople.json` |
| `scripts_faction_quests.json` | `questlist_faction.json` |
| `scripts_magetower_quests.json` | `questlist_magetowers.json` |
| `westgate_conversationlists.json` | `conversationlist_westgate.json` |
| `westgate_cooking.json` | `itemlist_westgate_cooking.json` |
| `westgate_droplists.json` | `droplist_westgate.json` |
| `westgate_forge.json` | `itemlist_westgate_forge.json` |
| `westgate_garden.json` | `itemlist_westgate_garden.json` |
| `westgate_items.json` | `itemlist_westgate.json` |
| `westgate_monsters.json` | `monsterlist_westgate.json` |
| `westgate_quests.json` | `questlist_westgate.json` |

### Files Left Unchanged (original names kept)

The following files are custom engine extension types with no
equivalent in the 7 standard AT data-type prefixes.
They are loaded via `<resource type="json" file="..."/>` in
`loadresources.xml` and work correctly with their original names:

| File | Reason kept |
|---|---|
| `ab_maps.json` | Map area definitions (Astral Beasts) |
| `castle_maps.json` | Map area definitions (Castle) |
| `jq_bank_maps.json` | Map area definitions (Bank) |
| `jqa_maps.json` | Map area definitions (JQA pack) |
| `jq_maps.json` | Map area definitions (core JQ) |
| `jq_maps2.json` | Map area definitions (core JQ, extended) |
| `westgate_maps.json` | Map area definitions (Westgate) |
| `jq_connections.json` | Area connection data (custom engine type) |
| `jqa_connections.json` | Area connection data (JQA pack) |
| `jq_placements.json` | NPC/item placement data |
| `jqa_placements.json` | NPC/item placement data (JQA pack) |
| `jq_search_areas.json` | Search area definitions |
| `jq_party_areas.json` | Party area data |
| `jq_computer.json` | Computer minigame data |

### Files That Were Already Correctly Named

42 files already matched the required naming convention and were
not modified:
`actorconditions_cleric`, `actorconditions_debug`, `actorconditions_druid`,
`actorconditions_guilds`, `actorconditions_mage`,
`conversationlist_debug`, `conversationlist_foraging`,
`conversationlist_guilds`, `conversationlist_mining`,
`itemcategories_1`, `itemcategories_foraging`, `itemcategories_guilds`,
`itemlist_crafted`, `itemlist_debug`, `itemlist_forage`,
`itemlist_foraging`, `itemlist_guilds`, `itemlist_lockpicks`, `itemlist_mining`,
`monsterlist_animals`, `monsterlist_debug`, `monsterlist_dragon`,
`monsterlist_drowelf`, `monsterlist_dwarf`, `monsterlist_elf`,
`monsterlist_foraging`, `monsterlist_gnome`, `monsterlist_goblin`,
`monsterlist_guilds`, `monsterlist_halfelf`, `monsterlist_halfling`,
`monsterlist_hobgoblin`, `monsterlist_human`, `monsterlist_magetowers`,
`monsterlist_mining`, `monsterlist_ogre`, `monsterlist_orc`,
`monsterlist_seaelf`, `monsterlist_trainer`, `monsterlist_woodelf`,
`questlist_debug`, `questlist_guilds`

---

## Notes for Future Contributors

- When adding new JSON files, name them `<type>_<content>.json` where
  type is one of the 7 prefixes above.
- Maps files (`*_maps.json`) are a custom type; keep them named by
  content pack (e.g. `mypack_maps.json`).
- After adding files, update the appropriate `<array>` block in
  `res/values/loadresources.xml`.
