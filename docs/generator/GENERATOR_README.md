# Andor's Trail Content Generator v2
## Developer Guide — How to Modify and Run

---

## Quick Start

```bash
node generate_andors_trail_v2.mjs
```

**Requirements:** Node.js 18+ (uses only built-in modules — no `npm install` needed)

**Output:** `andors_trail_content_v2.zip` in the working directory

---

## What Gets Generated

| File | Description |
|---|---|
| `itemlist.json` | All 2,200+ items |
| `monsterlist.json` | All 2,300+ monsters and NPCs |
| `droplists.json` | All drop tables |
| `conversationlist.json` | All 769 conversation trees |
| `questlist.json` | All 350 quests |
| `actorconditions.json` | All status conditions |
| `values/strings.xml` | ~10,000 Android string entries |
| `values/loadresources.xml` | Resource manifest for AT to load all files |
| `data/*.json` | Specialised sub-files for quick reference |
| `*.tmx` | 33 Tiled Map Format files (all quest + world maps) |
| `README.md` | Developer integration guide (included in zip) |

---

## Script Structure

The script is one self-contained ESM file (`generate_andors_trail_v2.mjs`) with clearly marked sections:

```
LINE ~1      — FILE HELPERS       (writeFile, writeJson)
LINE ~30     — ZIP BUILDER        (pure Node.js, no deps)
LINE ~90     — TMX / TILE HELPERS (tilesets, base64+gzip layers, objects)
LINE ~160    — MASTER DATA        (regions, races, holidays, guilds, etc.)
LINE ~220    — CONTENT HELPERS    (makeItem, makeMonster, makeConversation, etc.)
LINE ~310    — PICKPOCKET SYSTEM
LINE ~380    — TIMEKEEPER/HOLIDAY SYSTEM
LINE ~530    — ANIMAL CONTENT     (23 regions × 25 animals)
LINE ~560    — FORAGE CONTENT
LINE ~590    — MINING CONTENT
LINE ~640    — CRAFTING ITEMS     (cloth, food, produce, forge, bench, miner)
LINE ~730    — GUILD ITEMS        (scrolls, lockpicks, keys)
LINE ~800    — GUILD CONVERSATIONS (doors, bank, jail, guild NPCs)
LINE ~950    — FACTION CONTENT    (15 races)
LINE ~1000   — QUEST CONTENT      (witch, drow, lloth, dragons, moons, castle, towers, haunted)
LINE ~1250   — POKEMON CONTENT    (9 regions, 270 beasts)
LINE ~1360   — STOLEN ITEMS
LINE ~1380   — MAP GENERATORS     (all 33 TMX maps)
LINE ~1700   — XML RESOURCES
LINE ~1730   — README BUILDER
LINE ~1780   — MAIN (assembles and writes ZIP)
```

---

## How TMX Maps Work

Every map calls `buildTMX()` which automatically inserts:

### 4 Standard Tilesets (always present)
```
dc-dngn    firstgid=1    521×521px, 1px spacing/margin  (floor/walls)
dc-dngn-t  firstgid=257  521×521px, 1px spacing/margin  (transparent/walkable)
chars0     firstgid=513  521×521px, 1px spacing/margin  (character sprites)
items      firstgid=769  521×521px, 1px spacing/margin  (item sprites)
```

### 4 Standard Tile Layers (base64 + gzip encoded)
```
Ground    — filled with GID 1   (stone floor from dc-dngn)
Walkable  — filled with GID 257 (walkable marker from dc-dngn-t)
Objects   — empty (GID 0)
Above     — empty (GID 0)
```

### Then your custom object layers follow

The base64+gzip data is generated with:
```js
const raw = Buffer.alloc(width * height * 4);   // 4 bytes per tile
for (let i = 0; i < width*height; i++)
  raw.writeUInt32LE(fillGid, i*4);               // little-endian uint32
const data = zlib.gzipSync(raw).toString('base64');
```

---

## How to Add a New Map

Find `generateAllMaps()` and add a new entry:

