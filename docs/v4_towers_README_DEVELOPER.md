# Mage Tower Quest — Developer README

## Overview
This expansion adds the Nine Mage Tower quest chain to Jasias Quest (Andor's Trail fork).
Nine towers, each with 4 combat floors + 1 boss floor, yield a colored crystal. A 10th tower
(the Tower of Convergence) is where all nine crystals unlock the grand reward.
Additionally: 9 unique outside quest-giver mages, 24 world NPCs, and 9 side quests.

---

## File Manifest

### res/values/
- **loadresources.xml** — MERGE entries into your existing file
- **strings.xml** — MERGE string entries into your existing file

### res/xml/
- **worldmap.xml** — MERGE map/area entries into your existing worldmap.xml
- **tower_01_exterior.tmx … tower_09_exterior.tmx** — Exterior areas (with quest NPC)
- **tower_01_floor_01.tmx … tower_09_floor_05.tmx** — 45 combat floor maps (9 towers × 5 floors)
- **tower_10_exterior.tmx** — Convergence tower exterior
- **tower_10_floor_01.tmx … tower_10_floor_05.tmx** — Convergence tower floors

### res/raw/
- **monsterlist_magetowers.json** — All mage NPCs (floor mages, bosses, quest givers, world NPCs)
- **conversations_magetowers.json** — All dialogue
- **scripts_magetower_quests.json** — 9 main quests + 9 side quests + 1 convergence quest
- **items_magetowers.json** — 9 crystals + Prism of Unity + side quest items
- **droplists_magetowers.json** — Drop tables for all tower mages

---

## Tower Architecture

Each tower (1–9) has:
```
tower_XX_exterior.tmx       — Outside area; quest-giver NPC stands here
tower_XX_floor_01.tmx       — Floor 1: Apprentice Mages  (5 mages)
tower_XX_floor_02.tmx       — Floor 2: Journeyman Mages  (6 mages)
tower_XX_floor_03.tmx       — Floor 3: Adept Mages        (7 mages)
tower_XX_floor_04.tmx       — Floor 4: Sentinel Mages     (8 mages)
tower_XX_floor_05.tmx       — Top: Grand Archmage (boss), drops colored crystal
```

Difficulty scales in two dimensions:
- **Tower number** (1 = easiest, 9 = hardest) — HP, damage, resistance all scale
- **Floor number** (1 = bottom, 4 = hardest before boss) — stats increase per floor

Tower 10 (Convergence) has no combat:
```
tower_10_exterior.tmx       — Exterior
tower_10_floor_01.tmx       — 5 friendly mages with random philosophical quotes
tower_10_floor_02.tmx       — 5 friendly mages with random quotes
tower_10_floor_03.tmx       — 5 friendly mages with random quotes
tower_10_floor_04.tmx       — 5 friendly mages with random quotes
tower_10_floor_05.tmx       — Crystal Altar Chamber: place all 9 crystals for grand reward
```

---

## Tower Themes & Crystals
| # | Tower Name       | Crystal           | Theme     |
|---|-----------------|-------------------|-----------|
| 1 | Ruby Tower       | Red Crystal       | Fire      |
| 2 | Amber Tower      | Orange Crystal    | Earth     |
| 3 | Solar Tower      | Yellow Crystal    | Lightning |
| 4 | Emerald Tower    | Green Crystal     | Nature    |
| 5 | Sapphire Tower   | Blue Crystal      | Water     |
| 6 | Mystic Tower     | Indigo Crystal    | Void      |
| 7 | Amethyst Tower   | Violet Crystal    | Shadow    |
| 8 | Ivory Tower      | White Crystal     | Holy      |
| 9 | Obsidian Tower   | Black Crystal     | Death     |

---

## Quest Structure

**Main quest per tower:** `quest_tower{N}_main`
- 4 floor-clearing steps + 1 boss kill + 1 crystal collection
- Completion triggers crystal drop and updates world NPC dialogue

**Side quest per outside mage:** `quest_tower{N}_side`
- One-step collection or kill quest, thematically related to the tower
- Reward: exp + gold, no crystal

**Convergence quest:** `quest_convergence_main`
- 9 collection steps (one per crystal) + 1 altar delivery step
- Reward: 5000 EXP, 2000 gold, Prism of Unity item

---

## NPC Placement Guide

**Outside Mage NPCs** (one per tower exterior):
Place each in the exterior .tmx map at position x=480, y=480 (already in spawn data).

| NPC ID                 | Name                | Tower             |
|------------------------|---------------------|-------------------|
| npc_tower1_questgiver  | Aldric Ashbane      | Ruby Tower        |
| npc_tower2_questgiver  | Faeyra Frostwhisper | Amber Tower       |
| npc_tower3_questgiver  | Gwynar Grimspell    | Solar Tower       |
| npc_tower4_questgiver  | Celindra Coldweave  | Emerald Tower     |
| npc_tower5_questgiver  | Brennus Blazemark   | Sapphire Tower    |
| npc_tower6_questgiver  | Hexara Hexbound     | Mystic Tower      |
| npc_tower7_questgiver  | Sylvan Stormcaller  | Amethyst Tower    |
| npc_tower8_questgiver  | Thyra Thornweave    | Ivory Tower       |
| npc_tower9_questgiver  | Dravos Duskmantle   | Obsidian Tower    |

**World NPCs** (24 total, IDs: npc_world_questgiver_01 to npc_world_questgiver_24):
Place these in any existing world map to help players discover the quest chain.
They have dialogue for both quest introduction and progress updates.

---

## TMX Tile Notes
- All TMX files use `tileset_dungeon2` as the primary tileset
- Ground tile values 1–11 correspond to different floor themes (fire=3, earth=2, etc.)
- You MUST paint the maps in Tiled Map Editor — tile data is placeholder
- Icon IDs follow the convention: `ic_npc_mage_{theme}_{gender}` — add drawables
- Crystal items need icons: `ic_item_crystal_{theme}`

## Engine Requirements
- `isUnique: true` with boss NPCs prevents them from respawning on kill (standard AT behavior)
- `spawnRespawnTimer: 604800` on bosses = 7-day respawn for the boss fight to be repeatable
- The altar interaction uses `type: "questTrigger"` event on tower_10_floor_05.tmx
- The `hasAllItems` conversation condition checks for all 9 crystals simultaneously
