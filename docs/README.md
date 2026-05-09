# Andor's Trail Extended Content Pack v2
## Developer Reference

### What's Included

| Category | Count |
|---|---|
| TMX Map Files | 33 |
| JSON Data Files | 16 |
| String Entries | 9878 |
| Regions | 23 |
| Unique Items | 600+ |
| Unique Monsters/NPCs | 900+ |
| Quests | 200+ |
| Conversations | 600+ |
| Actor Conditions | 200+ |
| Astral Beasts | 270 + 30 breeding |
| Dragon Types | 10 standard + 2 ancient |
| Races/Factions | 15 |
| Holidays | 6 |
| Personal Events | 4 |

---

### TMX Map Files
- `template_crafting.tmx`
- `template_guild.tmx`
- `template_faction.tmx`
- `faction_hall.tmx`
- `template_quests.tmx`
- `template_pokemon.tmx`
- `template_holiday.tmx`
- `template_overworld.tmx`
- `home.tmx`
- `house.tmx`
- `astral_spire.tmx`
- `lpc_church.tmx`
- `ring_clearing.tmx`
- `swamp_witch.tmx`
- `drow_cave.tmx`
- `lloth_realm.tmx`
- `volcano.tmx`
- `castle.tmx`
- `crystal_towers.tmx`
- `haunted_house.tmx`
- `haunted_mansion.tmx`
- `haunted_prison.tmx`
- `graveyard.tmx`
- `crypt.tmx`
- `mausoleum.tmx`
- `moon_red.tmx`
- `moon_orange.tmx`
- `moon_yellow.tmx`
- `moon_green.tmx`
- `moon_blue.tmx`
- `moon_indigo.tmx`
- `moon_violet.tmx`
- `pokemon_gym.tmx`

---

### Map Layer Structure
Every TMX map follows the Andor's Trail template exactly:
```
Tilesets: dc-dngn (gid 1), dc-dngn-t (gid 257), chars0 (gid 513), items (gid 769)
Tile Layers (base64+gzip encoded):
  Ground    — filled with GID 1 (floor tile)
  Walkable  — filled with GID 257 (walkable marker)
  Objects   — empty (GID 0)
  Above     — empty (GID 0)
  [+ holiday variant layers where applicable]
Object Layers — Spawn_*, Keys_*, Replace_* layers
```

---

### Pickpocket System
NPC conversation `conv_pickpocket_action` is placed on all 200 pickpocket target NPCs.
- **Thief 1+**: 50% pickpocket chance → **30 gold** base
- **Thief 6+ (Sneak)**: 75% chance → scaled gold
- **Thief 9+ (Hide)**: 90% chance → maximum gold
- **Other guilds**: Battle option only
- **Kill drop**: random gold 1–19g (always under 20)
- **Caught**: `mapChange` to jail, lawyer arranges bail for 100g

Gold per level: L1:30g, L2:50g, L3:75g, L4:110g, L5:150g, L6:200g, L7:275g, L8:360g, L9:460g, L10:600g

---

### Timekeeper / Holiday System
A single NPC (`npc_timekeeper`, conversation `conv_timekeeper`) handles ALL holidays.
Place this NPC in any city. The conversation branches by date condition:

**Between holidays:**
- Tells player the current date
- Shows the next upcoming holiday
- Accepts the Time Crystal quest (carry crystal for 7 days)

**During a holiday window:**
- Becomes the holiday host NPC
- Gives 1 daily gift (gold + themed items; better gifts if quest complete)
- Offers the 4-part holiday quest
- Manages layer replacement (Objects_*, Above_*, Walkable_*) automatically

**Holiday Schedule:**
- New Year's: 01-01 ± 1 week
- Easter: 04-09 ± 1 week
- Fourth of July: 07-04 ± 1 week
- Halloween: 10-31 ± 1 week
- Thanksgiving: 11-23 ± 1 week
- Christmas: 12-25 ± 1 week

**Events** (birthday, graduation, wedding, funeral): 24 hours, arranged by event planner NPC for 500g.

**Implementation:**
- Holiday active: `ac_holiday_active_{id}` condition
- Gift given today: `ac_holiday_gift_given_{id}` condition (resets daily)
- Quest complete: `ac_holiday_quest_done_{id}` condition (permanent, enables good gifts)
- Layer trigger objects in `Replace_holiday_{id}` layer use `startDate`, `weeksBefore`, `weeksAfter` properties

---

