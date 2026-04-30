# Jasias Quest Expansion Pack — Developer README
## Overview
This expansion adds a large new world to jasias-quest using the Andor's Trail engine.
Main island (14 regions west→east), 8 offshore islands, plus many side areas.

## Story Layout
Harbor → Slope → Forest → Clearing → Swamp → Humpbacked Bridge → Green →
Road → Lane → Crossroads → Path → Jetty → Beach → Sea

### Branches from the main island
- Slope N: Orc Cave (3 rooms) — Grak the Warchief boss quest
- Slope S: 12-room Forest Maze → Lake (4 shore maps) → Lake Island (3 maps) — Lake Serpent quest
- Clearing N: 3×3 Plains Grid + Dark Forest (NW) + River (E) + Mountain (N) → 24-room Mine + 3-map Summit
- Swamp S: 3×3 Swamp Maze — Bog Horror quest
- Green N: Church (attic + basement) → Graveyard — Ghost Lord quest
- Road N: Town Square → Pub
- Road S: Alley → Bank, Magic Shop, Post Office
- Lane N: Market (6 stalls)
- Lane S: Adventurer's Guild (12 quests + guild blade reward)
- Crossroads N: 5-map East Road + 2-map Side Alley + Inn
- Crossroads S: City Garden (3 daily-reset plots)
- Path N: School (office, 2 classrooms, library, gym, lunchroom, play area)
- Jetty S: Dock → Storm, Coral, Ash, Phantom Isles (boat)
- Harbor: Crow, Serpent, Ember, Mist Isles (boat)
- Beach N: 3-map North Beach → 12-room Dragon Cave — Ancient Dragon quest
- Sea DOWN: Octopus Lair (requires Diving Bag helmet)

## Maps Changed in the Existing Game
- **home** — Computer object added. Apply home_jq_overlay.xml.
- **castle_sunnys_bedroom** — Computer object added. Apply castle_sunnys_bedroom_jq_overlay.xml.
- **castle_jasias_bedroom** — Computer object added. Apply castle_jasias_bedroom_jq_overlay.xml.

## Files Included
| File | Purpose |
|------|---------|
| res/values/loadresources.xml | Merge into existing loadresources.xml |
| res/values/strings.xml | Merge into existing strings.xml |
| res/xml/worldmap.xml | Merge map/connection entries into existing worldmap.xml |
| res/raw/jq_actors.json | 47 monsters/animals |
| res/raw/jq_items.json | 108 items (weapons, consumables, quest, forageables, logout device) |
| res/raw/jq_spells.json | 12 spells |
| res/raw/jq_shops.json | 21 shop definitions |
| res/raw/jq_npcs.json | 30 NPCs with greetings |
| res/raw/jq_quests.json | 48 quests |
| res/raw/jq_search_areas.json | 52 daily-reset searchable areas |
| res/raw/jq_inns.json | 9 inn room definitions |
| res/raw/jq_maps.json | Map metadata |
| res/raw/jq_connections.json | Map connection graph |
| res/raw/jq_placements.json | Actor/NPC placements per map |
| res/raw/jq_computer.json | Computer interactable object (home + castle bedrooms) |
| res/raw/jq_mud_logout.json | MUD logout teleport-menu action definition |
| res/xml/*.tmx | 182 TMX map files (blank tiles, ready to paint in Tiled) |
| res/xml/home_jq_overlay.xml | Computer overlay for Jasia's bedroom (home) |
| res/xml/castle_sunnys_bedroom_jq_overlay.xml | Computer overlay for Sunny's bedroom |
| res/xml/castle_jasias_bedroom_jq_overlay.xml | Computer overlay for Jasia's castle bedroom |
| res/xml/jq_expansion.world | Tiled world file for all JQ maps |
| res/xml/ab_existing.world | Placeholder Tiled world for existing ab_ maps |

## Installation
1. Copy all files into your jasias-quest project keeping the res/ structure.
2. Merge res/values/loadresources.xml entries into your existing loadresources.xml.
3. Merge res/values/strings.xml entries into your existing strings.xml.
4. Merge res/xml/worldmap.xml entries into your existing worldmap.xml.
   Connect jq_harbor to your existing world's harbor/start point.
5. In Tiled, paint each .tmx file with appropriate tilesets (they are blank stubs).
6. Apply the three overlay XML files to home.tmx, castle_sunnys_bedroom.tmx, and
   castle_jasias_bedroom.tmx by adding the <objectgroup> block from each overlay
   before the </map> tag.

## New Mechanics

### MUD Connection
Computer objects placed in home / castle_sunnys_bedroom / castle_jasias_bedroom open a
Nemesis MUD connection dialog. On first connect they grant two items:
- `jq_mud_access_token` — quest item proving the player has logged in.
- `jq_mud_logout_device` — the logout device (see below).

The computer uses `storeOriginMap: true`, which records which bedroom the player
connected from. This is passed to the logout device so the origin is pre-selected.

### MUD Logout Device (jq_mud_logout_device)
**Usable from anywhere in the game world — no matter how deep into a dungeon the player is.**

- Defined as a consumable with `keepAfterUse: true` (never consumed).
- On use it opens a teleport-menu (defined in `res/raw/jq_mud_logout.json`) with choices:
  1. Jasia's Bedroom (home)
  2. Castle — Jasia's Bedroom (castle_jasias_bedroom)
  3. Castle — Sunny's Bedroom (castle_sunnys_bedroom)
  4. Stay connected (cancel — no teleport)
- The option matching the player's connection origin is pre-selected.
- Requires the player to carry `jq_mud_access_token` to activate (prevents use before
  connecting to the MUD for the first time).
- The teleport_menu action is defined in `res/raw/jq_mud_logout.json`.

### Diving Bag
Helmet slot item. The Sea map exit DOWN to the Octopus Lair requires it equipped.

### Daily Search Areas
52 outdoor search spots with 24-hour reset timers.

### Inn Rooms
Players can buy a night's rest at any island inn (gold cost, fully heals HP).

### Guild Completion
All 12 guild quests → Guild Badge + Guildmaster's Blade (unique weapon).

## ID Prefix
All new content uses the `jq_` prefix to avoid conflicts with existing content.
