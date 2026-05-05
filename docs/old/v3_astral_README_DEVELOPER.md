# Astral Beasts — Developer README

A drop-in content mod for the **jasias-quest** fork of **Andor's Trail**.
It adds an original creature-collection minigame ("Astral Beasts") that
the player launches from a console in **Jasia's bedroom** (`home.tmx`)
and **Sunny's bedroom** (`castle_sunny_bedroom.tmx`).

This mod is content only — no Java engine changes. Every entry uses
existing Andor's Trail JSON / TMX schemas, so it loads as-is once the
resource arrays in `loadresources.xml` reference the new files.

---

## 1. What's in the box

```
res/values/
    loadresources.xml         ADDITIVE fragment — merge into base loadresources.xml
    strings.xml               1010 lines — all new strings (hand + generated)

res/xml/
    worldmap.xml              Reference index of the 9 regions (read by author, not engine)
    home.tmx                  MODIFIED — adds Astral Console next to Jasia's wardrobe
    castle_sunny_bedroom.tmx  MODIFIED — adds Astral Console on Sunny's side table

    ab_<region>_<sub>.tmx     45 region maps (9 regions × 5 sub-maps each).
                              Emberlands is fully authored; the other 8 regions
                              are functional skeletons with NPC spawns + door
                              wiring — re-tile in Tiled to taste.
    level_0.world ..
        level_7.world         8 Tiled world files arranging each region's 5
                              sub-maps spatially. Open in Tiled (File → Open →
                              level_N.world) to see and edit a whole region as
                              a single canvas. Voidmarsh (region 9) has TMX
                              skeletons but no .world file — it is the endgame
                              zone reached only via the Astral Console.

res/raw/
    ab_actorconditions.json     281 entries  (creature spells + trainer ranks + jinx)
    ab_itemcategories.json        6 entries  (orb, beast equip, evostone, incense, dex, pass)
    ab_items.json               305 entries  (5 orb tiers, 270 beast equip, 10 stones, 9 dex, 9 passes, incense)
    ab_droplists.json            20 entries  (starter kit, gym/champion drops, jinx roll)
    ab_quests.json               39 entries  (trainer-rank, 9 dex, 9 gym, 9 team, 9 champion, master, endgame)
    ab_conversationlists.json   679 entries  (console, capture/fight branches, all NPC dialogues)
    ab_monsters.json            343 entries  (console object, 8 NPCs × 9 regions, 270 wild forms)
    ab_maps.json                 45 entries  (9 regions × 5 sub-maps each)

build/
    generate.mjs              The data generator. Re-run to extend the roster.
    strings_generated.xml     Raw output of the generator (already merged into strings.xml).

README_DEVELOPER.md           This file.
README_PLAYER.md              Hype-style player-facing intro.
```

---

## 2. Installing into your fork

Working from the root of `jasias-quest/AndorsTrail/`:

1. **Copy `res/raw/ab_*.json`** into `AndorsTrail/res/raw/`. They're prefixed
   `ab_` so they will not collide with anything in the base game or the
   existing `jq_*` / `castle_*` / `westgate_*` content.
2. **Copy `res/xml/home.tmx` and `res/xml/castle_sunny_bedroom.tmx`** over the
   existing ones. The diffs vs upstream are minimal — see the `<!-- ASTRAL
   BEASTS -->` comment blocks in each file. Only one Spawn + one Sign are
   added per map.
3. **Copy `res/xml/worldmap.xml`** into `AndorsTrail/res/xml/`. This file is
   a developer reference (used when authoring the region TMX files); it
   is not auto-loaded by the engine.
4. **Merge `res/values/loadresources.xml`** into the existing
   `AndorsTrail/res/values/loadresources.xml`. The shipped file is a
   *fragment*: each `<array>` block lists only the new `<item>` lines you
   need to insert into the matching array in the base file. Do **not**
   replace the file wholesale.
5. **Merge `res/values/strings.xml`** into the existing
   `AndorsTrail/res/values/strings.xml`. The shipped file holds 974
   generated strings plus a small hand-written header section. Insert
   everything between the two long comment banners into the base
   `<resources>` block.
6. **Build** with `./gradlew assembleDebug` from `AndorsTrail/`. The mod
   is content only; no manifest or Gradle changes are required.

