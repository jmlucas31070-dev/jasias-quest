#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
crafting.py

"""

import json
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET
from copy import deepcopy

# ============================================================
# PATHS
# ============================================================

ROOT = Path(".")
RAW = ROOT / "raw"
XML = ROOT / "xml"
VALUES = ROOT / "values"

RAW.mkdir(exist_ok=True)
XML.mkdir(exist_ok=True)
VALUES.mkdir(exist_ok=True)

# ============================================================
# TMX TEMPLATE
# ============================================================

TMX_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/"
    "AndorsTrailRelease/andors-trail/"
    "refs/heads/master/AndorsTrail/res/xml/template.tmx"
)

TMX_TEMPLATE = ROOT / "template.tmx"

# ============================================================
# DOWNLOAD TEMPLATE
# ============================================================

def download_template():
    if TMX_TEMPLATE.exists():
        return

    print("Downloading template.tmx...")
    urllib.request.urlretrieve(TMX_TEMPLATE_URL, TMX_TEMPLATE)
    print("Downloaded template.tmx")


# ============================================================
# HELPERS
# ============================================================

def sid(text):

    return (
        text.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("'", "")
    )

def write_json(path, data):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ============================================================
# REGIONS
# ============================================================

REGIONS = {
    "grassland": {
        "animals": [
            "Rabbit", "Fox", "Deer", "Badger", "Mole",
            "Hare", "Field Mouse", "Boar", "Goat", "Pheasant",
            "Weasel", "Lynx", "Wolf", "Bison", "Antelope",
            "Raccoon", "Ferret", "Ram", "Mink", "Squirrel",
            "Elk", "Crow", "Falcon", "Otter", "Wild Dog"
        ],
        "forage": [
            "Dandelion", "Clover", "Chamomile", "Wild Onion", "Mint",
            "Lavender", "Berry", "Grass Seed", "Wild Garlic", "Mushroom",
            "Sage", "Thyme", "Rosehip", "Acorn", "Walnut",
            "Hazelnut", "Blueberry", "Blackberry", "Juniper", "Yarrow",
            "Flax", "Nettle", "Wild Carrot", "Parsley", "Sunflower Seed"
        ]
    },

    "desert": {
        "animals": [
            "Scorpion", "Camel", "Sand Fox", "Vulture", "Lizard",
            "Cobra", "Hyena", "Jackal", "Dune Beetle", "Meerkat",
            "Horned Toad", "Desert Wolf", "Gazelle", "Wild Cat", "Oryx",
            "Buzzard", "Dust Serpent", "Sand Rat", "Rattlesnake", "Mantis",
            "Dung Beetle", "Fire Ant", "Roadrunner", "Desert Hare", "Monitor"
        ],
        "forage": [
            "Cactus Fruit", "Dry Root", "Agave", "Date Fruit", "Desert Herb",
            "Aloe", "Palm Seed", "Yucca", "Dry Moss", "Spice Pod",
            "Sun Pepper", "Desert Flower", "Prickly Pear", "Sagebrush", "Tamarisk",
            "Salt Crystal", "Dried Berry", "Mesquite Bean", "Desert Mushroom", "Sand Mint",
            "Dust Leaf", "Bitter Root", "Scorpion Weed", "Cactus Sap", "Sunroot"
        ]
    },

    "swamp": {
        "animals": [
            "Alligator", "Frog", "Leech", "Marsh Rat", "Snake",
            "Bog Spider", "Heron", "Swamp Boar", "Mud Crab", "Mosquito",
            "Eel", "Turtle", "Toad", "Salamander", "Mire Wolf",
            "Water Snake", "Bog Hound", "Marsh Hawk", "Otter", "Mud Lizard",
            "Swamp Cat", "Fen Beetle", "Marsh Deer", "Croaker", "Snapping Turtle"
        ],
        "forage": [
            "Bog Moss", "Swamp Reed", "Water Lily", "Mud Mushroom", "Blackroot",
            "Marsh Herb", "Wet Bark", "Fen Berry", "Swamp Mint", "Leech Vine",
            "Mire Blossom", "Mud Fern", "Rot Fruit", "River Bulb", "Cattail",
            "Mire Seed", "Bog Flower", "Wet Herb", "Mud Pepper", "Swamp Garlic",
            "Frogwort", "Duckweed", "Water Nut", "Fen Grass", "Reed Stem"
        ]
    }
}

DEFAULT_REGION = REGIONS["grassland"]

ALL_REGION_NAMES = [
    "grassland",
    "shrubland",
    "swamp",
    "marsh",
    "bog",
    "desert",
    "tundra",
    "hills",
    "mountain",
    "alpine",
    "volcano",
    "river",
    "lake",
    "sea",
    "ocean",
    "small_cave",
    "large_cave",
    "dark_cave",
    "damp_cave",
    "deep_cave",
    "hell",
    "city",
    "farm"
]

for region in ALL_REGION_NAMES:
    if region not in REGIONS:
        REGIONS[region] = DEFAULT_REGION

# ============================================================
# CONSTANTS
# ============================================================

ITEM_ICON = "items_armours:1"
MONSTER_ICON = "monsters_arulirs:1"
ACTORCONDITION_ICON = "actorconditions_1:0"

# ============================================================
# DATA CONTAINERS
# ============================================================

ITEMLISTS = {}
ITEMCATEGORIES = {}
MONSTERLISTS = {}
DROPLISTS = {}
ACTORCONDITIONS = {}

# ============================================================
# ARMOR SLOT DEFINITIONS
# ============================================================

ARMOR_SLOT_DATA = {

    "shield": {
        "suffix": "Shield",
        "inventorySlot": "shield"
    },

    "head": {
        "suffix": "Helmet",
        "inventorySlot": "head"
    },

    "neck": {
        "suffix": "Necklace",
        "inventorySlot": "neck"
    },

    "body": {
        "suffix": "Armor",
        "inventorySlot": "body"
    },

    "hand": {
        "suffix": "Gloves",
        "inventorySlot": "hand"
    },

    "feet": {
        "suffix": "Boots",
        "inventorySlot": "feet"
    }
}

# ============================================================
# WEAPON TYPES
# ============================================================

WEAPON_TYPES = [
    "Sword",
    "Staff",
    "Wand",
    "Mace",
    "Dagger",
    "Spear"
]

# ============================================================
# CATEGORY HELPERS
# ============================================================

def create_weapon_category(guild):

    return {

        "id": f"crafted_weapon_{guild}",

        "name":
            f"Crafted {guild.title()} Weapons",

        "actionType": "equip",

        "size": "large",

        "inventorySlot": "weapon"
    }

def create_scroll_category(guild):

    return {

        "id": f"crafted_scroll_{guild}",

        "name":
            f"Crafted {guild.title()} Scroll",

        "actionType": "use"
    }

def create_potion_category(guild):

    return {

        "id": f"crafted_potion_{guild}",

        "name":
            f"Crafted {guild.title()} Potion",

        "actionType": "use"
    }

def create_armor_category(guild, slot):

    slot_info = ARMOR_SLOT_DATA[slot]

    return {

        "id": f"crafted_{slot}_{guild}",

        "name":
            f"Crafted {guild.title()} "
            f"{slot_info['suffix']}",

        "actionType": "equip",

        "size": "large",

        "inventorySlot":
            slot_info["inventorySlot"]
    }

# ============================================================
# BASE ITEM CATEGORIES
# ============================================================

ITEMCATEGORIES["animal"] = [

    {
        "id": "animal_parts",
        "name": "Animal Parts"
    }
]

ITEMCATEGORIES["forage"] = [

    {
        "id": "forage_ingredients",
        "name": "Forage Ingredients"
    }
]

ITEMCATEGORIES["mining"] = [

    {
        "id": "mining_ingredients",
        "name": "Mining Ingredients"
    },

    {
        "id": "mining_tools",
        "name": "Mining Tools",
        "actionType": "equip",
        "inventorySlot": "weapon"
    }
]

ITEMCATEGORIES["gardening"] = [

    {
        "id": "garden_ingredients",
        "name": "Garden Ingredients"
    },

    {
        "id": "garden_fresh",
        "name": "Fresh Garden Food",
        "actionType": "use"
    },

    {
        "id": "garden_tools",
        "name": "Garden Tools",
        "actionType": "equip",
        "inventorySlot": "weapon"
    }
]

# ============================================================
# SPELL GUILDS
# ============================================================

SPELL_GUILDS = [
    "mage",
    "cleric",
    "druid"
]

for guild in SPELL_GUILDS:

    ITEMCATEGORIES[guild] = []

    ITEMCATEGORIES[guild].append(
        create_weapon_category(guild)
    )

    ITEMCATEGORIES[guild].append(
        create_scroll_category(guild)
    )

    ITEMCATEGORIES[guild].append(
        create_potion_category(guild)
    )

    for slot in ARMOR_SLOT_DATA.keys():

        ITEMCATEGORIES[guild].append(
            create_armor_category(
                guild,
                slot
            )
        )

# ============================================================
# AILMENTS
# ============================================================

AILMENTS = [

    "Blight Fever",
    "Rotting Curse",
    "Plague Touch",
    "Venom Shock",
    "Frostbite",
    "Hellfire Burn",
    "Mind Rot",
    "Soul Drain",
    "Blood Curse",
    "Weakening Hex",
    "Shadow Plague",
    "Dark Paralysis",
    "Poison Blood",
    "Spirit Sickness",
    "Bone Decay",
    "Disease Cloud",
    "Chaos Fever",
    "Lung Rot",
    "Pestilence",
    "Curse of Agony",
    "Death Mark",
    "Nightmare Toxin",
    "Decay Touch",
    "Rotting Venom",
    "Chaotic Doom"
]

ACTORCONDITIONS["ailment"] = []

for ailment in AILMENTS:

    ACTORCONDITIONS["ailment"].append({

        "id": sid(ailment),

        "name": ailment,

        "iconID": ACTORCONDITION_ICON,

        "isNegative": 1,

        "abilityEffect": {

            "increaseAttackChance": -10,

            "increaseMaxHP": -10,

            "increaseMaxAP": -1
        }
    })

# ============================================================
# ANIMALS
# ============================================================

ITEMLISTS["animal"] = []
MONSTERLISTS["animal"] = []
DROPLISTS["animal"] = []

for region, data in REGIONS.items():

    for animal in data["animals"]:

        animal_id = f"{region}_"+sid(animal)

        hide_id = f"{region}_{animal_id}_hide"

        dl_id = f"dl_{region}_{animal_id}"

        ITEMLISTS["animal"].append({

            "id": hide_id,

            "name": f"{animal} Hide",

            "iconID": ITEM_ICON,

            "displaytype": "ordinary",

            "baseMarketCost": 20,

            "category": "animal_parts",

            "description":
                f"Hide taken from a "
                f"{animal.lower()}."
        })

        DROPLISTS["animal"].append({

            "id": dl_id,

            "items": [
                {
                    "itemID": hide_id,
                    "chance": "100",

                    "quantity": {
                        "min": 1,
                        "max": 2
                    }
                }
            ]
        })

        conditions = []

        for ailment in AILMENTS:

            conditions.append({

                "condition":
                    sid(ailment),

                "chance": 1,

                "magnitude": 1,

                "duration": 20
        })
    
        MONSTERLISTS["animal"].append({

            "id": animal_id,

            "name": animal,

            "iconID": MONSTER_ICON,

            "maxHP": 50,

            "attackChance": 60,

            "attackDamage": {
                "min": 5,
                "max": 10
            },

            "moveCost": 5,

            "attackCost": 4,

            "droplist": dl_id,

            "hitEffect": {

                "conditionsSource":
                    conditions
            }
        })

# ============================================================
# FORAGE
# ============================================================

FORAGE = [

    "Mint",
    "Lavender",
    "Rosemary",
    "Sage",
    "Chamomile",
    "Wild Garlic"
]

ITEMLISTS["forage"] = []

for region, data in REGIONS.items():

    for forage in data["forage"]:
        iid = f"{region}_{sid(forage)}"
        iname = f"{forage}"

        ITEMLISTS["forage"].append({

            "id": iid,

            "name": iname,

            "iconID": ITEM_ICON,

            "displaytype": "ordinary",

            "baseMarketCost": 10,

            "category":
                "forage_ingredients",

            "description":
                f"A forage ingredient "
                f"called {iname}."
        })

# ============================================================
# MINING
# ============================================================

MINING = [
    "Copper Ore",
    "Tin Ore",
    "Iron Ore",
    "Silver Ore",
    "Gold Ore",
    "Quartz",
    "Ruby",
    "Sapphire",
    "Emerald",
    "Obsidian",
    "Coal",
    "Sulfur",
    "Crystal Shard",
    "Granite",
    "Marble",
    "Topaz",
    "Amethyst",
    "Diamond",
    "Meteorite",
    "Mithril"
]

ITEMLISTS["mining"] = []

for ore in MINING:

    ITEMLISTS["mining"].append({

        "id": sid(ore),

        "name": ore,

        "iconID": ITEM_ICON,

        "displaytype": "ordinary",

        "baseMarketCost": 25,

        "category":
            "mining_ingredients",

        "description":
            f"A mining resource "
            f"called {ore}."
    })

ITEMLISTS["mining"].append({

    "id": "iron_pick_axe",

    "name": "Iron Pick Axe",

    "iconID": ITEM_ICON,

    "displaytype": "ordinary",

    "baseMarketCost": 100,

    "category": "mining_tools",

    "description":
        "A heavy mining tool.",

    "equipEffect": {

        "increaseAttackDamage": {
            "min": 2,
            "max": 5
        }
    }
})

# ============================================================
# GARDENING
# ============================================================

GARDENING = [
    "Tomato",
    "Potato",
    "Corn",
    "Onion",
    "Carrot",
    "Rosemary",
    "Lavender",
    "Mint",
    "Basil",
    "Pepper",
    "Cabbage",
    "Pumpkin",
    "Bean",
    "Pea",
    "Apple",
    "Pear",
    "Plum",
    "Berry",
    "Mushroom",
    "Garlic"
]

ITEMLISTS["gardening"] = []

for crop in GARDENING:

    crop_id = "garden_"+sid(crop)

    ITEMLISTS["gardening"].append({

        "id": crop_id,

        "name": crop,

        "iconID": ITEM_ICON,

        "displaytype": "ordinary",

        "baseMarketCost": 10,

        "category": "garden_fresh",

        "description":
            f"Fresh {crop.lower()} "
            f"ready to eat.",


        "useEffect": {
            "increaseCurrentHP":{
                "min":5,
                "max":5
            }
        }
    })

    ITEMLISTS["gardening"].append({

        "id": f"{crop_id}_seed",

        "name": f"{crop} Seed",

        "iconID": ITEM_ICON,

        "displaytype": "ordinary",

        "baseMarketCost": 3,

        "category":
            "garden_ingredients",

        "description":
            f"Seeds used to grow "
            f"{crop.lower()}."
    })

ITEMLISTS["gardening"].append({

    "id": "iron_hoe",

    "name": "Iron Hoe",

    "iconID": ITEM_ICON,

    "displaytype": "ordinary",

    "baseMarketCost": 75,

    "category": "garden_tools",

    "description":
        "A gardening hoe weapon.",

    "equipEffect": {

        "increaseAttackDamage": {
            "min": 1,
            "max": 4
        }
    }
})

# ============================================================
# SPELL DATA
# ============================================================

SPELL_DATA = {

    "mage": {

        "offensive": [
            "Fireball",
            "Lightning Bolt",
            "Magic Missile",
            "Cone of Cold",
            "Meteor Swarm",
            "Chain Lightning",
            "Ice Storm",
            "Disintegrate",
            "Finger of Death",
            "Delayed Blast Fireball",
            "Arcane Burst",
            "Flame Strike",
            "Thunder Wave",
            "Blizzard",
            "Chaos Bolt",
            "Soul Burn",
            "Nether Blast",
            "Shadow Flame",
            "Astral Spear",
            "Void Nova",
            "Crystal Lance",
            "Inferno",
            "Storm Sphere",
            "Mind Rupture",
            "Frost Lance"
        ],

        "defensive": [
            "Mage Armor",
            "Shield",
            "Arcane Barrier",
            "Mirror Image",
            "Stoneskin",
            "Prismatic Wall",
            "Mana Shield",
            "Mystic Ward",
            "Frost Armor",
            "Aegis",
            "Temporal Guard",
            "Crystal Shield",
            "Arcane Veil",
            "Energy Barrier",
            "Soul Ward",
            "Void Shield",
            "Astral Armor",
            "Guardian Sphere",
            "Blink Shield",
            "Phantom Guard",
            "Ward of Ages",
            "Mystic Cloak",
            "Planar Barrier",
            "Arcane Sanctuary",
            "Spell Reflection"
        ]
    },

    "cleric": {

        "offensive": [
            "Holy Smite",
            "Divine Wrath",
            "Sacred Flame",
            "Sun Strike",
            "Judgement",
            "Radiant Burst",
            "Hammer of Faith",
            "Exorcism",
            "Holy Nova",
            "Celestial Spear",
            "Purge Evil",
            "Wrath of Dawn",
            "Consecration",
            "Divine Lance",
            "Light Hammer",
            "Blessed Fire",
            "Faith Bolt",
            "Holy Storm",
            "Sunfire",
            "Sacred Judgement",
            "Heavens Fury",
            "Radiant Spear",
            "Divine Flame",
            "Smite Undead",
            "Sacred Storm"
        ],

        "defensive": [
            "Divine Shield",
            "Blessing",
            "Sanctuary",
            "Holy Barrier",
            "Guardian Angel",
            "Sacred Ward",
            "Healing Aura",
            "Prayer Shield",
            "Faith Armor",
            "Protection",
            "Holy Grace",
            "Shield of Light",
            "Blessed Armor",
            "Celestial Guard",
            "Redemption",
            "Aegis of Faith",
            "Divine Protection",
            "Sacred Veil",
            "Holy Resistance",
            "Spirit Ward",
            "Purity",
            "Shield of Faith",
            "Light Ward",
            "Grace of Dawn",
            "Guardian Prayer"
        ]
    },

    "druid": {

        "offensive": [
            "Thorn Strike",
            "Poison Bloom",
            "Natures Wrath",
            "Vine Lash",
            "Earthquake",
            "Hurricane",
            "Wildfire",
            "Storm Call",
            "Venom Roots",
            "Moonfire",
            "Sunstrike",
            "Entangle",
            "Nature Bolt",
            "Oak Smash",
            "Tornado",
            "Spirit Thorn",
            "Feral Rage",
            "Earth Spear",
            "Bloom Rot",
            "Nature Shock",
            "Wild Growth",
            "Forest Fury",
            "Plague Seeds",
            "Stone Rain",
            "Wrath of Beasts"
        ],

        "defensive": [
            "Barkskin",
            "Nature Shield",
            "Regrowth",
            "Spirit Guard",
            "Earth Ward",
            "Stone Skin",
            "Healing Roots",
            "Wild Protection",
            "Moon Ward",
            "Forest Veil",
            "Natural Armor",
            "Oak Shield",
            "Nature Blessing",
            "Renewal",
            "Lifebloom",
            "Ancient Ward",
            "Storm Barrier",
            "Wild Grace",
            "Spirit Bark",
            "Earth Guard",
            "Feral Shield",
            "Bloom Shield",
            "Root Barrier",
            "Nature Sanctuary",
            "Beast Ward"
        ]
    }
}

# ============================================================
# SPELL CONTENT GENERATION
# ============================================================

for guild, spells in SPELL_DATA.items():

    ACTORCONDITIONS[guild] = []

    ITEMLISTS[f"weapon_{guild}"] = []
    ITEMLISTS[f"scroll_{guild}"] = []
    ITEMLISTS[f"potion_{guild}"] = []
    ITEMLISTS[f"armor_{guild}"] = []

    # --------------------------------------------------------
    # OFFENSIVE SPELLS
    # --------------------------------------------------------

    for i, spell in enumerate(
        spells["offensive"]
    ):

        spell_id = sid(spell)

        weapon_type = WEAPON_TYPES[
            i % len(WEAPON_TYPES)
        ]

        weapon_name = (
            f"{spell} {weapon_type}"
        )

        ACTORCONDITIONS[guild].append({

            "id": spell_id,

            "name": spell,

            "iconID": ACTORCONDITION_ICON,

            "isNegative": 1,

            "abilityEffect": {

                "increaseAttackChance": 15,

                "increaseAttackDamage": {
                    "min": 10,
                    "max": 25
                }
            }
        })

        ITEMLISTS[f"weapon_{guild}"].append({

            "id":
                f"{spell_id}_{sid(weapon_type)}",

            "name": weapon_name,

            "iconID": ITEM_ICON,

            "displaytype": "ordinary",

            "baseMarketCost": 250,

            "category":
                f"crafted_weapon_{guild}",

            "description":
                f"A magical "
                f"{weapon_type.lower()} "
                f"infused with {spell}.",

            "hitEffect": {

                "conditionsSource": [
                    {
                        "condition": spell_id,
                        "magnitude": 1,
                        "duration": 20,
                        "chance": 100
                    }
                ]
            },

            "equipEffect": {

                "increaseAttackDamage": {
                    "min": 10,
                    "max": 20
                },

                "increaseAttackChance": 10
            }
        })

        ITEMLISTS[f"scroll_{guild}"].append({

            "id": f"{spell_id}_scroll",

            "name":
                f"Scroll of {spell}",

            "iconID": ITEM_ICON,

            "displaytype": "ordinary",

            "baseMarketCost": 100,

            "category":
                f"crafted_scroll_{guild}",

            "description":
                f"A magical scroll "
                f"containing {spell}.",

            "useEffect": {

                "conditionsSource": [
                    {
                        "condition": spell_id,
                        "magnitude": 1,
                        "duration": 20,
                        "chance": 100
                    }
                ]
            }
        })

        ITEMLISTS[f"potion_{guild}"].append({

            "id": f"{spell_id}_potion",

            "name":
                f"{spell} Potion",

            "iconID": ITEM_ICON,

            "displaytype": "ordinary",

            "baseMarketCost": 120,

            "category":
                f"crafted_potion_{guild}",

            "description":
                f"A magical potion "
                f"infused with {spell}.",

            "useEffect": {

                "conditionsSource": [
                    {
                        "condition": spell_id,
                        "magnitude": 2,
                        "duration": 10,
                        "chance": 100
                    }
                ]
            }
        })

    # --------------------------------------------------------
    # DEFENSIVE SPELLS
    # --------------------------------------------------------

    slot_keys = list(
        ARMOR_SLOT_DATA.keys()
    )

    for i, spell in enumerate(
        spells["defensive"]
    ):

        spell_id = sid(spell)

        slot = slot_keys[
            i % len(slot_keys)
        ]

        slot_info = ARMOR_SLOT_DATA[
            slot
        ]

        armor_suffix = (
            slot_info["suffix"]
        )

        armor_name = (
            f"{spell} {armor_suffix}"
        )

        ACTORCONDITIONS[guild].append({

            "id": spell_id,

            "name": spell,

            "iconID": ACTORCONDITION_ICON,

            "isNegative": 0,

            "abilityEffect": {

                "increaseDefense": 15,

                "increaseMaxHP": 25
            }
        })

        ITEMLISTS[f"armor_{guild}"].append({

            "id":
                f"{spell_id}_{slot}",

            "name": armor_name,

            "iconID": ITEM_ICON,

            "displaytype":
                "ordinary",

            "baseMarketCost": 200,

            "category":
                f"crafted_{slot}_{guild}",

            "description":
                f"Protective gear "
                f"blessed with "
                f"{spell}.",

            "equipEffect": {

                "increaseDefense": 15,

                "increaseMaxHP": 25
            }
        })

# ============================================================
# WRITE JSON FILES
# ============================================================

write_json(
    RAW / "itemlist_animal.json",
    ITEMLISTS["animal"]
)

write_json(
    RAW / "monsterlist_animal.json",
    MONSTERLISTS["animal"]
)

write_json(
    RAW / "droplists_animal.json",
    DROPLISTS["animal"]
)

write_json(
    RAW / "itemcategories_animal.json",
    ITEMCATEGORIES["animal"]
)

write_json(
    RAW / "itemlist_forage.json",
    ITEMLISTS["forage"]
)

write_json(
    RAW / "itemcategories_forage.json",
    ITEMCATEGORIES["forage"]
)

write_json(
    RAW / "itemlist_mining.json",
    ITEMLISTS["mining"]
)

write_json(
    RAW / "itemcategories_mining.json",
    ITEMCATEGORIES["mining"]
)

write_json(
    RAW / "itemlist_gardening.json",
    ITEMLISTS["gardening"]
)

write_json(
    RAW / "itemcategories_gardening.json",
    ITEMCATEGORIES["gardening"]
)

write_json(
    RAW / "actorconditions_ailment.json",
    ACTORCONDITIONS["ailment"]
)

for guild in SPELL_GUILDS:

    write_json(
        RAW / f"actorconditions_{guild}.json",
        ACTORCONDITIONS[guild]
    )

    write_json(
        RAW / f"itemlist_weapon_{guild}.json",
        ITEMLISTS[f"weapon_{guild}"]
    )

    write_json(
        RAW / f"itemlist_scroll_{guild}.json",
        ITEMLISTS[f"scroll_{guild}"]
    )

    write_json(
        RAW / f"itemlist_potion_{guild}.json",
        ITEMLISTS[f"potion_{guild}"]
    )

    write_json(
        RAW / f"itemlist_armor_{guild}.json",
        ITEMLISTS[f"armor_{guild}"]
    )

    write_json(
        RAW / f"itemcategories_{guild}.json",
        ITEMCATEGORIES[guild]
    )

# ============================================================
# LOADRESOURCES.XML
# ============================================================

LOADRESOURCES = """<?xml version="1.0" encoding="utf-8"?>
<resources>

    <array name="loadresource_items">
        <item>@raw/itemlist_animal</item>
        <item>@raw/itemlist_forage</item>
        <item>@raw/itemlist_mining</item>
        <item>@raw/itemlist_gardening</item>
        <item>@raw/itemlist_weapon_mage</item>
        <item>@raw/itemlist_weapon_cleric</item>
        <item>@raw/itemlist_weapon_druid</item>
        <item>@raw/itemlist_scroll_mage</item>
        <item>@raw/itemlist_scroll_cleric</item>
        <item>@raw/itemlist_scroll_druid</item>
        <item>@raw/itemlist_potion_mage</item>
        <item>@raw/itemlist_potion_cleric</item>
        <item>@raw/itemlist_potion_druid</item>
        <item>@raw/itemlist_armor_mage</item>
        <item>@raw/itemlist_armor_cleric</item>
        <item>@raw/itemlist_armor_druid</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_animal</item>
    </array>

    <array name="loadresource_droplists">
        <item>@raw/droplists_animal</item>
    </array>

    <array name="loadresource_itemcategories">
        <item>@raw/itemcategories_animal</item>
        <item>@raw/itemcategories_forage</item>
        <item>@raw/itemcategories_mining</item>
        <item>@raw/itemcategories_gardening</item>
        <item>@raw/itemcategories_mage</item>
        <item>@raw/itemcategories_cleric</item>
        <item>@raw/itemcategories_druid</item>
    </array>

    <array name="loadresource_actorconditions">
        <item>@raw/actorconditions_ailment</item>
        <item>@raw/actorconditions_mage</item>
        <item>@raw/actorconditions_cleric</item>
        <item>@raw/actorconditions_druid</item>
    </array>

