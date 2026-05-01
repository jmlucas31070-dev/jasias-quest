# Jasias Quest: The Faction Wars — Developer README

## Overview

This expansion adds a comprehensive faction warfare system to Jasias Quest (Andor's Trail fork).
It introduces 14 player-affecting factions, 1,400 unique NPCs, seasonal holiday events,
guild-based stealth abilities, and a grand tournament system.

## Files Changed / Added

### res/values/
- **loadresources.xml** — ADD entries from this file to your existing loadresources.xml (do not replace)
- **strings.xml** — ADD string entries from this file to your existing strings.xml

### res/xml/
- **worldmap.xml** — ADD map entries from this file to your existing worldmap.xml
- **template_spawn.tmx** — NEW: Faction spawn demonstration map
- **template_faction_{race}.tmx** (×14) — NEW: Headquarters maps for each race
- **template_holiday_{event}.tmx** (×4) — NEW: Easter, July4th, Halloween, Christmas festival maps
- **template_event_{name}.tmx** (×4) — NEW: Generic event maps (spring_fair, harvest_moon, etc.)
- **template_battlefield.tmx** — NEW: Grand Faction Tournament arena

### res/raw/
- **monsterlist_{race}.json** (×14) — NEW: 100 unique NPCs + leader + elder per race
- **factions.json** — NEW: Faction definitions and base reputation scores
- **conversations_factions.json** — NEW: All NPC dialogue, quest hooks, holiday conversations
- **scripts_faction_quests.json** — NEW: 168 faction quests + holiday quests + tournament quest
- **items_faction.json** — NEW: Cloak of Invisibility, Champion's Medallion, holiday items, etc.
- **droplists_faction.json** — NEW: Drop tables for all faction NPCs
- **abilities_faction.json** — NEW: Hide ability, Invisibility spells (mage/cleric/druid)

## Story Layout

The expansion centers on the FACTION WARS — an era of rising tensions among the world's
14 major races. The player, a Wood Elf, must navigate these conflicts through diplomacy,
combat, and cunning.

### Key Locations
1. **Faction Spawn Grounds** — Where faction NPCs roam based on their 48-hour spawn cycle
2. **14 Faction Headquarters** — Each race has a stronghold with a Leader (quests) and Elder (rep trading)
3. **Grand Faction Battlefield** — Round-robin tournament arena with 13 champion fights
4. **Festival Grounds** (×4) — Holiday areas with seasonal decorations and events

### NPC Architecture
- **100 unique NPCs per race** (isUnique: true) — they don't respawn when killed
- **spawnRespawnTimer: 172800** (48 hours) — their SPAWN POINT resets after 48 hours
- **1 Faction Leader per race** — offers 12 quests, respawn: 604800 (7 days)
- **1 Elder per race** — sells faction reputation changes for gold

### Faction Quests (12 per race = 168 total)
- Quests 1–6 per race: RAISE that race's faction score (+10 each = +60 total)
- Quests 7–12 per race: LOWER that race's faction score (-10 each = -60 total)
- **Design Intent**: A player who completes ALL quests ends up at net 0 change per faction
  (balanced). Players choose which quests to prioritize based on their alliance goals.

### Faction Aggression System
Implemented via factions.json aggressionThreshold values:
- If player's score with a faction falls below aggressionThreshold, NPCs of that race attack on sight
- Default hostile factions for Wood Elf: Drow (-30), Goblins (-50), Hobgoblins (-40), Orcs (-60), Ogres (-70), Dragons (-80)
- The faction aggression check runs on every map with `type="factionAggression"` event triggers

### Stealth System
Three ways to bypass faction aggression:
1. **Thief: Hide in Shadow** — Toggle ability. Requires guild membership + Cloak of Shadows item
2. **Cloak of Invisibility** — Wearable item (no guild required)
3. **Mage/Cleric/Druid: Invisibility spells** — Require guild membership + appropriate spell
All methods: `cancelOn: "combatStart"` (stealth breaks when a fight starts)

### Holiday Event System
Maps use event triggers with these properties:
- `holidayID` — Links to the event calendar
- `eventStartOffset: "-7"` — Event starts 7 days BEFORE the holiday
- `eventEndOffset: "7"` — Event ends 7 days AFTER the holiday
- `layerSwapObjects` / `layerSwapAbove` — Names of alternate layer sets for seasonal decoration
- `monsterSpawnEvent` — Triggers seasonal monster spawns when event is active

The game engine should check if today's date falls within the event window and:
1. Load the holiday map's alternate Objects/Above tile layers
2. Enable the holiday NPC spawns
3. Make holiday quests available (checked via `dayOffset` in scripts)

## Integration Notes
- All IDs follow the pattern `{type}_{race}_{index}` for consistency
- Icon IDs use the convention `ic_npc_{race}_{gender}` — add matching drawables to res/drawable/
- The faction score is stored as a player script flag: `faction_{race}_score`
- Tournament champion NPCs need to be added to their respective race's monsterlist

## Known Limitations / TODOs
- Tile data in .tmx files uses placeholder tile IDs (all tile 1 = base grass)
  → You will need to paint the maps in Tiled map editor with actual tileset tiles
- Icon resources (drawables) for new NPCs are referenced but not included — add your own sprites
- The engine must support `isUnique: true` + `spawnRespawnTimer` simultaneously
  (unique = don't respawn on kill, but the spawn point becomes available again after 48h)
