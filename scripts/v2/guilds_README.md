# Five-Guild System + Tiled `.world` files for jasias-quest

A drop-in content pack for the [jasias-quest](https://github.com/jmlucas31070-dev/jasias-quest)
fork of Andor's Trail. Adds:

- **Five guilds** the player can join, each with a 7-rank progression and a final
  master quest:
  - **Iron Hall** (fighter) — Aldric the Ironclad
  - **Shadow Lodge** (thief) — Vespera the Quiet
  - **Sun Sanctum** (cleric) — Father Caelan
  - **Verdant Circle** (druid) — Mother Briar
  - **Arcanum Spire** (mage) — Magister Vorell
- A **stacking actor condition per guild** representing rank — every rank-up
  adds one stack of passive bonuses suited to that guild's role.
- A **master tome** unique item per guild, awarded on master quest
  completion.
- **5 guild hall TMX templates** (one per guild) — minimal stub maps with
  the master spawned at the centre and a placeholder exit door for you to
  wire up to your towns.
- **383 Tiled `.world` files** — one per region of jasias-quest's outdoor
  & dungeon worlds. Drop them next to the corresponding TMX files and the
  Tiled editor will let you view each region as one continuous world.
- A **Python helper** that re-generates those `.world` files at any time
  (for when you add or rename maps).

Everything ships in the format Andor's Trail expects: JSON in `res/raw/`,
the registration array in `res/values/loadresources.xml`, TMX hall files in
`res/xml/`, and the Tiled `.world` files in `worlds/` (you copy those into
`res/xml/` alongside the TMX files).

---

## What's in the box

```
jasias_guilds/
├── README.md
├── res/
│   ├── raw/
│   │   ├── actorconditions_guilds.json    # 5 stacking rank conditions
│   │   ├── itemcategories_guilds.json     # 1 new neck-slot category
│   │   ├── itemlist_guilds.json           # 5 master tomes
│   │   ├── monsterlist_guilds.json        # 5 guild master NPCs
│   │   ├── conversationlist_guilds.json   # 95 dialogue phrases
│   │   └── questlist_guilds.json          # 5 quests, 8 stages each
│   ├── values/
│   │   └── loadresources.xml              # full file with new entries
│   └── xml/
│       └── interiors_guild_*.tmx          # 5 hall templates
├── worlds/                                # 383 Tiled .world files
│   ├── level_0_ados_city.world
│   ├── level_0_deniran_city.world
│   ├── ...
│   └── level_7_kikareukin_clouds.world
└── scripts/
    └── generate_worlds.py                 # regenerate worlds from TMX inventory
```

---

## Installation

> **Backup your fork first.** This pack overwrites `loadresources.xml` and
> drops files into `res/xml/`.

1. Copy `res/raw/*` into your fork's `AndorsTrail/res/raw/`.
2. **Replace** `AndorsTrail/res/values/loadresources.xml` with the version
   from `res/values/loadresources.xml`. (Or apply the manual patch in
   *Manual loadresources patch* below.)
3. Copy `res/xml/interiors_guild_*.tmx` into `AndorsTrail/res/xml/`.
4. Copy **all 383 files** from `worlds/` into `AndorsTrail/res/xml/`.
   These are not loaded by the game — they're metadata files used only by
   the Tiled editor. Putting them in the same folder as the TMX files lets
   Tiled discover them.
5. Build as usual (`./gradlew assembleDebug` or open in Android Studio).

---

## How the guild system works

### Rank progression

Each guild has a single quest (e.g. `g_quest_iron`) with stages
**10, 20, 30, 40, 50, 60, 70, 100**. Stages 10–70 are the seven ranks:

| Stage | Rank          | Tribute (gold) | XP reward |
| ----- | ------------- | --------------:| ---------:|
| 10    | Initiate      |              0 |        50 |
| 20    | Apprentice    |             50 |       100 |
| 30    | Adept         |            200 |       200 |
| 40    | Journeyman    |            500 |       400 |
| 50    | Veteran       |          1,500 |       800 |
| 60    | Elder         |          5,000 |     1,600 |
| 70    | Grandmaster   |         15,000 |     3,200 |
| 100   | Master (done) |         50,000 |     5,000 |

Each rank-up:

1. Removes the gold tribute from the player (`giveItem gold` with negative
   value).
2. Advances the quest to the next stage (`questProgress`).
3. Adds **one stack** of the guild's actor condition (`actorCondition` reward
   value 999 = forever; the condition has `isStacking: 1`).