```js
maps.push(makeStandardMap('my_dungeon.tmx', [
  // Object layer 1 — monster spawns
  {
    type: 'objectgroup',
    name: 'Spawn_monsters',
    color: '#ff0000',
    objects: [
      makeSpawnObj('monster_witch_0', 96, 96),      // (actorId, x_px, y_px)
      makeSpawnObj('monster_witch_1', 128, 96),
    ]
  },
  // Object layer 2 — interactive objects (keys)
  {
    type: 'objectgroup',
    name: 'Keys_loot',
    color: '#00ff00',
    objects: [
      makeKeyObj('chest_1', 'conv_chest_loot', 64, 64),   // (name, convId, x, y)
      makeSignObj('sign_entrance', 64, 32, 'Enter at your own risk!'),
    ]
  },
  // Object layer 3 — NPC spawns
  {
    type: 'objectgroup',
    name: 'Spawn_npcs',
    color: '#0000ff',
    objects: [
      makeNPCObj('npc_boss', 'conv_dungeon_boss', 160, 160),
    ]
  },
], 30, 30));  // width=30, height=30 tiles
```

### Object helper signatures:
```js
makeSpawnObj(actorId, x, y, extraProps=[])
makeNPCObj(actorId, convId, x, y, extraProps=[])
makeKeyObj(name, convId, x, y, extraProps=[])
makeSignObj(name, x, y, signText)
```

### Extra properties example:
```js
makeKeyObj('locked_chest', 'conv_chest', 96, 96, [
  { name: 'requiresItem', value: 'item_door_key' },
  { name: 'resetAfterHours', value: '24' },
])
```

---

## How to Add a New Item

Call `makeItem()` and push to one of the aggregation arrays in `main()`:

```js
const myItem = makeItem({
  id:             'item_magic_sword',       // unique string ID
  name:           'Magic Sword',            // display name (auto-added to strings.xml)
  desc:           'A sword crackling with magic energy.',  // optional
  iconRow:        5,                        // sprite sheet row
  iconCol:        3,                        // sprite sheet column
  itemType:       'weapon',                 // 'weapon' | 'armor' | 'miscellaneous'
  equipmentSlot:  'weapon',                 // 'weapon' | 'offhand' | 'head' | 'body' | 'hand' | 'feet' | 'neck' | 'ring'
  damagePotential: dmg(8, 20),             // {current: min, max: max}
  damageResistance: 0,                      // flat DR
  attackChance:   5,                        // bonus attack %
  baseMarketCost: 250,                      // gold value
  isQuestItem:    false,
  isSellable:     true,
  weight:         2,
  // Optional:
  useEffect:      { addGold: 100 },         // or restoreHP, applyActorCondition, mapChange, etc.
  charges:        3,                        // if consumable
});
```

---

## How to Add a New Monster / NPC

```js
const myMonster = makeMonster({
  id:             'npc_cave_troll',
  name:           'Cave Troll',
  hp:             120,
  ap:             10,
  atk:            75,                       // attack chance %
  dmgMin:         8,
  dmgMax:         18,
  block:          10,                       // block chance %
  dr:             5,                        // damage resistance
  droplistID:     'dl_cave_troll',          // optional drop table
  faction:        'trolls',
  spawnGroup:     2,
  iconRow:        6,
  iconCol:        3,
  conversationID: 'conv_cave_troll',        // optional
});
```

---

## How to Add a New Conversation

```js
conversations.push(makeConversation(
  'conv_my_npc',                            // unique ID
  'Hello adventurer! Can I help you?',     // opening message (auto-added to strings.xml)
  [
    // Reply with no conditions
    { text: 'Tell me about quests.',
      actions: [{ startQuest: 'quest_my_quest' }] },

    // Reply gated on guild level
    { text: 'Pickpocket (Thief 3+)',
      conditions: [{ requiresGuildLevel: { guild: 'thief', minLevel: 3 } }],
      actions: [{ rollChance: { chance: 60, onSuccess: 'stealGold', onFail: 'caught' } }] },

    // Reply gated on item possession
    { text: 'Here is the key.',
      conditions: [{ hasItem: 'item_door_key' }],
      actions: [{ consumeItem: 'item_door_key' }, { openDoor: true }] },

    // Reply gated on quest state
    { text: 'Quest done!',
      conditions: [{ requiresQuestPart: { questID: 'quest_my_quest', part: 1 } }],
      actions: [{ giveItem: 'item_magic_sword' }] },

    // Always-available exit
    { text: 'Goodbye.' },
  ]
));
```