### Guild System
6 guilds: Adventurer, Fighter, Thief, Mage, Cleric, Druid
- One active at a time (excluding Adventurer)
- Leave/rejoin preserves progress; abilities require active membership
- 12 quests per guild for advancement

**Crafting gates:**
| Station | Guild | Min Level |
|---|---|---|
| Fighter's Forge | Fighter | 3 |
| Mage/Cleric/Druid Desks | Respective | 3 |
| Cauldron | Mage/Cleric/Druid | 6 |
| Door Pick | Thief | 3 |
| Key Craft | Thief | 3 |
| Bank Robbery | Thief | 12 |

---

### Door Mechanics
- **Key/Master Key**: immediate open
- **Pick Lock**: 4 lockpick tiers (20%→80% success), thief level reduces failure
- **Bash**: Fighter 1+ (30%), Fighter 5+ (60%)
- **Inspect**: any thief level → enables key crafting
- **Door Pass Scroll**: Mage/Cleric/Druid 3+

---

### Home System
| Size | Features | Cost |
|---|---|---|
| Small | Console, Computer, Stove | 500g |
| Mid | + Garden, Bench | 1000g |
| Large | + Both Forges | 2000g |
| Luxury | + Butler (5% shop discount) | 4000g |

Butler sets `butler_discount_active` condition → shops check this for 5% discount.

---

### Main Quest Chain
1. **Rumor Board** → Swamp Witch quest (swamp_witch.tmx)
2. **Swamp Witch**: 4 monster drops + 1 foraged item → Sunny went to Drow Caves
3. **12 Sunny Info Quests** → open Drow Cave quest
4. **Drow Cave** (drow_cave.tmx): guard + leader + witch (12 ingredients: 6 from cave animals, 6 foraged)
5. **Spell → Lloth's Realm** (lloth_realm.tmx): Lloth gives ring, sends to Volcano
6. **Volcano** (volcano.tmx): 10 dragon types × 4 ages; adult dragon quests
7. **Ancient Dragons** (Platinum + Chromatic): gated on all 10 adult quests complete
8. **Ring activates** → map change back to Lloth; Sunny transformed into Drow Elf
9. **Ring Clearing** (ring_clearing.tmx): find Sunny's ring via search area
10. **Drow Villages + 7 Moons** (moon_*.tmx): drow quests per moon
11. **Family Reunion**: Sunny + Ozzy + Nymph → Sunny ascends → rich reward

---

### Dragon Quest Gate
`quest_dragon_ancient_platinum` and `quest_dragon_ancient_chromatic` require:
`requiresAllQuestsComplete` = [quest_dragon_bronze_adult, quest_dragon_brass_adult, quest_dragon_copper_adult, quest_dragon_silver_adult, quest_dragon_gold_adult, quest_dragon_white_adult, quest_dragon_black_adult, quest_dragon_green_adult, quest_dragon_blue_adult, quest_dragon_red_adult]

---

### Astral Beasts (Pokémon System)
- 270 beasts: 9 regions × 10 base beasts × 3 evolution tiers
- 30 additional breeding beasts
- Spirit Orb catch rates: Orb I=25%, II=50%, III=75%, IV=95%
- Evolve via Scholar NPC (gold cost per tier)
- Breed via Breeder NPC (consumes both beasts, creates 1 new)
- 9 regional gyms: 12 trainers + 1 gym leader + 1 champion each
- Grand Champion after all 9 regional champions defeated
- **Prevention zones**: `Keys_prevent_pokemon` strips equipped beasts in real world; `Keys_prevent_overworld` strips real gear in game worlds

---

### Crystal Towers
12 colored towers (4 mage, 4 cleric, 4 druid), 5 levels each.
Each level: 5 progressively harder mage/cleric/druid mobs.
Crystal Grandmaster accepts all 12 crystals → Grand Crystal Staff.

---

### Ailment System
24 ailments applied by specific monsters.
Castle alchemist sells cure potions. 6 monsters per ailment drop the cure.

---

### Faction System
15 races with D&D-standard attitudes toward the player (wood elf).
Quest completion: raises own faction score, lowers rival's.
Disguises sold in faction_hall.tmx — chance to negate hostile faction attacks.

---

### Integration Checklist
1. Copy all `.tmx` files to your `maps/` directory
2. Copy all `.json` files to your `content/` directory  
3. Merge `values/strings.xml` entries into your app's string resources
4. Add `values/loadresources.xml` entries to your resource loading list
5. Tileset image files required: `dc-dngn.png`, `dc-dngn-t.png`, `chars0.png`, `items.png`

---

*Andor's Trail Extended Content Pack v2 — Generated May 2026*