</resources>
"""

with open(
    VALUES / "loadresources.xml",
    "w",
    encoding="utf-8"
) as f:

    f.write(LOADRESOURCES)

# ============================================================
# TMX MAPS
# ============================================================

download_template()

template_tree = ET.parse(TMX_TEMPLATE)
template_root = template_tree.getroot()

for region in ALL_REGION_NAMES:

    root = deepcopy(template_root)

    # --------------------------------------------------------
    # Spawn_animal
    # --------------------------------------------------------

    spawn_layer = ET.SubElement(root, "objectgroup")
    spawn_layer.set("name", "Spawn_animal")

    spawn = ET.SubElement(spawn_layer, "object")
    spawn.set("id", "1")
    spawn.set("x", "0")
    spawn.set("y", "0")
    spawn.set("width", "1280")
    spawn.set("height", "1280")

    props = ET.SubElement(spawn, "properties")

    ET.SubElement(
        props,
        "property",
        name="spawnGroup",
        value=f"{region}_animals"
    )

    ET.SubElement(
        props,
        "property",
        name="spawnCount",
        value="3"
    )

    # --------------------------------------------------------
    # Keys_forage
    # --------------------------------------------------------

    forage_layer = ET.SubElement(root, "objectgroup")
    forage_layer.set("name", "Keys_forage")

    obj = ET.SubElement(forage_layer, "object")
    obj.set("id", "2")
    obj.set("x", "128")
    obj.set("y", "128")
    obj.set("width", "32")
    obj.set("height", "32")

    props = ET.SubElement(obj, "properties")

    ET.SubElement(
        props,
        "property",
        name="droplist",
        value=f"dl_forage_{region}"
    )

    ET.SubElement(
        props,
        "property",
        name="respawnHours",
        value="24"
    )

    # --------------------------------------------------------
    # Keys_mining
    # --------------------------------------------------------

    mining_layer = ET.SubElement(root, "objectgroup")
    mining_layer.set("name", "Keys_mining")

    obj = ET.SubElement(mining_layer, "object")
    obj.set("id", "3")
    obj.set("x", "256")
    obj.set("y", "256")
    obj.set("width", "32")
    obj.set("height", "32")

    props = ET.SubElement(obj, "properties")

    ET.SubElement(
        props,
        "property",
        name="droplist",
        value="dl_all_mining"
    )

    ET.SubElement(
        props,
        "property",
        name="requiredWeapon",
        value="tool_pickaxe"
    )

    ET.SubElement(
        props,
        "property",
        name="respawnHours",
        value="48"
    )

    # --------------------------------------------------------
    # Keys_garden
    # --------------------------------------------------------

    garden_layer = ET.SubElement(root, "objectgroup")
    garden_layer.set("name", "Keys_garden")

    obj = ET.SubElement(garden_layer, "object")
    obj.set("id", "4")
    obj.set("x", "384")
    obj.set("y", "384")
    obj.set("width", "32")
    obj.set("height", "32")

    props = ET.SubElement(obj, "properties")

    ET.SubElement(
        props,
        "property",
        name="droplist",
        value="dl_all_garden"
    )

    ET.SubElement(
        props,
        "property",
        name="requiredWeapon",
        value="tool_hoe"
    )

    ET.SubElement(
        props,
        "property",
        name="respawnHours",
        value="72"
    )

    # --------------------------------------------------------
    # Keys_garden_plant
    # --------------------------------------------------------

    plant_layer = ET.SubElement(root, "objectgroup")
    plant_layer.set("name", "Keys_garden_plant")

    obj = ET.SubElement(plant_layer, "object")
    obj.set("id", "5")
    obj.set("x", "512")
    obj.set("y", "512")
    obj.set("width", "32")
    obj.set("height", "32")

    props = ET.SubElement(obj, "properties")

    ET.SubElement(
        props,
        "property",
        name="requiredWeapon",
        value="tool_hoe"
    )

    ET.SubElement(
        props,
        "property",
        name="yieldMultiplier",
        value="3"
    )

    ET.SubElement(
        props,
        "property",
        name="respawnHours",
        value="72"
    )

    ET.indent(root)

    tree = ET.ElementTree(root)

    tree.write(
        XML / f"{region}.tmx",
        encoding="utf-8",
        xml_declaration=True
    )

# ============================================================
# COMPLETE
# ============================================================

print("")
print("========================================")
print("Generation Complete")
print("========================================")
print("")

for path in RAW.glob("*.json"):

    print(path.name)

print(f"Items: {len(ITEMLISTS)}")
print(f"Item Categories: {len(ITEMCATEGORIES)}")
print(f"Monsters: {len(MONSTERLISTS)}")
print(f"Droplists: {len(DROPLISTS)}")
print(f"Actor Conditions: {len(ACTORCONDITIONS)}")

print("")
print("Done.")