### Common condition types:
```js
{ requiresGuildLevel: { guild: 'thief', minLevel: 3 } }
{ hasItem: 'item_id' }
{ hasAllItems: ['item_a', 'item_b'] }
{ hasCondition: 'condition_name' }
{ notHasCondition: 'condition_name' }
{ requiresQuestPart: { questID: 'quest_id', part: 0 } }
{ requiresActorCondition: 'ac_condition_id' }
{ requiresFactionLevel: { race: 'drow_elf', minLevel: 2 } }
```

### Common action types:
```js
{ startQuest: 'quest_id' }
{ setQuestPart: { questID: 'quest_id', part: 1 } }
{ giveItem: 'item_id' }
{ consumeItem: 'item_id' }
{ payGold: 100 }
{ addGold: 50 }
{ openShop: 'shop_id' }
{ openDoor: true }
{ startCombat: '$target' }
{ mapChange: { mapID: 'map_id', mapX: 5, mapY: 5 } }
{ rollChance: { chance: 75, onSuccess: 'actionName', onFail: 'otherAction' } }
{ applyActorCondition: { conditionID: 'ac_id', duration: 5 } }
{ setActorCondition: 'ac_id' }
{ setCondition: 'condition_name' }
{ giveDropList: 'dl_id' }
```

---

## How to Add a New Quest

```js
quests.push(makeQuest(
  'quest_my_quest',                         // unique ID
  'My Amazing Quest',                       // quest name (auto-added to strings.xml)
  'A description of what this quest is about.',
  [
    // Part 0 — first objective
    { desc: 'Go find the magic sword.',
      exp: 200 },
    // Part 1 — second objective
    { desc: 'Return the sword to the king.',
      exp: 500,
      reward: [{ itemID: 'item_magic_sword', chance: 100, quantity: { current: 1, max: 1 } }] },
  ]
));
```

---

## How to Add a New Holiday

In the `HOLIDAYS` array near the top of the script:

```js
const HOLIDAYS = [
  // ... existing holidays ...
  {
    id:          'midsummer',            // used in all generated IDs
    name:        'Midsummer Festival',   // display name
    monthDay:    '06-21',                // MM-DD
    weeksBefore: 1,
    weeksAfter:  1,
    theme:       'summer',
  },
];
```

Then in `buildTimekeeperSystem()`, add entries to `holidayThemeGifts` and `holidayGoodGifts`:

```js
const holidayThemeGifts = {
  // ... existing entries ...
  midsummer: ['Sun Crown', 'Sunflower', 'Bonfire Ash', 'Summer Ale', 'Maypole Ribbon', 'Meadow Wreath'],
};
const holidayGoodGifts = {
  // ... existing entries ...
  midsummer: ['Solar Amulet', 'Sunblade', 'Light Crystal', 'Dawn Ring', 'Midsun Staff', 'Radiant Stone'],
};
```

The Timekeeper conversation and holiday quest are auto-generated from that data.

---

## How to Modify the Pickpocket System

Find `buildPickpocketSystem()`. Key values to change:

```js
// Gold per thief level (index 0 = level 1, index 9 = level 10)
const PICKPOCKET_GOLD = [30, 50, 75, 110, 150, 200, 275, 360, 460, 600];

// Success chances per method (in conv_pickpocket_action replies)
// Thief 1+ standard:   chance: 50
// Thief 6+ Sneak:      chance: 75
// Thief 9+ Hide:       chance: 90

// Kill gold: items gold_coins_1 through gold_coins_19 (always random 1-19g)
// Change the range(19) to change the max drop:
const KILL_GOLD_ITEMS = range(19).map(g => { ... });  // 19 = max 19g
```

To change the number of pickpocket targets, change:
```js
range(200).forEach(i => { ... });   // 200 targets
```

---

## How to Modify the Timekeeper

The Timekeeper conversation is in `buildTimekeeperSystem()`.

To change what the Timekeeper says between holidays, edit the `conv_timekeeper` replies:
```js
conversations.push(makeConversation('conv_timekeeper',
  'I am the Timekeeper. I watch the flow of days...',  // ← change this
  [
    // Holiday branches are auto-generated above this
    { text: 'What is today\'s date?', actions: [{ showCurrentDate: true }] },
    // Add new options here
    { text: 'My new option.', actions: [...] },
    { text: 'Leave' },
  ]
));
```