4. Increases the player's standing with the guild's faction
   (`alignmentChange`) by 5 (or 25 on the master stage).

Because the rank conditions stack, by the time the player is rank 7 they
have +7×(per-stack bonus) on the relevant stat. The bonuses are:

| Guild           | Per-stack bonus                                   | Master tome bonus                       |
| --------------- | ------------------------------------------------- | --------------------------------------- |
| Iron Hall       | +1/+1 attack damage, +2 max HP                    | +5 AC, +1 DR                            |
| Shadow Lodge    | +5 critical skill, +2 attack chance               | +10 critical skill, +5 AC               |
| Sun Sanctum     | +5 max HP, +1 damage resistance                   | +15 max HP, +5 block chance             |
| Verdant Circle  | +5 attack chance                                  | +1 max AP, +10 AC                       |
| Arcanum Spire   | +3 critical skill, +1 max HP, +1/+2 attack damage | +1 max AP, +5 critical skill            |

### The master quest

The master quest (stage 70 → 100) is a two-step interaction:

1. The player asks the master for the master trial. The master tells them
   to "walk the world for a season" and starts a hidden timer
   (`createTimer g_t_master_<guild>`).
2. The player must wait at least **5,760 game rounds** (≈40 hours of game
   time at 25s/round) AND be carrying **50,000 gold** to complete it.
3. Speaking to the master a second time (after both conditions are met)
   takes the gold, advances the quest to stage 100, and gives the
   appropriate Tome of the *Guild* — a permanent neck-slot equippable that
   grants the master-tier bonuses listed above.

This means the master quest is the only one that gates on real-time play,
not just gold. If you'd rather it be instant, search for `MASTER_TIMER_ROUNDS`
in `res/raw/conversationlist_guilds.json` (or just `5760`) and replace it
with a smaller number, or remove the `timerElapsed` requirement entirely.

### Faction standings

Each guild's quest also raises the player's faction score with that guild
(`guild_iron`, `guild_shadow`, `guild_sun`, `guild_verdant`, `guild_arcane`).
You can use these in your own dialogues and quests as `factionScore`
requirements — for example, only sell guild-branded gear if the player is
above some threshold, or have rival guilds penalise standing in others.

### Wiring the halls into your world

The five `interiors_guild_*.tmx` files are intentionally minimal — empty
walkable maps with the master NPC spawned dead-centre at tile (16,16) and a
placeholder map-change object at the left edge marked
`REPLACE_ME_WITH_PARENT_TOWN_MAP_ID`. To attach a hall to a town:

1. Open the hall TMX in Tiled and decorate it however you like (walls,
   furniture, banners, etc.) — the master spawn and the leave object will
   stay put.
2. Edit the placeholder mapchange's `map` property to point at the town map
   the player should re-enter when they leave.
3. In your town map, add a matching mapchange object that points at the
   hall and uses `place="entrance_to_<guild>_hall"` so the player arrives
   at the hall's entrance.

You can also place multiple halls of the same guild in different towns —
just clone the TMX, rename it (`interiors_guild_iron_crossglen.tmx`,
`interiors_guild_iron_kalavan.tmx`, etc.) and adjust the mapchange targets.
The guild master NPC is `unique: 1`, so only one of them will be on the
world at any time.

---

## How the Tiled `.world` files work

Tiled's [`.world` format](https://doc.mapeditor.org/en/stable/manual/worlds/)
is a JSON sidecar that groups multiple TMX files into one displayed world.
Each entry gives a TMX filename and its pixel position:

```json
{
  "type": "world",
  "onlyShowAdjacentMaps": false,
  "maps": [
    {"fileName": "level_0_ados_city_x0_y0.tmx", "x": 0,    "y": 0,    "width": 1024, "height": 1024},
    {"fileName": "level_0_ados_city_x1_y0.tmx", "x": 1024, "y": 0,    "width": 1024, "height": 1024},
    {"fileName": "level_0_ados_city_x0_y1.tmx", "x": 0,    "y": 1024, "width": 1024, "height": 1024},
    ...
  ]
}
```

Once Tiled finds a `.world` file in the same directory as the maps, opening
any one of those maps will show the rest tiled around it as the player
sees them. You can scroll across a whole region and edit all the constituent
maps as one — much easier than juggling 16 separate files.

### One world per region

