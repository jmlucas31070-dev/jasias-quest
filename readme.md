# Jasia's Quest

Jasia's Quest is a single-player quest-driven roguelike fantasy dungeon crawler RPG with a powerful story.

Uncover the truths about your sister Sunny. Battle fierce monsters, gain experience and levels. Solve quests, find hidden treasures and improve your equipment.

While it may feel like the Andor story for a girl, but it's not. The quest is completed, just not by you.

https://discord.gg/ck8zGyANMb

## Contributing

For now, contact me in discord if you want to work on some of the maps. 
Check [here](https://stendhalgame.org/) for reference.
Each of their maps is 128x128 tiles, so loads of open space to plop maps into at 32x32 tiles each.
I need the 2 mountains for story content, and ados. Other than that I'm open to ideas.
As you can tell there are not many restrictions, ie.. computers in a castle.

## Andor's Trail

Source code is the Andor's Trail with the game removed and replaced with mine.
All bugs belong to me at this point. *wink*

## News/Updates

* **Addition 1**:
- A **foraging** system: bushes, berry patches, and nut trees you can search for
  herbs, fruit, mushrooms, twigs, etc.
- A **mining** system: rock outcrops, ore veins, and gem fissures that require
  an equipped pickaxe to work.
- A **daily reset** for both systems, gated by an in-game timer (~24 in-game
  hours, see *Tuning the cooldown* below).
- A **Python helper script** that injects spawn nodes into existing TMX maps
  from a small JSON config — so you don't have to edit hundreds of maps by hand.

* **Addition 2**:
Adds a universal banking system: deposit/withdraw, loans,
lockbox storage, and droplist-backed mystery caches. Every branch shares
a single ledger because all state lives on the player (inventory items +
quest progress).

* **Addition 3**:
This expansion adds a brand-new neighborhood — **Westgate Heights** —
just outside Ados's west gate, plus four buyable player homes and a
full-loop crafting economy: sewing, cooking, gardening, and forging.

* **Addition 4**:
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

* **Addition 5**:
Adds a full main quest, supporting cast, central
narrative maps, and 7 colored moons (each a 3×3 region grid).

* **Addition 6**:
This expansion adds a large new world to jasias-quest using the Andor's Trail engine.
Main island (14 regions west→east), 8 offshore islands, plus many side areas.

* **Addition 7**:
adds an original creature-collection minigame ("Astral Beasts") that
the player launches from a console in **Jasia's bedroom** (`home.tmx`)
and **Sunny's bedroom** (`castle_sunny_bedroom.tmx`).

* **Addition 8**:
This expansion adds a comprehensive faction warfare system to Jasias Quest (Andor's Trail fork).
It introduces 14 player-affecting factions, 1,400 unique NPCs, seasonal holiday events,
guild-based stealth abilities, and a grand tournament system.

* **Addition 9**:
This expansion adds the Nine Mage Tower quest chain to Jasias Quest (Andor's Trail fork).
Nine towers, each with 4 combat floors + 1 boss floor, yield a colored crystal. A 10th tower
(the Tower of Convergence) is where all nine crystals unlock the grand reward.
Additionally: 9 unique outside quest-giver mages, 24 world NPCs, and 9 side quests.
* **Addition 10**:
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

* **Addition 11**:
This addon adds a full party system, 20 pubs with unique recruitable NPCs,
an Adventurers Guild, five specialty guilds, 24 standard quests plus one 6-part
epic quest, spell scrolls as ring-slot equipment, guild recall scrolls, a cleric
shop, a mage scroll shop, and a trophy case to jasias-quest.

* **Addition 12**:
This addition pack expands jasias-quest with:

- **10 Libraries** with Scholar NPCs who teach crafting skills
- **5 Guild Systems** (Fighter, Thief, Mage, Cleric, Druid) with tiered rank progression and persistent skills
- **7 Crafting Skills** (Foraging, Mining, Cooking, Sewing, Gardening, Weapon Forging, Armor Forging)
- **200 Pickpocketable Townspeople** spread across existing maps
- **Full Crafting System** with recipes for weapons, armor, cloth, food, potions, scrolls, wands, and staffs
- **Wands and Staffs** for all player-craftable spells
- **Recall Scrolls** for Mage, Cleric, Druid, and Adventurer's guilds
- **Home Furnishings** system (computer, game console, writing desk, cauldron, wand/staff crafting tables)
- **Astral Beast World** logout matching the MUD logout procedure
- **Template maps** for loot houses and crafting rooms

* **Updates and future**:
Removed all stendgal levels and interiors from maps and loadresources.
Unused maps in unused directory. Got it down to 3228 maps. Still needs more pruning.
Working on the level 0 maps to ensure that main map will work and look proper. Then I can tackle the castle and the main story.

### Andor's Trail Content Studio
A Win/Mac/Linux content creator/editor available [here](https://andorstrail.com/viewtopic.php?f=6&t=4806).
This totally works still and I'm going into this assuming to delete many of the stendhal tilesets, so always will.

## APK Downloads

No downloads, just raw src code. Sorry.

## Authors

It's all on these guys below. I'm an over-achiever at best.
Added Stendhal source readme and license to repo.

**Created &amp; originally programmed by Oskar Wiksten**

### Development team

* **Oskar Wiksten** - *Creator* [Github Profile](https://github.com/oskarwiksten/)
* **Kevin (Zukero)** - *Lead Developer* [Github Profile](https://github.com/Zukero/)
* **Scott Devaney** **\*** - *Community Advocate* [Game Forums](https://andorstrail.com)
* **Richard Jackson** **\*** - *Lead Content Wrangler* 
* **Ian Haase** - *Lead Cartographer* 
* **Christian Berlage** **\***
* **Christian Zink**
* **Mike Gulisano**
* **Daniel-Ømicrón Rodríguez García (Omicronrg9)** **\***
* **Nathan Watson**
* **Draze**
* **Antison** **\***
* **OMGeeky** **\***

   (**\*** Currently active on team)



### Contributors List
Additional contributors to the project are listed [here](/contributors.md).
## Licenses

### Code
Andor's Trail code is released under GNU GPL v2.
### Content
Andor's Trail gameplay content is copyright by their respective authors and has only been licensed for use in Andor's Trail.
### Graphics
The graphics licenses and contributions can be found [here](/gfxcontrib.md).

## Wiki
Here is our slightly out of date [Wiki](https://andorstrail.gitbook.io/docs).
## Acknowledgments
Additional shout-outs.