---

## 3. Story layout

Jasia and her sister Sunny each have a slim crystal **Astral Console** in
their bedrooms. The Console projects them — and the player — into a
parallel layer of the world where the **Astral Beasts** roam. There are
nine regions in this layer, one for each elemental clade:

| # | Region         | Clade       | Element    | Hub town       | Gym Leader  | Champion   | Eclipse Admin |
|---|----------------|-------------|------------|----------------|-------------|------------|---------------|
| 1 | Emberlands     | Cinderkin   | fire       | Ashbridge      | Pyralis     | Ignara     | Solrin        |
| 2 | Tideholm       | Tidefolk    | water      | Saltspire      | Marenna     | Coralax    | Brackwell     |
| 3 | Verdant Reach  | Verdant     | grass      | Mossglen       | Ferna       | Sylvane    | Thornell      |
| 4 | Stormcrest     | Stormborn   | lightning  | Boltreach      | Volta       | Tempyx     | Kestrel       |
| 5 | Frostvale      | Rimekin     | ice        | Hoarwatch      | Crysell     | Glacira    | Borissa       |
| 6 | Stoneheart     | Geokin      | earth      | Granitemarch   | Korran      | Tellurik   | Quarrick      |
| 7 | Duskwood       | Shadeborn   | shadow     | Hollowfen      | Nyxara      | Umbros     | Vellis        |
| 8 | Aetherspire    | Aetherborn  | light      | Highmere       | Solarya     | Lumiel     | Halen         |
| 9 | Voidmarsh      | Wyrmkin     | void       | Greylight      | Morrigane   | Voidrak    | Sablehex      |

The shared antagonist is **Team Eclipse**, a syndicate that wants to
"dim the sky" over each region in turn. They run a hideout per region,
fronted by the Admin in the table above and a stable of grunts.

After all nine champions are defeated, the **Long Tournament** end-game
quest fires (`ab_quest_endgame_reset`): every gym and champion is
flagged for a re-run at higher difficulty.

---

## 4. Maps changed

Only two TMX files are shipped as modified:

* `res/xml/home.tmx` — Jasia's bedroom. Added one Spawn (`ab_obj_computer`)
  at tile (12, 8) and a matching Sign one tile south. No other tiles or
  objects were altered.
* `res/xml/castle_sunny_bedroom.tmx` — Sunny's bedroom. Added one Spawn
  (`ab_obj_computer`) at tile (3, 3) and a Sign one tile south.

The console NPC is defined as a stationary "object" monster
(`ab_obj_computer`) with `phraseID: ab_console_boot`. Talking to it opens
the Astral Console dialogue tree.

### Region maps (shipped)

All nine regions are wired in JSON (NPCs, dialogues, quests, drops,
spawns) and registered in `ab_maps.json`. **All 45 region TMX files are
also shipped** in `res/xml/`:

```
ab_<region>_center.tmx    Beast Center hub. Spawns the 4 NPCs:
                          ab_npc_<region>_{clerk,professor,breeder,shopkeeper}
                          plus an exit MapChange back to home.tmx.

ab_<region>_route.tmx     Wild zone. Three "wild_patch" spawn areas seeded
                          with the region's three lowest-tier species. Doors
                          to center (W), gym (E), and hideout (S).

ab_<region>_gym.tmx       Interior. Two team grunts as trial keepers + the
                          ab_npc_<region>_gymleader at the back. Door east
                          to the champion arena.

ab_<region>_hideout.tmx   Interior. Four team grunts and the
                          ab_npc_<region>_team_admin at the back.

ab_<region>_champion.tmx  Arena. ab_npc_<region>_champion only — already
                          gated in dialogue by requireItem ab_pass_<region>.
```

**Two worked examples ship richer than the rest:**

- **Emberlands** (`ab_ember_*.tmx`, `level_0.world`) — varied tile
  palette (border + striped body), an Above-layer decoration set
  (crates, barrels, lanterns, banners), and one welcome sign per
  sub-map.

