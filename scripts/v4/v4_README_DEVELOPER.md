# Jasias Quest — Addition: Developer README

## Story Layout

This addition introduces five interconnected systems layered on top of Jasias Quest:

### 1. Trainer NPCs (270 unique trainers)
- Located across all regions and towns.
- Each trainer has a unique name and opening line.
- Conversations: greeting → battle prompt → (No Thanks | Battle).
- Monster data: `res/raw/monsterlist_trainer.json`
- Conversations: `res/raw/conversations_trainers.json`

### 2. Regional Wildlife (15 regions × 25 animals = 375 animals)
- Monster data: `res/raw/monsterlist_animals.json`
- Each region has its own droplist: `res/raw/droplists_regions.json`
- Forage items per region: `res/raw/itemlist_forage.json`
- Map templates per region: `res/xml/template_<region>.tmx`
  - Each map has a full-coverage Spawn layer tagged with the region's monster group.

### 3. Guild Crafting System
- Three guilds: Mage, Cleric, Druid.
- Scrolls and potions are guild-restricted.
- Crafting map: `res/xml/template_crafting_room.tmx`
  - Writing Desk → scroll crafting conversation.
  - Brewing Cauldron → potion crafting conversation.
- Portable items (Writing Table, Mini Cauldron) allow field crafting.
- Actor conditions: `res/raw/actorconditions_mage.json`, `actorconditions_cleric.json`, `actorconditions_druid.json`
- Items: `res/raw/itemlist_crafted.json`

### 4. Lockpick & Bash System
- Three lockpick tiers: Crude (20%), Standard (50%), Masterwork (85%).
- Bash requires Fighter class; Lockpick requires Thief class.
- Bash effectiveness depends on shield type (none < cloth < metal).
- Template locked room: `res/xml/template_door.tmx`
- Conversations: `res/raw/conversations_door.json`

### 5. Actor Conditions
- 50 per guild (25 offense, 24 defense) — inspired by D&D spell schools.
- Each condition is guild-restricted.

## Changed / New Files

| File | Purpose |
|------|---------|
| `res/raw/monsterlist_trainer.json` | 270 trainer NPCs |
| `res/raw/monsterlist_animals.json` | 375 regional animals |
| `res/raw/droplists_regions.json` | Regional drop tables |
| `res/raw/itemlist_forage.json` | Forage items (12 per region) |
| `res/raw/itemlist_crafted.json` | Crafted scrolls and potions |
| `res/raw/itemlist_lockpicks.json` | 3 lockpick tiers |
| `res/raw/actorconditions_mage.json` | Mage guild conditions |
| `res/raw/actorconditions_cleric.json` | Cleric guild conditions |
| `res/raw/actorconditions_druid.json` | Druid guild conditions |
| `res/raw/conversations_trainers.json` | Trainer battle conversations |
| `res/raw/conversations_crafting.json` | Crafting conversations |
| `res/raw/conversations_door.json` | Door lockpick/bash conversation |
| `res/xml/template_<region>.tmx` | 15 region map templates |
| `res/xml/template_crafting_room.tmx` | Guild crafting hall map |
| `res/xml/template_door.tmx` | Locked door template map |
| `res/values/strings.xml` | All string resources |
| `res/values/loadresources.xml` | Resource loader entries |
| `res/xml/worldmap.xml` | World map area entries |

## Integration Notes
- Copy all `res/` folders directly into your jasias-quest project root.
- Ensure your `loadresources.xml` is merged (not replaced) with any existing file.
- Same for `strings.xml` and `worldmap.xml`.
- Spawn layers use the Spawn tile (value 1) covering the entire map; configure your spawn manager to read the `spawnGroup` property to pick the correct monster pool.
- Guild restriction is enforced via the `requireClass` property on conversation replies and the `restriction` field on actor conditions — implement checks in your conversation engine.
