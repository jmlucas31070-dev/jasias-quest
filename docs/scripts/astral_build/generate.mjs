// Astral Beasts content generator for Jasia's Quest / Andor's Trail format.
// Reads the compact world definition below and emits JSON files into ../res/raw
// and a strings fragment into ../build/strings_generated.xml.
//
// Run with: node generate.mjs

import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const RAW = join(__dirname, "..", "res", "raw");
const OUT_STR = join(__dirname, "strings_generated.xml");
mkdirSync(RAW, { recursive: true });

// ---------------------------------------------------------------------------
// World definition
// ---------------------------------------------------------------------------

const REGIONS = [
  { id: "ember",  name: "Emberlands",   clade: "Cinderkin", element: "fire",     tier: 1, town: "Ashbridge",      gymLeader: "Pyralis",  champion: "Ignara",     teamAdmin: "Solrin",   theme: "scorched plains and basalt fields" },
  { id: "tide",   name: "Tideholm",     clade: "Tidefolk",  element: "water",    tier: 2, town: "Saltspire",      gymLeader: "Marenna",  champion: "Coralax",    teamAdmin: "Brackwell", theme: "drowned reefs and sea-cliff villages" },
  { id: "verdant",name: "Verdant Reach",clade: "Verdant",   element: "grass",    tier: 3, town: "Mossglen",       gymLeader: "Ferna",    champion: "Sylvane",    teamAdmin: "Thornell",  theme: "old-growth canopies and overgrown ruins" },
  { id: "storm",  name: "Stormcrest",   clade: "Stormborn", element: "lightning",tier: 4, town: "Boltreach",      gymLeader: "Volta",    champion: "Tempyx",     teamAdmin: "Kestrel",   theme: "high mesas above the lightning-line" },
  { id: "frost",  name: "Frostvale",    clade: "Rimekin",   element: "ice",      tier: 5, town: "Hoarwatch",      gymLeader: "Crysell",  champion: "Glacira",    teamAdmin: "Borissa",   theme: "blue-ice tundras and frozen rivers" },
  { id: "stone",  name: "Stoneheart",   clade: "Geokin",    element: "earth",    tier: 6, town: "Granitemarch",   gymLeader: "Korran",   champion: "Tellurik",   teamAdmin: "Quarrick",  theme: "deep canyons and lattice-worked mines" },
  { id: "dusk",   name: "Duskwood",     clade: "Shadeborn", element: "shadow",   tier: 7, town: "Hollowfen",      gymLeader: "Nyxara",   champion: "Umbros",     teamAdmin: "Vellis",    theme: "dim oakwoods where the lamps never quite catch" },
  { id: "aether", name: "Aetherspire",  clade: "Aetherborn",element: "light",    tier: 8, town: "Highmere",       gymLeader: "Solarya",  champion: "Lumiel",     teamAdmin: "Halen",     theme: "white-stone terraces above the cloud line" },
  { id: "void",   name: "Voidmarsh",    clade: "Wyrmkin",   element: "void",     tier: 9, town: "Greylight",      gymLeader: "Morrigane",champion: "Voidrak",    teamAdmin: "Sablehex",  theme: "lightless wetlands at the edge of the unmade world" },
];

// 10 creatures per region. Tags:
//   line: "starter3a/b/c", "mid2a/b", "solo", "legend", "myth"
//   slot: weapon|shield|head|body|hand|feet|ring|neck
//   tier: 1..9 (used for capture difficulty)
const SLOT_ROTATION = ["body", "head", "ring", "hand", "feet", "neck", "head", "ring"];

function speciesFor(region) {
  // Species are named by clade flavour. The names are original coinages.
  const root = {
    ember:   ["Cindlet",  "Pyrrun",   "Ignifex",   "Smokrat",  "Smoulkin", "Ashfennec","Glowmoth",  "Bramberus","Solphoenix","Magmaron"],
    tide:    ["Drilet",   "Maridon",  "Tidalys",   "Brinepup", "Brineback","Reefling", "Frothfin",  "Kelpdrak", "Abyssarius","Maelstor"],
    verdant: ["Sproutle", "Verdwyn",  "Bloomyx",   "Sapnik",   "Saproot",  "Mossfox",  "Pollenkit", "Thornox",  "Greenwarden","Sylvarch"],
    storm:   ["Sparlet",  "Voltrik",  "Thunderyx", "Statikit", "Statilope","Cloudfink","Galemoth",  "Stormhawk","Skystorm",   "Rixaron"],
    frost:   ["Frostlet", "Crysoul",  "Rimearch",  "Slushpup", "Slushound","Snowfennec","Hailflitter","Glacicrab","Aurorix",   "Hoarmonarch"],
    stone:   ["Pebblet",  "Stonewyrm","Geomarch",  "Quarrik",  "Quarrigon","Cavefennec","Gemmoth",   "Granibear","Corestar",   "Mantleux"],
    dusk:    ["Wisplet",  "Shadegrim","Umbrelyx",  "Hexpup",   "Hexnaught","Mistfox",   "Mothshade", "Grimsoul", "Eclipsar",   "Necronyx"],
    aether:  ["Glowlet",  "Lumara",   "Aetheryx",  "Wingwhelp","Wingseraph","Sunfennec","Beamoth",   "Halocrane","Solaeon",    "Auralis"],
    void:    ["Voidlet",  "Wyrmgrim", "Voidarch",  "Glimpup",  "Glimhound","Voidfox",   "Hexmoth",   "Wyrmbear", "Endorae",    "Unmaker"],
  }[region.id];

  const tags = [
    { line: "starter3a", slot: "ring",   tier: region.tier,                evo: 1 }, // becomes 2
    { line: "starter3b", slot: "head",   tier: Math.min(9, region.tier+1), evo: 2 }, // becomes 3
    { line: "starter3c", slot: "body",   tier: Math.min(9, region.tier+2), evo: 0 },
    { line: "mid2a",     slot: "feet",   tier: region.tier,                evo: 1 }, // becomes b
    { line: "mid2b",     slot: "hand",   tier: Math.min(9, region.tier+1), evo: 0 },
    { line: "solo",      slot: "neck",   tier: region.tier,                evo: 0 },
    { line: "solo",      slot: "head",   tier: region.tier,                evo: 0 },
    { line: "solo",      slot: "ring",   tier: region.tier,                evo: 0 },
    { line: "legend",    slot: "weapon", tier: Math.min(9, region.tier+1), evo: 0 },
    { line: "myth",      slot: "shield", tier: Math.min(9, region.tier+2), evo: 0 },
  ];

  return root.map((name, i) => ({
    id: `${region.id}_${name.toLowerCase()}`,
    name,
    region: region.id,
    clade: region.clade,
    element: region.element,
    ...tags[i],
    indexInRegion: i,
  }));
}