- **Tideholm** (`ab_tide_*.tmx`, `level_1.world`) — same tile/decor
  treatment as Emberlands, **plus** two optional side-quest NPCs and
  three side-quest signs:
  - `ab_npc_tide_lighthouse_keeper` (in `ab_tide_center.tmx` at tile 6,9)
    starts the **Saltspire Lantern** quest.
  - `ab_npc_tide_pearl_diver` (in `ab_tide_route.tmx` at tile 8,10)
    sells the lantern bead for 200g (after the keeper sends you) and
    runs the **Tideholm Pearl Survey** quest, which awards a
    "Pearl Token" once you hold the Tideholm Crest.
  - Three lore signs: a Saltspire harbour notice, a Beast Center hours
    sign, and a shoreline notice plus a pier sign on the route.
  - Two quest items (`ab_q_tide_lantern_bead`, `ab_q_tide_pearl_token`),
    one droplist (`ab_drop_tide_lantern_reward` — 2× Great Orbs), six
    new dialogues, and two new entries in `ab_quests.json`. All of it is
    declared in `build/generate.mjs` under the
    `Side-quest content (Tideholm worked example)` section — copy that
    block, search-and-replace `tide`/`Tideholm` for the next region you
    want to flesh out.

The other six main-progression regions plus Voidmarsh are functional
**skeletons** — every NPC, door, and spawn area is in place and each
region is fully playable, but the ground tile is uniform (tile id 1),
the Above layer is empty, and there is only the bare minimum of signs.
Open the matching `level_N.world` file in Tiled and re-tile / decorate
to taste.

The shipped `loadresources.xml` fragment includes a `loadresource_tmx`
block listing all 45 region TMX paths; insert those lines into the
existing `loadresource_tmx` array in your base `loadresources.xml`.

### Tiled world files

Eight `.world` files (`level_0.world` … `level_7.world`) sit in
`res/xml/` and arrange each region's five sub-maps as a single Tiled
canvas. The layout is:

```
                      [gym  (1024,-384)]
[center (0,0)] [route (512,0)] (gap) [champion (1536,0)]
                      [hideout (1024, 384)]
```

Coordinates are in pixels (each sub-map is 16×12 tiles × 32 px = 512×384 px).

| File           | Region        |
|----------------|---------------|
| level_0.world  | Emberlands    |
| level_1.world  | Tideholm      |
| level_2.world  | Verdant Reach |
| level_3.world  | Stormcrest    |
| level_4.world  | Frostvale     |
| level_5.world  | Stoneheart    |
| level_6.world  | Duskwood      |
| level_7.world  | Aetherspire   |

In Tiled, **File → Open → level_N.world** loads all five sub-maps at
once for that region. Voidmarsh's five TMX files are shipped (so
`ab_maps.json` resolves and the endgame quest works) but no `.world`
file ships for it — it is reached only via the Astral Console after
the Voidmarsh champion is defeated, and is intentionally laid out
differently from the eight main-progression regions. Author your own
`level_void.world` if you want to see it on a single canvas.

`worldmap.xml` (also in `res/xml/`) gives canonical grid coordinates
for each region's slot on the in-game world map and is read by
developers when authoring the per-map `<namedArea>` objects.

---

## 5. Mechanics

### Capture vs fight
Each wild beast has its own dialogue
(`ab_wild_capture_<species>[_form]`) with three replies:

* **Fight it.** → hands off to Andor's Trail combat (`nextPhrase: "FIGHT"`).
* **Throw a Spirit Orb.** → consumes one orb of the appropriate tier and
  branches into `ab_capture_roll_<species>[_form]`.
* **Back away.** → exits.

The roll dialogue gates the success reply with two AT-native checks:
* `requireQuestProgress` against `ab_quest_trainer_level` at a tier-
  specific threshold (1 → 50 across the nine tiers, +5 for shiny / variant).
* `requireConditionImmunity: ab_cond_jinxed` — if the player is jinxed
  the orb shatters.

Successful captures award a **Bound `<species>`** equipment item and
advance the matching regional dex quest by ten progress per species.

### "Tiny percent fail chance"
Andor's Trail dialogue is deterministic, so the random fail is modelled
as a 2 % chance to receive `ab_cond_jinxed` from the
`ab_drop_jinx_chance` droplist (rolled on every successful catch). The
condition lasts until cleared and blocks the next capture attempt. If
you'd rather not have it, delete the `rewardDropList: ab_drop_jinx_chance`
line from each `ab_capture_roll_*` reply in `ab_conversationlists.json`.

