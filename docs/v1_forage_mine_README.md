# Foraging & Mining content pack for jasias-quest

A drop-in content pack for the [jasias-quest](https://github.com/jmlucas31070-dev/jasias-quest)
fork of Andor's Trail. Adds:

- A **foraging** system: bushes, berry patches, and nut trees you can search for
  herbs, fruit, mushrooms, twigs, etc.
- A **mining** system: rock outcrops, ore veins, and gem fissures that require
  an equipped pickaxe to work.
- A **daily reset** for both systems, gated by an in-game timer (~24 in-game
  hours, see *Tuning the cooldown* below).
- A **Python helper script** that injects spawn nodes into existing TMX maps
  from a small JSON config — so you don't have to edit hundreds of maps by hand.

Everything ships in the format Andor's Trail expects: JSON files in
`res/raw/`, the registration array in `res/values/loadresources.xml`, and TMX
overlay files in `res/xml/`.

---

## What's in the box

```
jasias_foraging_mining/
├── README.md
├── res/
│   ├── raw/
│   │   ├── itemcategories_foraging.json   # 8 new item categories
│   │   ├── itemlist_foraging.json         # 15 forageable items
│   │   ├── itemlist_mining.json           # 24 mining items + 3 pickaxes
│   │   ├── droplists_foraging.json        # 3 foraging droplists
│   │   ├── droplists_mining.json          # 4 mining droplists (low/mid/high/gem)
│   │   ├── conversationlist_foraging.json # bush dialogues + daily-reset gate
│   │   ├── conversationlist_mining.json   # rock dialogues + pickaxe gate
│   │   ├── monsterlist_foraging.json      # 3 forage "node" actor entries
│   │   └── monsterlist_mining.json        # 4 mining "node" actor entries
│   ├── values/
│   │   └── loadresources.xml              # full file with new entries registered
│   └── xml/
│       └── *.tmx                          # 8 sample modified maps (3 keep + 5 caves)
└── scripts/
    ├── generate_nodes.py                  # injects spawn areas into TMX maps
    └── nodes_config.json                  # sample node placements
```

---

## Installation

> **Backup your fork first.** This pack overwrites `loadresources.xml` and
> several TMX files.

1. Copy the contents of `res/raw/` into your fork's `AndorsTrail/res/raw/`.
2. **Replace** `AndorsTrail/res/values/loadresources.xml` with the version from
   `res/values/loadresources.xml`.
   (If you've already made changes to `loadresources.xml`, instead manually
   add the new entries — see *Manual loadresources patch* below.)
3. Copy the TMX files from `res/xml/` into `AndorsTrail/res/xml/`. They
   replace the empty-stub maps already in your fork for the same map IDs.
4. Build the project as usual (`./gradlew assembleDebug`, or open in Android
   Studio).

---

## How it works

### Foraging nodes

Each forage node is implemented as a 1-HP, 0-damage "monster" of class
`animal`. The player can interact with it (no combat needed) which fires a
dialogue. The dialogue is a **selector** with three replies, evaluated in
order:

1. *(hidden — auto-selected if the daily timer hasn't elapsed yet)*
   → routes to `fm_forage_already`: "You have already gathered everything
   useful from here. Come back tomorrow."
2. *"Search through the brush." / "Pick the berries." / "Gather what you can."*
   → routes to the `_take` dialogue, which awards the appropriate droplist
   **and** creates the daily timer.
3. *"Leave it alone."* → exits cleanly.

When the player picks reply 2, the engine grants:

- `dropList` reward for the appropriate tier (`fm_drop_forage_common` /
  `_berry` / `_nut`).
- `createTimer` reward for `fm_t_forage_<tier>`. The next time reply 1's
  `timerElapsed` requirement evaluates, it returns true (with `negate: true`
  flipping it to false) until 3456 game rounds (~24 in-game hours at 25 s
  per outdoor round) have passed.

### Mining nodes

Same pattern, with one extra reply at the top: a `wear` requirement on the
pickaxe categories. If the player isn't wearing any pickaxe, the dialogue
falls through to `fm_mine_no_pick_branch` ("There is workable rock here, but
you would need a pickaxe…").

| Tier | Spawn group ID | Pickaxe required |
| --- | --- | --- |
| `mine_low` | `fm_node_mine_low` | wood, iron, or steel |
| `mine_mid` | `fm_node_mine_mid` | iron or steel |
| `mine_high` | `fm_node_mine_high` | steel only |
| `mine_gem` | `fm_node_mine_gem` | iron or steel |

> **Note on pickaxe progression.** Pickaxes are equipped in the weapon slot,
> so the player gives up a real weapon to mine. The wood pickaxe is
> deliberately weak in combat (1–2 damage). The seamstress / blacksmith / city
> shop where players buy pickaxes isn't part of this pack — drop the items
> into any existing shopkeeper's droplist, or hand them out via a quest, etc.

### Daily reset trade-off

The timers are **per tier**, not per node. That means after the player picks
*any* common-tier forage node anywhere on the map, all common-tier nodes
across the world are locked for ~24 in-game hours. This was a deliberate
trade-off to keep the dialogue list small (one set per tier, not one per
node).

If you want **per-map** or **per-node** cooldowns, regenerate the
`conversationlist_*.json` files with unique timer/dialogue IDs per node, and
update each spawn area to point at the right phrase. The Python script can
be extended to do this — the `_take` dialogues just need a unique
`createTimer.rewardID` per node.

### Tuning the cooldown

The "3456 rounds" value in each `_pick`/`_strike` dialogue selector
corresponds to 24 hours at 25 seconds per outdoor round. To change it,
search-and-replace `"value": 3456` in:

- `res/raw/conversationlist_foraging.json`
- `res/raw/conversationlist_mining.json`

Some useful conversions:

| Wall-clock target | Rounds to use |
| --- | --- |
| 1 hour            | `144` |
| 6 hours           | `864` |
| 12 hours          | `1728` |
| 24 hours          | `3456` |
| 48 hours          | `6912` |

---

## Adding more nodes to more maps

The repo has hundreds of TMX maps. The included `scripts/generate_nodes.py`
edits them in batch:

```bash
python3 scripts/generate_nodes.py \
    --config scripts/nodes_config.json \
    --maps-in  AndorsTrail/res/xml \
    --maps-out AndorsTrail/res/xml      # write back in place
```

The config is a flat JSON mapping `map_id -> [{x, y, tier}, …]` where `x` and
`y` are **tile** coordinates (0..31 on a 32x32 map). The script:

- finds the map's `<objectgroup name="Spawn">`,
- inserts one `<object type="spawn">` per node, named `fm_node_<tier>_<n>`,
- pixel-converts coords (`x*32`, `y*32`),
- preserves all other content in the file.

The 8 sample maps in `res/xml/` were produced by running this script against
the maps shipped in the jasias-quest repo at the time of writing, using the
sample config in `scripts/nodes_config.json`. They serve as worked examples;
expand the config to cover the rest of your world.

> **Tip.** To find walkable tiles on a map you don't know, open the TMX in
> Tiled — the "Walkable" layer marks unwalkable tiles with the top-left
> sprite of `map_trail_1`. Empty tiles in that layer are walkable, so any
> empty position is a valid node placement.

---

## Manual loadresources patch

If you'd rather merge by hand than overwrite, add these lines inside the
existing arrays in `AndorsTrail/res/values/loadresources.xml`:

```xml
<array name="loadresource_itemcategories">
    ...
    <item>@raw/itemcategories_foraging</item>
</array>
<array name="loadresource_items">
    ...
    <item>@raw/itemlist_foraging</item>
    <item>@raw/itemlist_mining</item>
</array>
<array name="loadresource_droplists">
    ...
    <item>@raw/droplists_foraging</item>
    <item>@raw/droplists_mining</item>
</array>
<array name="loadresource_conversationlists">
    ...
    <item>@raw/conversationlist_foraging</item>
    <item>@raw/conversationlist_mining</item>
</array>
<array name="loadresource_monsters">
    ...
    <item>@raw/monsterlist_foraging</item>
    <item>@raw/monsterlist_mining</item>
</array>
```

Order does not matter for the engine, but do keep one `<item>` per line for
diff sanity.

---

## Known caveats

- **Item icon indices are best-guess.** I used safe-looking sprite indices
  (`items_misc:0..17`, `items_consumables:0..10`, `items_jewelry:0..7`,
  `items_weapons:0..2`, `monsters_insects:0..6`). If a sprite looks wrong
  in-game, just adjust the `iconID` value to a sprite that does exist in
  your spritesheets.
- **Foraging "monster" sprites.** Forage and mine nodes appear in-game as
  whatever sprite you assign in `monsterlist_foraging.json` /
  `monsterlist_mining.json`. The shipped values point at `monsters_insects:n`
  as placeholders — swap to bush/rock sprites once you have art for them.
- The pack does not add NPCs that *sell* pickaxes or *buy* ore. That belongs
  in a follow-up content pack (or in the smithing/cooking systems planned
  for later).
- The 3-minute map-respawn behaviour of Andor's Trail (`Constants.java →
  MAP_UNVISITED_RESPAWN_DURATION_MS`) will cause the bush/rock sprites
  themselves to reappear quickly even within the daily cooldown. The
  dialogue gate is what enforces "one drop per day" — players will see the
  node respawn and be told they've already gathered there.