Maps are grouped by **region** — the part of the filename before the
trailing `_x{X}_y{Y}` suffix. So:

- `level_0_ados_city_x0_y0.tmx` … `level_0_ados_city_x3_y3.tmx`
  → `level_0_ados_city.world` (16 maps)
- `level_3_orril_dungeon_x0_y0.tmx` … `_x4_y7.tmx`
  → `level_3_orril_dungeon.world` (40 maps)

The pack ships **383 world files** covering all `level_*` maps in the
fork (6,343 TMX files in total, distributed across levels 0–7).

### Levels covered

| Level | World files | Notes                                          |
| ----- | ----------- | ---------------------------------------------- |
| 0     | 149         | Surface — towns, forests, plains, deserts, sea |
| 1     | 80          | First underground / cave layer                 |
| 2     | 45          | Deeper caves, dungeons, mines                  |
| 3     | 32          | Sea floor, deeper dungeons                     |
| 4     | 20          | —                                              |
| 5     | 20          | —                                              |
| 6     | 19          | Atlantis approach, kanmararn city              |
| 7     | 18          | Atlantis interior, cloud islands               |

### Regenerating after you add/rename maps

`scripts/generate_worlds.py` re-scans your `res/xml/` directory and rewrites
all `.world` files. Run it any time the map inventory changes:

```bash
python3 scripts/generate_worlds.py \
    --maps-in  AndorsTrail/res/xml \
    --out-dir  AndorsTrail/res/xml \
    --prefix   level_
```

Use `--prefix interiors_` to also generate worlds for interior map families,
or omit `--prefix` to generate one world per region for *every* TMX in the
folder. Use `--min-maps 4` to skip regions that contain only a few maps.

The script reads `width`, `height`, `tilewidth`, and `tileheight` from each
TMX so it works correctly even if a region uses non-standard map dimensions.

---

## Manual loadresources patch

If you'd rather merge by hand than overwrite, add these lines inside the
existing arrays in `AndorsTrail/res/values/loadresources.xml`:

```xml
<array name="loadresource_itemcategories">
    ...
    <item>@raw/itemcategories_guilds</item>
</array>
<array name="loadresource_actorconditions">
    ...
    <item>@raw/actorconditions_guilds</item>
</array>
<array name="loadresource_items">
    ...
    <item>@raw/itemlist_guilds</item>
</array>
<array name="loadresource_quests">
    ...
    <item>@raw/questlist_guilds</item>
</array>
<array name="loadresource_conversationlists">
    ...
    <item>@raw/conversationlist_guilds</item>
</array>
<array name="loadresource_monsters">
    ...
    <item>@raw/monsterlist_guilds</item>
</array>
```

---

## Known caveats

- **Master sprite indices are placeholders.** I used `monsters_humanoids:0..4`
  for the five masters — adjust to whatever NPC sprites you'd like.
- **Master tome icons are placeholders** (`items_weapons:1`, `items_misc:0`,
  `items_jewelry:0..1`, `items_consumables:0`). Swap to better art when you
  have it.
- **Quest tribute amounts are tuned for an Andor's Trail-paced economy**
  (50→50,000 gold). If your fork's economy is more or less generous,
  re-balance the `TRIBUTES` and `MASTER_TRIBUTE` values — they live in
  `res/raw/conversationlist_guilds.json` (look for the gold tribute amounts
  in each `g_<guild>_trial_<N>` phrase).
- **The `gold` item ID is assumed to be present** in the fork (it's the
  Andor's Trail vanilla item ID for gold). If your fork uses a different
  ID, search-and-replace `"requireID": "gold"` and `"rewardID": "gold"` in
  the conversation list.
- **The master tomes use the `neck` equipment slot.** If you want them as
  read-only books instead, change `actionType` from `"wear"` to `"none"`
  in `itemcategories_guilds.json` and they become inventory-only flavour
  items (you'll lose the equip-time stat bonuses; bake those into the
  rank-7 actor condition stack instead).
- **`.world` files are Tiled-editor metadata only.** They are *not*
  loaded by the Andor's Trail engine and don't affect runtime behaviour
  one way or the other. They're purely a quality-of-life tool for editing
  the world in Tiled.
- **The `worlds/` folder ships outside `res/xml/` to keep the install step
  obvious** — copy them in once you've decided you want them. Putting them
  in `res/xml/` is harmless (Android resource compilation skips unknown
  extensions), but it's a lot of small files to commit if you're not
  using Tiled.