### Trainer rank (1 → 100)
Modelled as a 100-stage quest (`ab_quest_trainer_level`). Stage 1 is
awarded by the Astral Console's "Begin a new journey" reply; subsequent
stages are awarded by gym wins, champion wins, dex turn-ins, and team
victories — wire in additional `rewardQuestStage` entries wherever you
want to grant rank progression. The progression is intentionally split
across many sources so the player can hit rank 100 by completing all
nine regions plus the master dex.

### Equipment slots
Each beast is also an equipment item that slots into a standard AT slot
and adds the beast's signature spell as an equipped condition.

* **Weapon slot** — region legendary (one per region; nine total).
* **Shield slot** — region mythical (one per region; nine total).
* **Body / head / hand / feet / ring / neck** — every other species,
  rotated so each slot is filled across the nine regions.

Shiny and variant forms occupy the same slot as the base form but carry
a stronger version of the same spell (×1.25 and ×1.10 respectively).

### Evolution
Visit any region's breeder (`ab_<region>_breeder_greet`). They show a
menu of the chained species in that region; selecting one consumes the
matching beast item plus a `<region> Stone` (`ab_stone_<region>`) and
returns the next-stage beast item. A universal `Resonant Shard`
(`ab_stone_resonant`) item is also defined for free-form upgrades — wire
its consumption in if you want.

### Breeding
Same breeder, "Breed a pair." Consumes a `Pair Incense` and returns the
region's stage-1 starter beast (placeholder behaviour — extend to a
full pairing matrix if you want unique offspring tables).

### Region access / champion gating
Each gym leader's dialogue rewards `ab_pass_<region>` on victory. The
champion's dialogue requires that pass before the fight is offered, and
on victory the next region's Console travel reply unlocks because that
reply requires `ab_pass_<region>` of the just-defeated region.

### Dex quests
Nine `ab_quest_dex_<region>` quests, each progressed by 10 per unique
species captured (so 10 captures = 100 progress = quest finished).
A meta-quest `ab_quest_master_dex` recognises the player as a Master
once all nine are done — wire its kickoff into a final NPC at the
Aetherspire or Voidmarsh dex turn-in if you want a celebratory cutscene.

### End-game reset
`ab_quest_endgame_reset` ("The Long Tournament") is defined and ready;
trigger its first stage from a final NPC after the Voidmarsh champion
to flag every gym/champion dialogue for re-fight. Andor's Trail does
not natively reset NPC death, so the simplest implementation is to
duplicate each gym/champion NPC with `_rematch` suffixes and gate them
on the tournament quest stage.

---

## 6. Extending the roster

Edit `build/generate.mjs`:

* Add or rename creatures inside the `speciesFor()` `root` object.
* Add new regions to the `REGIONS` array (and a corresponding row in
  `worldmap.xml`).
* Add new forms to the `FORMS` array (e.g. an "Eclipsed" form).

Then re-run `node generate.mjs` from the `build/` folder. It rewrites
all eight JSON files and the strings fragment in place. Re-merge the
strings fragment into `res/values/strings.xml`.

The existing slot rotation (`SLOT_ROTATION`) can be re-balanced if you
add many more species; nothing else in the script needs to change for
larger rosters.

---

## 7. Known limitations

* The nine region TMX maps are not shipped (see §4 *Maps to author*).
  Everything else needed to play is in this drop.
* AT dialogue's only randomness is the droplist roll; the "tiny percent
  catch fail" therefore manifests as a Jinxed status applied with 2 %
  chance after a successful catch, not as a missed throw.
* `requireItem_2`, `consumeItem_2`, `rewardQuestStage_2` are used in a
  handful of dialogue entries (the breeder evolution menu and the
  Console journey-start reward). Andor's Trail's vanilla schema accepts
  one of each per reply; if your engine fork was built before the
  multi-reward patch, split those replies into chained phrases. The
  jasias-quest fork already supports the multi-reward fields used by
  the bank dialogues, so this should work as-is.
* The Astral Console uses tile coordinates that assume the upstream
  bedroom layouts are unchanged. If you've already moved Sunny's bed,
  re-position the console object in the modified TMX.