To add a new holiday NPC variant (so the Timekeeper looks different per holiday), add `spawnLayerID` and `replaceActorID` properties to the layer trigger objects inside `template_holiday.tmx`'s `Replace_holiday_{id}` layers in `generateAllMaps()`.

---

## How to Add a New Map Size

Default is 30×30 tiles. Pass width and height as the 3rd and 4th args to `makeStandardMap()`:

```js
maps.push(makeStandardMap('my_big_dungeon.tmx', [...layers], 50, 80));
//                                                              ^   ^
//                                                              width height (tiles)
```

Pixel size = tiles × 32px per tile.

---

## How to Add a New Region

In the `REGIONS` array and `REGION_ANIMAL_NAMES` object:

```js
const REGIONS = [
  // ... existing regions ...
  'mushroom_forest',
];

const REGION_ANIMAL_NAMES = {
  // ... existing entries ...
  mushroom_forest: [
    'Spore Bat', 'Fungal Crawler', 'Mushroom Golem', 'Spore Cloud', 'Cap Frog',
    'Mycelium Rat', 'Truffle Hound', 'Puffball Slug', 'Toadstool Toad', 'Mold Spider',
    // ... 25 total names ...
  ],
};
```

Forage items, conversations, and quests are automatically generated from the REGIONS array.

---

## Tileset Icon Row/Col Reference

Icons are referenced as `iconRow:N, iconCol:N` in `makeItem()` and `makeMonster()`.

| Tileset | GID Start | Used For |
|---|---|---|
| dc-dngn.png | 1 | Terrain tiles (rows 1–16) |
| dc-dngn-t.png | 257 | Transparent overlays |
| chars0.png | 513 | Monster/NPC sprites |
| items.png | 769 | Item icons |

For items, `iconRow` and `iconCol` index into the `items.png` sprite sheet (32×32 cells).
For monsters, they index into the `chars0.png` sheet.

---

## Running with Custom Output Path

Change this constant near the top of the script:

```js
// Default: produces andors_trail_content_v2.zip in the parent dir
fs.writeFileSync(path.join(__dirname, '../andors_trail_content_v2.zip'), zipBuf);

// Custom path:
fs.writeFileSync('/path/to/my/output/my_content.zip', zipBuf);
```

---

## Output ZIP Structure

```
andors_trail_content_v2.zip
├── README.md                       ← integration guide for the game dev
├── values/
│   ├── strings.xml                 ← merge into your Android string resources
│   └── loadresources.xml           ← list of all content files to load
├── data/
│   ├── animal_animals.json
│   ├── forage.json
│   ├── mining.json
│   ├── pickpocket.json
│   ├── guild.json
│   ├── faction.json
│   ├── holiday.json
│   ├── pokemon.json
│   └── dragons.json
├── itemlist.json
├── monsterlist.json
├── droplists.json
├── conversationlist.json
├── questlist.json
├── actorconditions.json
└── *.tmx  (33 map files)
```

---

## Tips and Gotchas

- **IDs must be unique.** The `dedup()` call in `main()` silently drops duplicate IDs. If items vanish, check for ID collisions.
- **String auto-registration.** Every call to `makeItem()`, `makeMonster()`, `makeConversation()`, and `makeQuest()` calls `str()` which automatically registers text in `STRINGS` → `strings.xml`. You don't need to add strings manually.
- **Object IDs reset per map.** `_objId` resets to 1 at the start of each `buildTMX()` call. This is correct — object IDs are local to each TMX file.
- **Tile pixel coordinates.** TMX object `x` and `y` values are in pixels (not tiles). Multiply tile position by 32 to get pixel position: tile (2, 3) → x=64, y=96.
- **No external dependencies.** The ZIP builder uses only `node:zlib` and `node:fs`. The TMX tile data uses `zlib.gzipSync()`. Never add `require()` or `import` from npm packages — it will break the zero-install promise.
- **Tileset image files** (`dc-dngn.png`, `dc-dngn-t.png`, `chars0.png`, `items.png`) are not included in the ZIP — they must come from the Andor's Trail game assets. The TMX files reference them by filename only.

---

*Andor's Trail Extended Content Generator v2 — May 2026*
