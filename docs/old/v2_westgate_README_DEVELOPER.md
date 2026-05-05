# Westgate Heights — Developer README

A drop-in content expansion for the **jasias-quest** fork
(<https://github.com/jmlucas31070-dev/jasias-quest>), built with the
Andor's Trail content conventions and inspired in scope and pacing by
the player-housing systems in [Stendhal](https://stendhalgame.org).

This expansion adds a brand-new neighborhood — **Westgate Heights** —
just outside Ados's west gate, plus four buyable player homes and a
full-loop crafting economy: sewing, cooking, gardening, and forging.

---

## 1. Repository layout

Drop the contents of `res/` straight into `app/src/main/res/` of your
jasias-quest fork. Folder structure:

```
res/
├── values/
│   ├── loadresources.xml      ← MERGE with your existing loadresources.xml
│   └── strings.xml            ← MERGE with your existing strings.xml
├── xml/
│   ├── worldmap.xml           ← MERGE with your existing worldmap.xml
│   ├── westgate_market.tmx
│   ├── westgate_home1.tmx
│   ├── westgate_home2.tmx
│   ├── westgate_home3.tmx
│   └── westgate_home4.tmx
└── raw/
    ├── westgate_items.json
    ├── westgate_cooking.json
    ├── westgate_garden.json
    ├── westgate_forge.json
    ├── westgate_droplists.json
    ├── westgate_monsters.json
    ├── westgate_conversationlists.json
    ├── westgate_quests.json
    └── westgate_maps.json
```

> **Three files are MERGES, not overwrites:**
> `res/values/loadresources.xml`, `res/values/strings.xml`,
> `res/xml/worldmap.xml`. Open the supplied versions, copy the new
> entries into your existing files in the matching `<integer-array>` /
> `<resources>` / `<worldmap>` blocks. Everything else can be dropped
> straight in.

---

## 2. Story layout

The player has been adventuring across the lands for some time. Word
spreads in the taverns of Ados that a developer named **Mira Penhollow**
has cleared land outside the west gate and is selling four versions of a
personal home. The neighborhood — christened **Westgate Heights** — is
already busy: a market square has gone up around the gate road, with
six stalls, a farmer, a real-estate agent, and the homes themselves
arranged in a row to the south.

Players can stop, browse, and — if they have the gold — own real estate
for the first time in the game. Each tier of home unlocks more of the
new crafting systems, building toward a true home base.

---

## 3. Maps changed / added

**Changed (one map):**

- `ados_outside_west.tmx` (NOT included as a TMX — see notes below).
  You need to add a single MapChange object on its western edge that
  points to `westgate_market` at place `from_westgate_market`. This is
  a one-line edit in Tiled. We do not ship a modified version because
  the file may differ between forks.

**Added (five maps):**

| Map id              | TMX file                  | Purpose                                                                    |
| ------------------- | ------------------------- | -------------------------------------------------------------------------- |
| `westgate_market`   | `westgate_market.tmx`     | Outdoor square. 6 stalls + realtor + farmer + 4 home doors. 30×22 tiles.   |
| `westgate_home1`    | `westgate_home1.tmx`      | 1 room. Sewing machine. 12×10 tiles.                                       |
| `westgate_home2`    | `westgate_home2.tmx`      | 2 rooms. Sewing + stove. 18×12 tiles.                                      |
| `westgate_home3`    | `westgate_home3.tmx`      | 3 rooms. Sewing + forge + stove + 4-tile garden. 24×18 tiles.              |
| `westgate_home4`    | `westgate_home4.tmx`      | 4 rooms. Everything above + butler + 8-tile garden. 30×22 tiles.           |

> All five TMX files are **skeleton maps**. The ground layer is filled
> with tile id 1 from a placeholder tileset reference (`indoor1.tsx`,
> `outdoor1.tsx`, `world1.tsx`, `buildings1.tsx`, `objects1.tsx`). Open
> each map in [Tiled](https://www.mapeditor.org/) and paint the floors,
> walls, doors, and decorations using your fork's existing tilesets.
> The **eventLayer** is fully wired — NPCs, objects, MapChange portals,
> and signposts will all work as soon as you load the JSON files,
> regardless of the cosmetic painting.

---

## 4. New mechanics

### Real estate (deeds)

The realtor `wg_npc_realtor` (Mira Penhollow) sells four deeds:

| Item id          | Deed                          | Price       |
| ---------------- | ----------------------------- | ----------- |
| `wg_deed_home1`  | Westgate Cottage (1 Room)     | 5,000 g     |
| `wg_deed_home2`  | Westgate House (2 Rooms)      | 12,000 g    |
| `wg_deed_home3`  | Westgate Manor (3 Rooms)      | 25,000 g    |
| `wg_deed_home4`  | Westgate Estate (4 Rooms)     | 50,000 g    |

Each deed is gated on `inventory_remove gold N` in the conversation
reply. The corresponding `MapChange` portal in `westgate_market.tmx`
declares `requires=wg_deed_homeN` so the door is locked until the player
owns the deed.

### Sewing machine

In every home. Talks via `wg_sewingmachine_greet`. Each reply is a
recipe — it removes ingredients (cloth, dye, button, thread, needle)
and gives an equippable garment. **15 sewable garments** total covering
every armor slot:

- **Head**: Linen Hood, Wool Cap, Decorated Cap
- **Neck**: Silk Scarf, Leather Amulet Cord
- **Body**: Cotton Tunic, Wool Cloak, Padded Vest, Embroidered Sash
- **Hand**: Linen Gloves, Leather Mittens, Silk Wraps
- **Feet**: Cloth Boots, Wool Slippers, Traveler's Shoes

The seamstress (`wg_npc_seamstress`) sells every ingredient.

### Cooking (stove + portable stove)

The cast-iron stove in homes 2/3/4 talks via `wg_stove_greet`. **12
cooked dishes** total: Bread, Vegetable Stew, Roast Chicken, Meat Pie,
Grilled Fish, Berry Tart, Hearty Soup, Grilled Sausage, Cheese Bake,
Honey Cake, Traveler's Ration, Garden Omelette. Each restores HP/AP via
`useEffect`.

The grocer (`wg_npc_grocer`) and the farmers market (`wg_npc_market`)
sell ingredients. Some recipes require garden crops, so cooking links
back into the gardening loop.

`wg_portable_stove` is a **carryable** version sold by the gift vendor.
It uses the same conversation engine but consumes a `wg_stove_fuel`
charge per cook and only knows 4 simple recipes (bread, sausage, grilled
fish, vegetable stew). Treat it like a normal `useEffect` item that
opens the conversation `wg_portable_stove_greet`.

### Gardening (homes 3 & 4)

Garden plots are spawn-points of `wg_obj_garden_plot`. Talking to a plot
opens `wg_garden_plot_greet`. The "plant" replies remove a seed and set
a `timer` reward (`172,800 seconds` = 48 real hours). The "harvest"
reply is gated on `timer_elapsed` for the matching timer and gives the
crop.

> **Note on the `timer` reward type**: Andor's Trail's stock engine does
> not ship a real-time timer reward. The skeleton uses `timer` /
> `timer_elapsed` as a clean placeholder. Two integration options:
>
> 1. **Easiest (no engine work)**: replace `timer` with the existing
>    `actorCondition` reward and apply a long-duration condition called
>    `wg_growing_carrot` with rounds = `172800` and a `displayInBuffBar`
>    flag. Then gate the harvest reply on `actorCondition_required` for
>    the same condition with min duration. The condition ticks every
>    in-game round, so calibrate `rounds` to your tick rate (or pin it
>    to wall-clock time using a `WallClockCondition` subclass — see
>    next).
>
> 2. **Recommended**: add a tiny `WallClockCondition` extension to your
>    Java sources that stores `System.currentTimeMillis()` at apply time
>    and reports `isFinished()` once 48 hours have passed. Wire two new
>    requirement / reward types — `WallTimerSet` and `WallTimerElapsed`
>    — into your `RewardEffect` switch. We left the names neutral
>    (`timer` / `timer_elapsed`) so this drop-in works with either
>    approach without renaming JSON.

The farmer (`wg_npc_farmer`) sells **24 seed varieties**, each producing
its matching crop (carrot, potato, cabbage, tomato, corn, wheat, barley,
onion, garlic, pepper, pumpkin, cucumber, lettuce, spinach, beans, peas,
radish, beet, strawberry, watermelon, apple, pear, grapes, herbs).

### Forge (homes 3 & 4)

The forge talks via `wg_forge_greet`. From there you can branch into
weapon, shield, or ring sub-menus. Each is a normal recipe reply.

- **12 weapons**: Iron Dagger, Iron Shortsword, Steel Longsword, Steel
  Battleaxe, Iron Mace, Steel Warhammer, Iron Spear, Steel Halberd,
  Bronze Scimitar, Steel Rapier, Iron Club, Steel Greatsword.
- **6 shields**: Iron Buckler, Reinforced Wooden Shield, Iron Round
  Shield, Steel Kite Shield, Steel Tower Shield, Steel Heater Shield.
- **12 rings**: Iron, Bronze, Silver, Gold, Copper Ring of Health, Iron
  Ring of Strength, Silver Ring of Agility, Gold Ring of Wisdom, Steel
  Ring of Defense, Bronze Ring of Speed, Silver Ring of Luck, Gold Ring
  of Power.

Ingots, hafts, grips, gemstones, and coal are sold by the weaponer
(`wg_npc_weaponer`) and armorer (`wg_npc_armorer`).

### Butler (home 4 only)

`wg_npc_butler` (Reginald) is gated on `inventory_kept wg_deed_home4`
and only spawns inside the 4-room estate. Talking to him offers seven
"fetch" sub-shops, each a mirror of one of the market-stall droplists
with `priceMultiplier: 0.8` applied to every line — a flat 20% discount
on everything sold in the entire neighborhood.

### Quests

Two log-only quests track player milestones:

- `wg_quest_home` — progress 1, 10, 20, 30, 40 corresponding to
  hearing about the neighborhood and buying each of the four homes.
- `wg_quest_garden` — progress 1 (first plant) and 10 (first harvest).

---

## 5. Engine compatibility notes

This expansion uses only standard Andor's Trail JSON shapes (items,
itemcategories implied, droplists, monsters, conversationlists, quests,
maps) and standard TMX event objects (`Spawn`, `MapChange`, `Sign`).
Two things are extension points your fork may need to support:

1. **`priceMultiplier` on droplist items** — Stendhal-style discounted
   shops. Your stock fork may not honor this field. If not, the easy
   patch is in `ItemController` (or wherever shop prices are computed):
   when reading a droplist entry, multiply the resulting price by
   `entry.priceMultiplier` (defaulting to 1.0). This is a ~3-line
   change.

2. **`timer` / `timer_elapsed` reward and requirement types** — see the
   gardening notes above. Either map them to long-duration actor
   conditions or add a wall-clock condition class.

If neither extension is in your fork, the gardening and butler-discount
features will silently degrade to "no discount" and "harvest is always
ready" respectively — everything else still works.

---

## 6. Map-painting checklist

Open each `.tmx` in Tiled and:

1. Replace the placeholder `<tileset>` references at the top with paths
   to your fork's actual `.tsx` files (the ones in `assets/tilesets/`).
2. Paint the **Ground** layer with floors, paths, grass, etc.
3. Paint the **Object** layer with walls, fences, stall awnings,
   counters, fireplaces, garden bedding, etc. The objects whose
   eventLayer Spawn names contain `sewing_machine`, `stove`, `forge`,
   `garden_plot` should sit visually on top of an obvious sprite so
   players know where to tap.
4. Paint the **Above** layer with rooflines, lanterns hanging down, etc.
5. Save. The eventLayer doesn't need to be touched — it already works.

---

## 7. Quick smoke test

1. Drop everything in, build the APK, launch on emulator.
2. Walk west out of Ados west gate. You should appear in
   `westgate_market`. (If not, you forgot to add the MapChange exit on
   `ados_outside_west.tmx`.)
3. Talk to Mira. Buy `wg_deed_home1` (5,000 g — give yourself gold via
   the debug build if needed). The cottage door should now open.
4. Inside, talk to the sewing machine, sew a Linen Hood.
5. Equip the Linen Hood. If it shows up in the head slot, the items,
   conversations, monsters, and droplists are all hooked up. Ship it.

— Built with care. Have fun.

---

## 8. Castle expansion (added in v2)

A second drop, **Westgate Castle**, is now bundled in the same archive.
The castle stands directly north of Westgate Market, next door to the
homes. It is laid out as a **5×3 grid of 15 separate rooms** on the
main floor, plus two underground floors (lower castle + dungeons), a
roof, and **four corner-tower lookouts**.

### 8.1 Map layout

**Main floor — 5×3 grid (each room is its own TMX, 16×12 tiles):**

| col 0           | col 1            | col 2          | col 3                 | col 4            |
| --------------- | ---------------- | -------------- | --------------------- | ---------------- |
| `castle_grove`  | `castle_garden`  | `castle_antichamber` | `castle_throne`  | `castle_workroom` |
| `castle_kitchen`| `castle_dining`  | `castle_hall`  | `castle_trophy`       | `castle_library`  |
| `castle_guest_west` | `castle_sunny_bedroom` | `castle_entry` | **`home`** *(jasia's bedroom — game loads here)* | `castle_guest_east` |

- Each room is connected to its neighbors via `MapChange` portals on
  the shared edges (north / south / east / west doors at the middle
  of each wall).
- **`home.tmx`** intentionally uses the bare name the engine looks for
  when loading the player's home map. Do not rename it.
- **`castle_entry`** has a south-edge `MapChange` to `westgate_market`
  (place `from_castle_entry`) — this is the public exit. It also has
  a `MapChange` going up to `castle_roof`.
- **`castle_hall`** has a `MapChange` going down to `castle_b1`.

**Lower castle — `castle_b1.tmx`:** central hall with four rooms
around it — armory, servant quarters, storage room, guards quarters.
Stairs down lead to `castle_b2`.

**Dungeons — `castle_b2.tmx`:** warden's office, armory, guard office,
and a hall opening onto **four prison cells**. Stairs back up only.

**Roof — `castle_roof.tmx`:** open roof area with stairs back down to
`castle_entry` and four corner stairwells, one to each tower.

**Towers — `castle_tower_nw.tmx`, `castle_tower_ne.tmx`,
`castle_tower_sw.tmx`, `castle_tower_se.tmx`:** each tower is the
"lookout level up" from its corner of the roof.

### 8.2 NPCs

All castle NPCs live in `res/raw/castle_monsters.json`. The roster
covers staff, servants, and guards as requested:

- **Royal**: Queen Sunny.
- **Staff**: Doorman Heric, Usher Pell, Majordomo Tovin, Head Cook
  Bertrade, Royal Gardener Wendel, Flower Keeper Lien, Scribe Adelyn,
  Curator Halric, Librarian Rosalee, Quartermaster Hannock, Armory
  Master Drake.
- **Servants**: generic servants populating the kitchen, dining hall,
  guest quarters, sunny's bedroom and the basement servant quarters.
- **Guards**: rank-and-file castle guards spread across the throne
  room, great hall, basement, dungeons, roof and towers, plus Captain
  Roderic (basement guards' quarters), Officer Maela (dungeons), and
  four tower lookouts.
- **Dungeon**: Warden Ulrec, Jailer Korm, four prisoners (one per
  cell).
- **Visitors**: two visiting nobles in the guest quarters.

### 8.3 Quests

All three are in `res/raw/castle_quests.json`. Conversations live in
`res/raw/castle_conversationlists.json`.

1. **`wg_castle_q_silverware` — The Queen's Silverware.**
   Majordomo Tovin (dining hall) sends you to recover a stolen silver
   set hidden in the basement storage room. Reward: 1,500 gold.
2. **`wg_castle_q_drill` — Tower Drill.**
   Captain Roderic (basement guards' quarters) asks you to make the
   rounds of all four corner-tower lookouts and report back. Reward:
   1,200 gold and a Captain's Token.
3. **`wg_castle_q_prisoner` — The Prisoner's Letter.**
   Warden Ulrec (dungeons) asks you to find a sealed letter in the
   castle library that exonerates a wrongly held prisoner. Reward:
   1,800 gold.

### 8.4 Tiled `.world` files

A `world/` folder is included in the archive. It contains Tiled
[multi-map world files](https://doc.mapeditor.org/en/stable/manual/worlds/),
using the documented schema:

```json
{
  "maps": [
    { "fileName": "../res/xml/castle_grove.tmx", "x": 0,   "y": 0,   "width": 512, "height": 384 },
    { "fileName": "../res/xml/castle_garden.tmx","x": 512, "y": 0,   "width": 512, "height": 384 }
  ],
  "type": "world"
}
```

There is a `.world` file **for each of the 15 main-floor levels**
(`castle_grove.world`, `castle_garden.world`, …, `home.world`,
`castle_guest_east.world`). Each one places its target room at its
true grid coordinates and includes the room's immediate grid neighbors,
so opening any per-room world in Tiled will let you edit that room
with its surroundings visible. The hall's per-room world also embeds
the basement, and the entry's per-room world also embeds the roof.

For full-castle editing, open **`world/castle_overview.world`**, which
positions every TMX (15 main-floor rooms + basement 1 + basement 2 +
roof + 4 towers) at sensible offsets relative to one another.

Per-floor worlds are also provided for the non-main-floor areas:
`castle_basement1.world`, `castle_basement2.world`, `castle_roof.world`,
`castle_tower_nw.world`, `castle_tower_ne.world`,
`castle_tower_sw.world`, `castle_tower_se.world`.

To use, open Tiled → **File → Open World…** and pick whichever world
file you want to edit in.

### 8.5 Notes on `home.tmx`

In Andor's Trail forks (jasias-quest included), the player's home map
is referenced by the canonical id `home`. We deliberately gave jasia's
bedroom the file name `home.tmx` and the map id `home` so that:

- the existing engine call to load the player's home will find it; and
- the `MapChange` doors from castle_sunny_bedroom (west) and
  castle_guest_east (east) target `home` directly.

If your fork already ships a `home.tmx`, decide whether to preserve
the original (rename ours to e.g. `castle_jasia_home.tmx` and update
the four references in `castle_sunny_bedroom.tmx`,
`castle_guest_east.tmx`, `castle_maps.json`, `loadresources.xml`,
`worldmap.xml`, and `home.world`) or replace your existing home with
this one.
