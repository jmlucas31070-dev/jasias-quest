# Jasias-Quest: Party System Addon -- Developer README

## Overview
This addon adds a full party system, 20 pubs with unique recruitable NPCs,
an Adventurers Guild, five specialty guilds, 24 standard quests plus one 6-part
epic quest, spell scrolls as ring-slot equipment, guild recall scrolls, a cleric
shop, a mage scroll shop, and a trophy case to jasias-quest.

## File Structure

  res/values/loadresources.xml  -- Merge into existing (registers all new JSON/TMX resources)
  res/values/strings.xml        -- Merge into existing (all addon string resources)
  res/xml/worldmap.xml          -- Merge into existing (new map connections)
  res/xml/jq_adventurers_guild.tmx
  res/xml/jq_fighter_guild.tmx
  res/xml/jq_thief_guild.tmx
  res/xml/jq_mage_guild.tmx
  res/xml/jq_cleric_guild.tmx
  res/xml/jq_druid_guild.tmx
  res/xml/jq_pub_01.tmx ... res/xml/jq_pub_20.tmx
  res/raw/jq_party_actors.json        -- All NPCs (200 party members + guild/pub staff)
  res/raw/jq_party_items.json         -- Scrolls (spell + recall) and potions
  res/raw/jq_party_quests.json        -- 24 standard quests + 1 epic 6-part quest
  res/raw/jq_party_conversations.json -- All NPC dialogue trees
  res/raw/jq_party_areas.json         -- Area definitions for maps
  res/raw/jq_party_system.json        -- Party and guild system configuration

## Integration Steps

### 1. Copy Files
- Copy all res/raw/*.json files into your project res/raw/
- Copy all res/xml/jq_*.tmx files into your project res/xml/
- MERGE (not replace) res/values/loadresources.xml entries into your existing file
- MERGE (not replace) res/values/strings.xml entries into your existing file
- MERGE (not replace) res/xml/worldmap.xml area entries into your existing file

### 2. Tile Layer Data
The TMX files use CSV tile encoding with AT-indoors tileset.
Tile IDs:
  1  = stone floor
  17 = door
  36 = top-left corner wall
  37 = top horizontal wall
  38 = top-right corner wall
  52 = bottom-left corner wall
  53 = vertical wall (left/right edges)
  54 = bottom-right corner wall

If these IDs differ from your at_indoors.png, open TMX files in Tiled and remap.
The NPC spawn object layer is unaffected by tile remapping.

### 3. Map Connections
Update targetX/targetY in worldmap.xml adjacentmap entries to match your world map.
The stubs use jq_worldarea_01 as a placeholder -- replace with real area IDs.

### 4. Party System Engine (Engine-Level Changes Required)
jq_party_system.json defines rules. The engine must implement:

Party tracking:
- Array of up to 3 party member slots (actor IDs + join order)
- Persistent save/load of party state

Combat HP monitoring:
- After each combat hit, check player HP percentage
- At 30%: kill party slot 3 (most recently joined), heal player by 50% of that member maxHP
- At 15%: kill party slot 2, heal player similarly
- At 1%:  kill party slot 1 (first joined, last to die), heal player similarly

Party bonuses (per living member):
- +5 max HP
- +1 attack bonus
- +1 defense bonus
- +5% XP per member

Disband/dismiss UI:
- Accessible from party menu anywhere in the world
- On dismiss: set NPC location to their home pub spawn point
- On disband all: return all members to their home pubs

### 5. Scroll Equipment System
Scrolls use equipSlot: "ring" -- they occupy a ring slot.
- Track currentUses per equipped scroll instance
- Display charges in equipment UI using jq_scroll_charges_remaining string
- On each use: decrement currentUses
- When currentUses reaches 0: destroy item, show jq_scroll_depleted message

Recall scroll validation:
- On use: check player guild membership against requiresGuildMembership field
- If not a member: deal failDamage (10) HP, show failMessage
- If member: teleport to targetMap at targetX/targetY

### 6. Guild System
- mutuallyExclusive guilds: Fighter, Thief, Mage, Cleric, Druid
- Player may only belong to ONE of these at a time
- Adventurers Guild can be combined with any one specialty guild
- On leaving: set benefit multiplier to 0.5 for that guild rank bonuses
- On rejoining: restore multiplier to 1.0
- Guild rank/level is always stored persistently

### 7. Trophy Case
- Default text: jq_trophy_text_default string
- After epic quest completion (all 6 parts of jq_quest_epic done):
  show jq_trophy_text_player with %1$s = player name, %2$s = comma-joined party names

## Maps Added

  jq_pub_01 through jq_pub_20     20 pub interiors (10 unique party NPCs each)
  jq_adventurers_guild            Main guild hub: guildmaster, cleric, mage, scribe, trophy
  jq_fighter_guild                Fighter Guild hall
  jq_thief_guild                  Thief Guild hall
  jq_mage_guild                   Mage Guild hall
  jq_cleric_guild                 Cleric Guild hall
  jq_druid_guild                  Druid Guild hall

## Quest Summary

Standard Quests (24):
  01 Lost Merchant Escort           120 XP  40g  (party recommended)
  02 The Goblin Warrens             150 XP  50g  (party recommended)
  03 Missing Shipment               100 XP  35g
  04 The Haunted Mill               130 XP  45g  (party recommended)
  05 Wolf Pack Terror               110 XP  38g  (party recommended)
  06 Tomb of the Forgotten King     200 XP  80g  (party recommended)
  07 The Poisoned Well              120 XP  42g
  08 Brigand Camp Assault           160 XP  60g  (party recommended)
  09 The Alchemists Ingredients      90 XP  30g
  10 Siege at Fort Thornwall        220 XP  90g  (party recommended)
  11 The Cursed Idol                140 XP  55g  (party recommended)
  12 Bounty The Scarred Raider      180 XP  70g  (party recommended)
  13 Library of Lost Knowledge      100 XP  35g
  14 The Collapsing Mine            130 XP  48g  (party recommended)
  15 Night of the Undead            190 XP  75g  (party recommended)
  16 The Dragons Tithe              250 XP 100g  (party recommended)
  17 Smugglers Cove                 140 XP  52g  (party recommended)
  18 The Stolen Heir                170 XP  65g  (party recommended)
  19 Plague Rat Infestation         120 XP  40g
  20 The Oath-Breaker               160 XP  60g  (party recommended)
  21 Ruins of Old Vareth            200 XP  80g  (party recommended)
  22 The Witch of Blackwood         180 XP  70g  (party recommended)
  23 Tavern Troubles                 80 XP  25g
  24 The Arcane Anomaly             210 XP  85g  (party recommended)

Epic Quest: The Legend of the Companions (6 parts, ~4050 XP total, 1750g total)
  Part 1: The Prophecy Discovered    300 XP    0g
  Part 2: Gathering the Heroes       350 XP  100g
  Part 3: The Three Seals            500 XP  200g
  Part 4: The Betrayal at Ashgate    600 XP  150g
  Part 5: Siege of the Dark Spire    800 XP  300g
  Part 6: The Final Reckoning       1500 XP 1000g  + legendary medal + trophy update

## NPC Count
- 200 unique party members (10 per pub x 20 pubs), no respawn
- 40 pub staff (innkeeper + barkeep per pub), respawns
- 4 Adventurers Guild staff, respawns
- 15 specialty guild staff (guildmaster + trainer + scribe x 5), respawns
- Total: 259 new actors