const SPECIES = REGIONS.flatMap(speciesFor);
// Wire up evolutions (next id) for chains.
for (const r of REGIONS) {
  const list = SPECIES.filter(s => s.region === r.id);
  // starter chain: a -> b -> c
  list.find(s => s.line === "starter3a").evolvesInto = list.find(s => s.line === "starter3b").id;
  list.find(s => s.line === "starter3b").evolvesInto = list.find(s => s.line === "starter3c").id;
  // mid chain: a -> b
  list.find(s => s.line === "mid2a").evolvesInto = list.find(s => s.line === "mid2b").id;
}

// ---------------------------------------------------------------------------
// Forms: base / shiny / variant. Each form is its own entity.
// ---------------------------------------------------------------------------
const FORMS = [
  { suffix: "",         label: "",          power: 1.0,  iconShift: 0,  rarity: 0 }, // base
  { suffix: "_shiny",   label: " Shiny",    power: 1.25, iconShift: 1,  rarity: 1 },
  { suffix: "_variant", label: " Variant",  power: 1.10, iconShift: 2,  rarity: 1 },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const pad = (s) => s.replace(/[^a-z0-9_]/gi, "_").toLowerCase();
const ELEMENT_ICON = {
  fire:      "effects:1",
  water:     "effects:2",
  grass:     "effects:3",
  lightning: "effects:4",
  ice:       "effects:5",
  earth:     "effects:6",
  shadow:    "effects:7",
  light:     "effects:8",
  void:      "effects:9",
};
const ELEMENT_ITEM_ICON = {
  fire:      "items_misc:1",
  water:     "items_misc:2",
  grass:     "items_misc:3",
  lightning: "items_misc:4",
  ice:       "items_misc:5",
  earth:     "items_misc:6",
  shadow:    "items_misc:7",
  light:     "items_misc:8",
  void:      "items_misc:9",
};
const ELEMENT_BEAST_ICON = {
  fire:      "monsters_undead:1",
  water:     "monsters_undead:2",
  grass:     "monsters_undead:3",
  lightning: "monsters_undead:4",
  ice:       "monsters_undead:5",
  earth:     "monsters_undead:6",
  shadow:    "monsters_undead:7",
  light:     "monsters_undead:8",
  void:      "monsters_undead:9",
};

const strings = []; // {key, value}
function S(key, value) { strings.push({ key, value }); return `@string/${key}`; }

// ---------------------------------------------------------------------------
// Actorconditions: one spell per form (the creature's signature attack/buff
// granted while the equipment item is equipped).
// ---------------------------------------------------------------------------
const actorconditions = [];

// System-wide conditions
actorconditions.push({
  id: "ab_cond_jinxed",
  name: S("ab_cond_jinxed_name", "Jinxed"),
  description: "A bad omen clings to you. Spirit Orbs shatter on impact while this lasts.",
  iconID: "effects:14",
  positive: 0,
  category: "spiritual",
});
actorconditions.push({
  id: "ab_cond_trainer_focus",
  name: S("ab_cond_trainer_focus_name", "Trainer Focus"),
  description: "You move and breathe as your beasts do. Capture chance is improved.",
  iconID: "effects:11",
  positive: 1,
  category: "spiritual",
  statsEffect: { increaseAttackChance: 5 },
});
for (let lvl = 1; lvl <= 9; lvl++) {
  actorconditions.push({
    id: `ab_cond_trainer_tier_${lvl}`,
    name: S(`ab_cond_trainer_tier_${lvl}_name`, `Trainer Rank ${lvl}`),
    description: `You hold the rank token for tier ${lvl}. Higher-tier Spirit Orbs become available to you at the Beast Center.`,
    iconID: "effects:10",
    positive: 1,
    category: "spiritual",
  });
}

for (const sp of SPECIES) {
  for (const form of FORMS) {
    const id = `ab_spell_${sp.id}${form.suffix}`;
    const displayName = `${sp.name}${form.label} Resonance`;
    const baseDmg = 2 + sp.tier;
    const dmg = Math.round(baseDmg * form.power);
    const cond = {
      id,
      name: S(`${id}_name`, displayName),
      description: `The signature resonance of ${sp.name}${form.label}. While equipped, your strike carries the ${sp.element} of the ${sp.clade}.`,
      iconID: ELEMENT_ICON[sp.element],
      positive: 1,
      category: "spiritual",
      statsEffect: {
        increaseAttackDamage_min: dmg,
        increaseAttackDamage_max: dmg + sp.tier,
        increaseAttackChance: 2 + Math.floor(sp.tier / 2),
      },
    };
    actorconditions.push(cond);
  }
}

// ---------------------------------------------------------------------------
// Item categories
// ---------------------------------------------------------------------------
const itemcategories = [
  { id: "ab_cat_orb",        name: S("ab_cat_orb_name", "Spirit Orb"),         actionType: "use" },
  { id: "ab_cat_beast_eq",   name: S("ab_cat_beast_eq_name", "Astral Beast"),  actionType: "equip" },
  { id: "ab_cat_evostone",   name: S("ab_cat_evostone_name", "Evolution Stone"), actionType: "use" },
  { id: "ab_cat_incense",    name: S("ab_cat_incense_name", "Breeding Incense"), actionType: "use" },
  { id: "ab_cat_dex",        name: S("ab_cat_dex_name", "Beast Dex"),          actionType: "use" },
  { id: "ab_cat_region_pass",name: S("ab_cat_region_pass_name", "Region Pass"),actionType: "use" },
];

// ---------------------------------------------------------------------------
// Items: orbs, beast equipment, evolution stones, incense, dex, region passes
// ---------------------------------------------------------------------------
const items = [];

const ORB_TIERS = [
  { id: "ab_orb_basic",   name: "Spirit Orb",        tier: 1, cost: 200,  icon: "items_misc:30" },
  { id: "ab_orb_great",   name: "Great Spirit Orb",  tier: 3, cost: 600,  icon: "items_misc:31" },
  { id: "ab_orb_master",  name: "Master Spirit Orb", tier: 6, cost: 2200, icon: "items_misc:32" },
  { id: "ab_orb_dusk",    name: "Dusk Spirit Orb",   tier: 5, cost: 1500, icon: "items_misc:33" },
  { id: "ab_orb_lure",    name: "Lure Spirit Orb",   tier: 2, cost: 400,  icon: "items_misc:34" },
];
for (const o of ORB_TIERS) {
  items.push({
    id: o.id,
    name: S(`${o.id}_name`, o.name),
    iconID: o.icon,
    category: "ab_cat_orb",
    baseMarketCost: o.cost,
    description: `A Spirit Orb of tier ${o.tier}. Throw it at a wild beast to attempt a binding.`,
  });
}

// Slot mapping → AT equipment slot strings used in items
const SLOT_TO_AT = {
  weapon: "weapon",
  shield: "shield",
  head:   "head",
  body:   "body",
  hand:   "hand",
  feet:   "feet",
  ring:   "ring",
  neck:   "neck",
};

for (const sp of SPECIES) {
  for (const form of FORMS) {
    const id = `ab_eq_${sp.id}${form.suffix}`;
    const displayName = `Bound ${sp.name}${form.label}`;
    const cond = `ab_spell_${sp.id}${form.suffix}`;
    const slot = SLOT_TO_AT[sp.slot];
    const item = {
      id,
      name: S(`${id}_name`, displayName),
      iconID: ELEMENT_ITEM_ICON[sp.element],
      category: "ab_cat_beast_eq",
      baseMarketCost: 0,
      description: `${sp.name}${form.label} of the ${sp.clade}, bound into a focus. Equip in your ${slot} slot to fight alongside it.`,
      equipEffect: {
        addedConditions_equip: [
          { condition: cond, magnitude: 1, duration: -1, chance: 1.0 }
        ]
      }
    };
    if (sp.line === "legend" || sp.line === "myth") {
      item.displayType = sp.line === "myth" ? 4 : 3;
    }
    items.push(item);
  }
}

// Evolution stones (one per region, plus a universal "Resonant Shard")
for (const r of REGIONS) {
  items.push({
    id: `ab_stone_${r.id}`,
    name: S(`ab_stone_${r.id}_name`, `${r.clade} Stone`),
    iconID: ELEMENT_ITEM_ICON[r.element],
    category: "ab_cat_evostone",
    baseMarketCost: 1500,
    description: `An ${r.element}-charged stone. Bring a ${r.clade} beast to a Beast Center breeder to evolve it.`,
  });
}
items.push({
  id: "ab_stone_resonant",
  name: S("ab_stone_resonant_name", "Resonant Shard"),
  iconID: "items_misc:21",
  category: "ab_cat_evostone",
  baseMarketCost: 4000,
  description: "A universal evolution catalyst. Works on any clade.",
});

// Breeding incense
items.push({
  id: "ab_incense_pair",
  name: S("ab_incense_pair_name", "Pair Incense"),
  iconID: "items_misc:40",
  category: "ab_cat_incense",
  baseMarketCost: 1200,
  description: "Burned at the breeding alcove of any Beast Center. Permits two compatible beasts to leave an egg.",
});

// Beast Dex (one per region + master)
for (const r of REGIONS) {
  items.push({
    id: `ab_dex_${r.id}`,
    name: S(`ab_dex_${r.id}_name`, `${r.name} Dex`),
    iconID: "items_misc:50",
    category: "ab_cat_dex",
    baseMarketCost: 0,
    description: `A folio that records every Astral Beast sighted in ${r.name}.`,
  });
}
items.push({
  id: "ab_dex_master",
  name: S("ab_dex_master_name", "Master Dex"),
  iconID: "items_misc:51",
  category: "ab_cat_dex",
  baseMarketCost: 0,
  description: "The collected folios of every region. Held only by the world's foremost trainers.",
});

// Region passes (gym leader badges that unlock the next region)
for (const r of REGIONS) {
  items.push({
    id: `ab_pass_${r.id}`,
    name: S(`ab_pass_${r.id}_name`, `${r.name} Crest`),
    iconID: "items_misc:60",
    category: "ab_cat_region_pass",
    baseMarketCost: 0,
    description: `Awarded by ${r.gymLeader} of ${r.town}. Proof you have mastered the ${r.clade} circuit.`,
  });
}

// ---------------------------------------------------------------------------
// Monsters: NPCs, wild beast forms, and the computer object
// ---------------------------------------------------------------------------
const monsters = [];

// The computer "object" actor — an inanimate prop the player talks to
monsters.push({
  id: "ab_obj_computer",
  name: S("ab_obj_computer_name", "Astral Console"),
  iconID: "objects_furniture:25",
  monsterClass: "object",
  movementAggressionType: "stationary",
  phraseID: "ab_console_boot",
  spawnGroup: "ab_console",
  maxHP: 1, attackChance: 0, criticalSkill: 0, blockChance: 0, damageResistance: 0, exp: 0,
});

// Per-region NPCs (gym leader, champion, evil team admin, professor, breeder, clerk, shopkeeper, hideout grunt)
for (const r of REGIONS) {
  const npcs = [
    { suf: "professor",  cls: "humanoid", iconID: "npc_humans:8",  hp: 80,  phrase: `ab_${r.id}_professor_greet` },
    { suf: "clerk",      cls: "humanoid", iconID: "npc_humans:11", hp: 60,  phrase: `ab_${r.id}_clerk_greet` },
    { suf: "breeder",    cls: "humanoid", iconID: "npc_humans:14", hp: 70,  phrase: `ab_${r.id}_breeder_greet` },
    { suf: "shopkeeper", cls: "humanoid", iconID: "npc_humans:5",  hp: 70,  phrase: `ab_${r.id}_shop_greet` },
    { suf: "gymleader",  cls: "humanoid", iconID: "npc_humans:1",  hp: 240 + r.tier * 40, phrase: `ab_${r.id}_gym_greet`,
      attackChance: 60 + r.tier*2, criticalSkill: 5 + r.tier, exp: 800 + r.tier*200 },
    { suf: "champion",   cls: "humanoid", iconID: "npc_humans:4",  hp: 360 + r.tier * 60, phrase: `ab_${r.id}_champ_greet`,
      attackChance: 70 + r.tier*2, criticalSkill: 8 + r.tier, exp: 1500 + r.tier*300 },
    { suf: "team_admin", cls: "humanoid", iconID: "npc_humans:7",  hp: 200 + r.tier * 30, phrase: `ab_${r.id}_team_greet`,
      attackChance: 55 + r.tier*2, criticalSkill: 4 + r.tier, exp: 600 + r.tier*150 },
    { suf: "team_grunt", cls: "humanoid", iconID: "npc_humans:6",  hp: 100 + r.tier * 20, phrase: `ab_${r.id}_grunt_greet`,
      attackChance: 40 + r.tier*2, criticalSkill: 2 + r.tier, exp: 200 + r.tier*60 },
  ];
  for (const n of npcs) {
    monsters.push({
      id: `ab_npc_${r.id}_${n.suf}`,
      name: S(`ab_npc_${r.id}_${n.suf}_name`,
        ({
          professor:  `Professor of ${r.name}`,
          clerk:      `${r.name} Beast Center Clerk`,
          breeder:    `${r.name} Breeder`,
          shopkeeper: `${r.name} Orb Vendor`,
          gymleader:  `Gym Leader ${r.gymLeader}`,
          champion:   `Champion ${r.champion}`,
          team_admin: `Team Eclipse Admin ${r.teamAdmin}`,
          team_grunt: `Team Eclipse Grunt`,
        })[n.suf]),
      iconID: n.iconID,
      monsterClass: n.cls,
      movementAggressionType: "stationary",
      phraseID: n.phrase,
      spawnGroup: `ab_${r.id}`,
      maxHP: n.hp,
      attackChance: n.attackChance ?? 0,
      criticalSkill: n.criticalSkill ?? 0,
      blockChance: 0,
      damageResistance: 0,
      exp: n.exp ?? 0,
    });
  }
}

// Wild beasts: one monster entry per (species × form) so the engine can spawn each.
for (const sp of SPECIES) {
  for (const form of FORMS) {
    const baseHP = 20 + sp.tier * 12;
    const hp = Math.round(baseHP * form.power);
    monsters.push({
      id: `ab_wild_${sp.id}${form.suffix}`,
      name: S(`ab_wild_${sp.id}${form.suffix}_name`, `Wild ${sp.name}${form.label}`),
      iconID: ELEMENT_BEAST_ICON[sp.element],
      monsterClass: "beast",
      movementAggressionType: "wandering",
      phraseID: `ab_wild_capture_${sp.id}${form.suffix}`,
      spawnGroup: `ab_wild_${sp.region}`,
      maxHP: hp,
      attackChance: 30 + sp.tier * 3,
      attackDamage_min: 1 + sp.tier,
      attackDamage_max: 3 + sp.tier * 2,
      criticalSkill: sp.tier,
      blockChance: 5 + sp.tier,
      damageResistance: sp.tier,
      exp: 30 + sp.tier * 25 + (form.rarity ? 40 : 0),
    });
  }
}

// ---------------------------------------------------------------------------
// Droplists: orbs and crests as quest rewards, evolution stones from leaders
// ---------------------------------------------------------------------------
const droplists = [];
droplists.push({
  id: "ab_drop_starter_kit",
  items: [
    { itemID: "ab_orb_basic",     quantity_min: 5, quantity_max: 5, chance: 1.0 },
    { itemID: "ab_dex_ember",     quantity_min: 1, quantity_max: 1, chance: 1.0 },
  ]
});
for (const r of REGIONS) {
  droplists.push({
    id: `ab_drop_gym_${r.id}`,
    items: [
      { itemID: `ab_pass_${r.id}`, quantity_min: 1, quantity_max: 1, chance: 1.0 },
      { itemID: `ab_stone_${r.id}`, quantity_min: 1, quantity_max: 1, chance: 1.0 },
      { itemID: "ab_orb_great",     quantity_min: 3, quantity_max: 3, chance: 1.0 },
    ]
  });
  droplists.push({
    id: `ab_drop_champion_${r.id}`,
    items: [
      { itemID: "ab_stone_resonant", quantity_min: 1, quantity_max: 1, chance: 1.0 },
      { itemID: "ab_orb_master",     quantity_min: 1, quantity_max: 1, chance: 1.0 },
    ]
  });
}
droplists.push({
  id: "ab_drop_jinx_chance",
  items: [
    { itemID: "ab_orb_basic", quantity_min: 0, quantity_max: 0, chance: 0.02 },
  ]
});

// ---------------------------------------------------------------------------
// Quests: 9 region dexes, 1 master dex, 9 gym ladders, 9 evil-team chains,
// 1 trainer-level meta, 1 end-game reset
// ---------------------------------------------------------------------------
const quests = [];

quests.push({
  id: "ab_quest_trainer_level",
  name: S("ab_quest_trainer_level_name", "Trainer Path"),
  showInLog: 1,
  stages: Array.from({ length: 100 }, (_, i) => ({
    progress: i + 1,
    logText: `Your trainer rank advanced to ${i + 1} / 100.`,
    rewardExperience: 0,
  })),
});

for (const r of REGIONS) {
  quests.push({
    id: `ab_quest_dex_${r.id}`,
    name: S(`ab_quest_dex_${r.id}_name`, `${r.name} Dex`),
    showInLog: 1,
    stages: [
      { progress: 10,  logText: `The professor of ${r.town} entrusted you with the ${r.name} Dex.`, rewardExperience: 100 },
      { progress: 50,  logText: `You have catalogued half of the ${r.clade} of ${r.name}.`,         rewardExperience: 400 },
      { progress: 100, logText: `Every ${r.clade} of ${r.name} has been recorded.`,                  rewardExperience: 1500, finishesQuest: 1 },
    ],
  });
  quests.push({
    id: `ab_quest_gym_${r.id}`,
    name: S(`ab_quest_gym_${r.id}_name`, `${r.town} Gym`),
    showInLog: 1,
    stages: [
      { progress: 10,  logText: `You entered the ${r.town} Gym to challenge ${r.gymLeader}.`,       rewardExperience: 200 },
      { progress: 50,  logText: `You defeated the gym trial keepers.`,                               rewardExperience: 500 },
      { progress: 100, logText: `You bested ${r.gymLeader} and earned the ${r.name} Crest.`,         rewardExperience: 1200, finishesQuest: 1 },
    ],
  });
  quests.push({
    id: `ab_quest_team_${r.id}`,
    name: S(`ab_quest_team_${r.id}_name`, `Team Eclipse in ${r.name}`),
    showInLog: 1,
    stages: [
      { progress: 10,  logText: `Team Eclipse has been sighted in ${r.town}.`,                       rewardExperience: 200 },
      { progress: 50,  logText: `You located the Eclipse hideout in ${r.name}.`,                     rewardExperience: 600 },
      { progress: 100, logText: `Admin ${r.teamAdmin} has been driven out of ${r.name}.`,            rewardExperience: 1500, finishesQuest: 1 },
    ],
  });
  quests.push({
    id: `ab_quest_champ_${r.id}`,
    name: S(`ab_quest_champ_${r.id}_name`, `Champion of ${r.name}`),
    showInLog: 1,
    stages: [
      { progress: 50,  logText: `Champion ${r.champion} has agreed to face you.`,                    rewardExperience: 1000 },
      { progress: 100, logText: `You bested Champion ${r.champion}. The road to the next region opens.`, rewardExperience: 3000, finishesQuest: 1 },
    ],
  });
}

quests.push({
  id: "ab_quest_master_dex",
  name: S("ab_quest_master_dex_name", "Master Dex"),
  showInLog: 1,
  stages: [
    { progress: 10,  logText: "Every regional dex has been completed. The Master Dex has been issued in your name.", rewardExperience: 5000 },
    { progress: 100, logText: "You are recognised as a Master of the Astral Beasts.",                  rewardExperience: 10000, finishesQuest: 1 },
  ],
});

quests.push({
  id: "ab_quest_endgame_reset",
  name: S("ab_quest_endgame_reset_name", "The Long Tournament"),
  showInLog: 1,
  stages: [
    { progress: 10,  logText: "The League declared a Long Tournament. Every gym and every champion will face you again, harder than before.", rewardExperience: 2000 },
    { progress: 100, logText: "You held every crest a second time. The Long Tournament is yours.", rewardExperience: 20000, finishesQuest: 1 },
  ],
});

// ---------------------------------------------------------------------------
// Conversationlists: console boot, capture/fight branching, NPC dialogues
// ---------------------------------------------------------------------------
const conversationlists = [];

// --- Console (computer) boot dialogue
conversationlists.push({
  id: "ab_console_boot",
  message: "The Astral Console hums to life. A soft chime invites you to begin a beast journey across the nine regions.",
  replies: [
    { text: "Begin a new journey (Emberlands).", nextPhrase: "ab_console_journey_start" },
    { text: "Travel to a region I have unlocked.", nextPhrase: "ab_console_travel_menu" },
    { text: "Read the trainer almanac.", nextPhrase: "ab_console_almanac" },
    { text: "Step away.", nextPhrase: "EXIT" },
  ],
});
conversationlists.push({
  id: "ab_console_journey_start",
  message: "A starter kit is queued in your pack: five Spirit Orbs and the Emberlands Dex. The Console marks your trainer rank as 1.",
  replies: [
    { text: "Accept and begin.", nextPhrase: "EXIT",
      rewardDropList: "ab_drop_starter_kit",
      rewardQuestStage: { questID: "ab_quest_trainer_level", progress: 1 },
      rewardQuestStage_2: { questID: "ab_quest_dex_ember", progress: 10 } },
    { text: "Not now.", nextPhrase: "ab_console_boot" },
  ],
});
conversationlists.push({
  id: "ab_console_travel_menu",
  message: "Choose a destination.",
  replies: REGIONS.map(r => ({
    text: `Travel to ${r.town} (${r.name})`,
    nextPhrase: `ab_travel_${r.id}`,
    requireItem: `ab_pass_${r.id}`,
  })).concat([{ text: "Back", nextPhrase: "ab_console_boot" }]),
});
for (const r of REGIONS) {
  conversationlists.push({
    id: `ab_travel_${r.id}`,
    message: `The Console projects ${r.town}. The journey is instant.`,
    replies: [
      { text: "Step through.", nextPhrase: "EXIT",
        switchToMap: { map: `ab_${r.id}_center`, place: "from_console" } },
    ],
  });
}
conversationlists.push({
  id: "ab_console_almanac",
  message: "ASTRAL BEASTS — A FIELD GUIDE\n\n• Beasts are bound into focus items. Equip a focus to fight alongside that beast.\n• Wild beasts may be CAUGHT with Spirit Orbs or FOUGHT for experience and drops.\n• Catch chance scales with your trainer rank (1–100), the orb's tier, and the beast's tier.\n• Every region has a Beast Center hub: clerk, professor, breeder, orb vendor.\n• Defeat a gym leader for the region Crest, then the champion to open the next region.\n• Team Eclipse runs a hideout in every region. Their Admin guards an evolution stone.",
  replies: [{ text: "Close the almanac.", nextPhrase: "ab_console_boot" }],
});

// --- Per-wild-beast capture/fight branching
for (const sp of SPECIES) {
  for (const form of FORMS) {
    const wildID = `ab_wild_${sp.id}${form.suffix}`;
    const eqID   = `ab_eq_${sp.id}${form.suffix}`;
    const orbReq = sp.tier <= 2 ? "ab_orb_basic"
                  : sp.tier <= 5 ? "ab_orb_great"
                                 : "ab_orb_master";
    const trainerReq = Math.max(1, (sp.tier - 1) * 10 + (form.rarity ? 5 : 0));

    conversationlists.push({
      id: `ab_wild_capture_${sp.id}${form.suffix}`,
      message: `A wild ${sp.name}${form.label} bristles. Will you fight it or attempt to bind it?`,
      replies: [
        { text: "Fight it.", nextPhrase: "FIGHT" },
        { text: `Throw a ${orbReq.replace("ab_orb_", "")} Spirit Orb.`,
          nextPhrase: `ab_capture_roll_${sp.id}${form.suffix}`,
          requireItem: orbReq, consumeItem: orbReq },
        { text: "Back away.", nextPhrase: "EXIT" },
      ],
    });
    conversationlists.push({
      id: `ab_capture_roll_${sp.id}${form.suffix}`,
      message: `The orb arcs out and locks around ${sp.name}${form.label}…`,
      replies: [
        // Success path: trainer rank meets requirement and not jinxed
        { text: "Success — the beast is bound.",
          nextPhrase: "EXIT",
          requireQuestProgress: { questID: "ab_quest_trainer_level", progress: trainerReq },
          requireConditionImmunity: "ab_cond_jinxed",
          rewardItem: eqID, rewardItem_quantity: 1,
          rewardQuestStage: { questID: `ab_quest_dex_${sp.region}`, progress: Math.min(100, 10 + sp.indexInRegion * 9) },
          rewardDropList: "ab_drop_jinx_chance" },
        // Jinxed path
        { text: "The orb shatters — you feel an ill omen.",
          nextPhrase: "EXIT",
          requireCondition: "ab_cond_jinxed" },
        // Trainer rank too low
        { text: "Your rank is not enough — the beast escapes.",
          nextPhrase: "EXIT" },
      ],
    });
  }
}

// --- Per-region NPC dialogues (compact)
for (const r of REGIONS) {
  conversationlists.push({
    id: `ab_${r.id}_professor_greet`,
    message: `Welcome to ${r.town}. I study the ${r.clade} of ${r.theme}. Take this folio — it is the ${r.name} Dex.`,
    replies: [
      { text: "I will fill it.", nextPhrase: "EXIT",
        rewardItem: `ab_dex_${r.id}`, rewardItem_quantity: 1,
        rewardQuestStage: { questID: `ab_quest_dex_${r.id}`, progress: 10 } },
      { text: "Tell me about the region.", nextPhrase: `ab_${r.id}_professor_lore` },
      { text: "Be well.", nextPhrase: "EXIT" },
    ],
  });
  conversationlists.push({
    id: `ab_${r.id}_professor_lore`,
    message: `${r.name} is a land of ${r.theme}. The ${r.clade} thrive here. Defeat ${r.gymLeader} at the gym, then Champion ${r.champion}, and the road north opens.`,
    replies: [{ text: "Thank you.", nextPhrase: `ab_${r.id}_professor_greet` }],
  });
  conversationlists.push({
    id: `ab_${r.id}_clerk_greet`,
    message: `Beast Center, ${r.town} branch. Your beasts can rest here at no charge. Travel back to the Console at any time.`,
    replies: [{ text: "Thanks.", nextPhrase: "EXIT" }],
  });
  conversationlists.push({
    id: `ab_${r.id}_breeder_greet`,
    message: `Bring me an evolution stone — ${r.clade} Stone or a Resonant Shard — and a beast that is ready, and I will guide it to its next form. Bring two compatible beasts and a Pair Incense, and I will leave you with an egg.`,
    replies: [
      { text: "Evolve a beast.", nextPhrase: `ab_${r.id}_breeder_evolve_menu` },
      { text: "Breed a pair.",   nextPhrase: `ab_${r.id}_breeder_breed` },
      { text: "Be well.", nextPhrase: "EXIT" },
    ],
  });
  // Evolve menu — show every chained species in this region
  const chainSpecies = SPECIES.filter(s => s.region === r.id && s.evolvesInto);
  conversationlists.push({
    id: `ab_${r.id}_breeder_evolve_menu`,
    message: "Which beast?",
    replies: chainSpecies.map(s => ({
      text: `Evolve ${s.name}.`,
      nextPhrase: `ab_evolve_${s.id}`,
      requireItem: `ab_eq_${s.id}`,
      consumeItem: `ab_eq_${s.id}`,
      requireItem_2: `ab_stone_${r.id}`,
      consumeItem_2: `ab_stone_${r.id}`,
    })).concat([{ text: "Back", nextPhrase: `ab_${r.id}_breeder_greet` }]),
  });
  for (const s of chainSpecies) {
    const next = SPECIES.find(x => x.id === s.evolvesInto);
    conversationlists.push({
      id: `ab_evolve_${s.id}`,
      message: `${s.name} pulses, draws in the stone, and reshapes into ${next.name}.`,
      replies: [{ text: "Wonderful.", nextPhrase: "EXIT",
        rewardItem: `ab_eq_${next.id}`, rewardItem_quantity: 1 }],
    });
  }
  conversationlists.push({
    id: `ab_${r.id}_breeder_breed`,
    message: `Two ${r.clade} beasts and a Pair Incense — and an egg comes home with you.`,
    replies: [
      { text: "Burn the incense.",
        nextPhrase: "EXIT",
        requireItem: "ab_incense_pair", consumeItem: "ab_incense_pair",
        rewardItem: `ab_eq_${r.id}_${SPECIES.find(s => s.region === r.id && s.line === "starter3a").name.toLowerCase()}`,
        rewardItem_quantity: 1 },
      { text: "Back", nextPhrase: `ab_${r.id}_breeder_greet` },
    ],
  });
  conversationlists.push({
    id: `ab_${r.id}_shop_greet`,
    message: `Spirit Orbs, all tiers. What will it be?`,
    replies: [
      { text: "Buy 5 basic orbs (1000g).", nextPhrase: "EXIT",
        requireGold: 1000, removeGold: 1000, rewardItem: "ab_orb_basic", rewardItem_quantity: 5 },
      { text: "Buy a great orb (600g).", nextPhrase: "EXIT",
        requireGold: 600, removeGold: 600, rewardItem: "ab_orb_great", rewardItem_quantity: 1 },
      { text: "Buy a master orb (2200g).", nextPhrase: "EXIT",
        requireGold: 2200, removeGold: 2200, rewardItem: "ab_orb_master", rewardItem_quantity: 1 },
      { text: "Buy a Pair Incense (1200g).", nextPhrase: "EXIT",
        requireGold: 1200, removeGold: 1200, rewardItem: "ab_incense_pair", rewardItem_quantity: 1 },
      { text: "Be well.", nextPhrase: "EXIT" },
    ],
  });
  conversationlists.push({
    id: `ab_${r.id}_gym_greet`,
    message: `I am ${r.gymLeader}, leader of the ${r.town} Gym. Show me what you have built.`,
    replies: [
      { text: "I challenge you.", nextPhrase: "FIGHT",
        rewardQuestStage: { questID: `ab_quest_gym_${r.id}`, progress: 100 },
        rewardDropList: `ab_drop_gym_${r.id}` },
      { text: "Not yet.", nextPhrase: "EXIT" },
    ],
  });
  conversationlists.push({
    id: `ab_${r.id}_champ_greet`,
    message: `I am ${r.champion}, Champion of ${r.name}. The next region waits beyond me.`,
    replies: [
      { text: "I am ready.", nextPhrase: "FIGHT",
        requireItem: `ab_pass_${r.id}`,
        rewardQuestStage: { questID: `ab_quest_champ_${r.id}`, progress: 100 },
        rewardDropList: `ab_drop_champion_${r.id}` },
      { text: "Soon.", nextPhrase: "EXIT" },
    ],
  });
  conversationlists.push({
    id: `ab_${r.id}_team_greet`,
    message: `I am Admin ${r.teamAdmin} of Team Eclipse. We will dim the sky over ${r.name} whether you like it or not.`,
    replies: [
      { text: "Stand down.", nextPhrase: "FIGHT",
        rewardQuestStage: { questID: `ab_quest_team_${r.id}`, progress: 100 } },
      { text: "Withdraw.", nextPhrase: "EXIT" },
    ],
  });
  conversationlists.push({
    id: `ab_${r.id}_grunt_greet`,
    message: `Team Eclipse owns this hideout. Out.`,
    replies: [{ text: "Make me.", nextPhrase: "FIGHT" }, { text: "Back away.", nextPhrase: "EXIT" }],
  });
}

// ---------------------------------------------------------------------------
// Side-quest content (Tideholm worked example).
// Two optional NPCs, two quests, two quest items, one droplist, six dialogues.
// All Tideholm-prefixed (ab_q_tide_*, ab_npc_tide_lighthouse_keeper, ...)
// so the pattern is easy to copy for the other seven regions later.
// ---------------------------------------------------------------------------

// --- Quest items
items.push({
  id: "ab_q_tide_lantern_bead",
  name: S("ab_q_tide_lantern_bead_name", "Saltspire Lantern Bead"),
  iconID: "items_misc:21",
  category: "ab_cat_dex",
  baseMarketCost: 0,
  description: "A glass bead that holds a flicker of stormlight. The Saltspire keeper needs it to relight the lantern.",
});
items.push({
  id: "ab_q_tide_pearl_token",
  name: S("ab_q_tide_pearl_token_name", "Tideholm Pearl Token"),
  iconID: "items_misc:22",
  category: "ab_cat_dex",
  baseMarketCost: 0,
  description: "A small pearl etched with the diver's mark. Proof you completed the Pearl Survey.",
});

// --- Side-quest NPCs (Tideholm only)
monsters.push({
  id: "ab_npc_tide_lighthouse_keeper",
  name: S("ab_npc_tide_lighthouse_keeper_name", "Saltspire Lighthouse Keeper"),
  iconID: "npc_humans:9",
  monsterClass: "humanoid",
  movementAggressionType: "stationary",
  phraseID: "ab_tide_keeper_greet",
  spawnGroup: "ab_tide",
  maxHP: 60, attackChance: 0, criticalSkill: 0, blockChance: 0, damageResistance: 0, exp: 0,
});
monsters.push({
  id: "ab_npc_tide_pearl_diver",
  name: S("ab_npc_tide_pearl_diver_name", "Tideholm Pearl Diver"),
  iconID: "npc_humans:13",
  monsterClass: "humanoid",
  movementAggressionType: "stationary",
  phraseID: "ab_tide_diver_greet",
  spawnGroup: "ab_tide",
  maxHP: 60, attackChance: 0, criticalSkill: 0, blockChance: 0, damageResistance: 0, exp: 0,
});

// --- Quests
quests.push({
  id: "ab_quest_tide_lantern",
  name: S("ab_quest_tide_lantern_name", "The Saltspire Lantern"),
  showInLog: 1,
  stages: [
    { progress: 10,  logText: "The Saltspire keeper asked you to recover a lantern bead. The Tideholm pearl diver should have one.", rewardExperience: 150 },
    { progress: 50,  logText: "The pearl diver traded you a lantern bead for 200 gold.",                                              rewardExperience: 200 },
    { progress: 100, logText: "You returned the bead. Saltspire Light shines again over Tideholm.",                                   rewardExperience: 800, finishesQuest: 1 },
  ],
});
quests.push({
  id: "ab_quest_tide_pearl_survey",
  name: S("ab_quest_tide_pearl_survey_name", "Tideholm Pearl Survey"),
  showInLog: 1,
  stages: [
    { progress: 10,  logText: "The pearl diver wants proof you have walked the Tideholm circuit — the Tideholm Crest will do.", rewardExperience: 150 },
    { progress: 100, logText: "You presented the Tideholm Crest. The diver carved you a Pearl Token.",                          rewardExperience: 600, finishesQuest: 1 },
  ],
});

// --- Lighthouse-keeper completion droplist (gold + great orb)
droplists.push({
  id: "ab_drop_tide_lantern_reward",
  items: [
    { itemID: "ab_orb_great", quantity_min: 2, quantity_max: 2, chance: 1.0 },
  ],
});

// --- Dialogues
conversationlists.push({
  id: "ab_tide_keeper_greet",
  message: "I am the keeper of Saltspire Light. The lantern bead fell into the surf last storm, and I cannot raise the flame without it. The pearl diver down the route fishes such things up — go and ask her.",
  replies: [
    { text: "I will fetch a bead.", nextPhrase: "EXIT",
      rewardQuestStage: { questID: "ab_quest_tide_lantern", progress: 10 } },
    { text: "I have the bead.", nextPhrase: "ab_tide_keeper_complete",
      requireItem: "ab_q_tide_lantern_bead" },
    { text: "Be well.", nextPhrase: "EXIT" },
  ],
});
conversationlists.push({
  id: "ab_tide_keeper_complete",
  message: "You found one — and so quickly. The lantern remembers its flame. Take this with my thanks; the orbs were a gift from the Beast Center, and they sit better in a trainer's pack than on my shelf.",
  replies: [
    { text: "Thank you.", nextPhrase: "EXIT",
      requireItem: "ab_q_tide_lantern_bead", consumeItem: "ab_q_tide_lantern_bead",
      rewardDropList: "ab_drop_tide_lantern_reward",
      rewardQuestStage: { questID: "ab_quest_tide_lantern", progress: 100 } },
  ],
});
conversationlists.push({
  id: "ab_tide_diver_greet",
  message: "Tideholm sees more travellers than it used to. What brings you to the shallows?",
  replies: [
    { text: "The keeper sent me — sell me a lantern bead.", nextPhrase: "ab_tide_diver_trade",
      requireQuestProgress: { questID: "ab_quest_tide_lantern", progress: 10 } },
    { text: "Tell me about the Pearl Survey.", nextPhrase: "ab_tide_diver_survey_start" },
    { text: "I bring the Tideholm Crest.", nextPhrase: "ab_tide_diver_survey_complete",
      requireItem: "ab_pass_tide" },
    { text: "Be well.", nextPhrase: "EXIT" },
  ],
});
conversationlists.push({
  id: "ab_tide_diver_trade",
  message: "A bead for two hundred gold. The tides decide the price, not me.",
  replies: [
    { text: "Pay the toll.", nextPhrase: "EXIT",
      requireGold: 200, removeGold: 200,
      rewardItem: "ab_q_tide_lantern_bead", rewardItem_quantity: 1,
      rewardQuestStage: { questID: "ab_quest_tide_lantern", progress: 50 } },
    { text: "Another time.", nextPhrase: "ab_tide_diver_greet" },
  ],
});
conversationlists.push({
  id: "ab_tide_diver_survey_start",
  message: "The Survey is simple: walk the gym circuit, take the Tideholm Crest from Marenna, and bring it back to me. The tides remember every trainer who has done it.",
  replies: [
    { text: "I accept.", nextPhrase: "EXIT",
      rewardQuestStage: { questID: "ab_quest_tide_pearl_survey", progress: 10 } },
    { text: "Back.", nextPhrase: "ab_tide_diver_greet" },
  ],
});
conversationlists.push({
  id: "ab_tide_diver_survey_complete",
  message: "Tideholm Crest in hand. The Survey is yours. Take this Pearl Token — the gym leaders of Verdant Reach and Stormcrest accept it as introduction.",
  replies: [
    { text: "Thank you.", nextPhrase: "EXIT",
      requireItem: "ab_pass_tide",
      rewardItem: "ab_q_tide_pearl_token", rewardItem_quantity: 1,
      rewardQuestStage: { questID: "ab_quest_tide_pearl_survey", progress: 100 } },
  ],
});

// ---------------------------------------------------------------------------
// Maps registration: list each region's center, gym, hideout, champion arena
// ---------------------------------------------------------------------------
const maps = [];
for (const r of REGIONS) {
  for (const sub of ["center", "route", "gym", "hideout", "champion"]) {
    maps.push({
      id: `ab_${r.id}_${sub}`,
      tmxFile: `ab_${r.id}_${sub}`,
      spawnGroups: [`ab_${r.id}`, `ab_wild_${r.id}`],
    });
  }
}

// ---------------------------------------------------------------------------
// Write everything
// ---------------------------------------------------------------------------
function writeJSON(name, data) {
  writeFileSync(join(RAW, name), JSON.stringify(data, null, 2) + "\n");
  console.log(`wrote ${name}: ${Array.isArray(data) ? data.length : 1} entries`);
}
writeJSON("ab_actorconditions.json", actorconditions);
writeJSON("ab_itemcategories.json",  itemcategories);
writeJSON("ab_items.json",           items);
writeJSON("ab_droplists.json",       droplists);
writeJSON("ab_quests.json",          quests);
writeJSON("ab_conversationlists.json", conversationlists);
writeJSON("ab_monsters.json",        monsters);
writeJSON("ab_maps.json",            maps);

// Strings fragment (the loader merges this into strings.xml)
const stringLines = strings.map(s =>
  `    <string name="${s.key}">${s.value
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/'/g, "\\'").replace(/\n/g, "\\n")}</string>`
).join("\n");
writeFileSync(OUT_STR, stringLines + "\n");
console.log(`wrote strings_generated.xml: ${strings.length} keys`);

// Stats summary
console.log(`\nSpecies: ${SPECIES.length}, Forms: ${FORMS.length}, Wild monsters: ${SPECIES.length * FORMS.length}`);
console.log(`Total NPCs: ${monsters.length}, Total items: ${items.length}, Total dialogues: ${conversationlists.length}`);
