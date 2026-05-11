#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_crafting_content_v4.py

Andor's Trail crafting ecosystem generator
ATCS compatible
v0.8.15+ compatible

Generates:

./raw/
    actorconditions_crafting.json
    conversationlist_crafting.json
    droplists_crafting.json
    itemcategories_crafting.json
    itemlist_crafting.json
    monsterlist_crafting.json
    questlist_crafting.json

./values/
    loadresources.xml

./xml/
    <region>.tmx
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
# DOWNLOAD TEMPLATE
# ============================================================

def download_template():
    if TMX_TEMPLATE.exists():
        return

    print("Downloading template.tmx...")
    urllib.request.urlretrieve(TMX_TEMPLATE_URL, TMX_TEMPLATE)
    print("Downloaded template.tmx")

# ============================================================
# DATA CONTAINERS
# ============================================================

ITEMS = []
MONSTERS = []
DROPLISTS = []
ITEMCATEGORIES = []

# ============================================================
# HELPERS
# ============================================================

def sid(text):
    return (
        text.lower()
        .replace(" ", "_")
        .replace("-", "_")
    )

def add_item(
    item_id,
    name,
    category,
    description,
    value=10,
    weight=1
):
    ITEMS.append({
        "id": item_id,
        "name": name,
        "category": category,
        "description": description,
        "iconID": "items_armours:1",
        "displaytype": "default",
        "value": value,
        "weight": weight
    })

def add_monster(
    monster_id,
    name,
    droplist,
    spawn_group
):
    MONSTERS.append({
        "id": monster_id,
        "name": name,
        "iconID": "monsters_arulirs:1",
        "description": f"A wild {name.lower()} commonly found in the region.",
        "faction": "wild",
        "maxHP": 30,
        "baseAttack": 6,
        "baseDefense": 3,
        "attackCost": 8,
        "moveCost": 8,
        "droplist": droplist,
        "spawnGroup": spawn_group,
        "canMove": True,
        "aggressive": False
    })

def add_tag_droplist(dl_id, tag):
    DROPLISTS.append({
        "id": dl_id,
        "items": [
            {
                "tag": tag,
                "quantity": {
                    "min": 1,
                    "max": 1
                },
                "chance": 100
            }
        ]
    })

def add_item_droplist(dl_id, item_id):
    DROPLISTS.append({
        "id": dl_id,
        "items": [
            {
                "itemID": item_id,
                "quantity": {
                    "min": 1,
                    "max": 1
                },
                "chance": 100
            }
        ]
    })

# ============================================================
# ITEM CATEGORIES
# ============================================================

for region in ALL_REGION_NAMES:

    ITEMCATEGORIES.append({
        "id": f"ingredient_{region}",
        "name": f"{region.replace('_', ' ').title()} Forage Ingredients"
    })

    ITEMCATEGORIES.append({
        "id": f"animalpart_{region}",
        "name": f"{region.replace('_', ' ').title()} Animal Parts"
    })

ITEMCATEGORIES.extend([
    {
        "id": "ingredient_mining",
        "name": "Mining Ingredients"
    },
    {
        "id": "ingredient_gardening",
        "name": "Gardening Ingredients"
    }
])

# ============================================================
# REGION CONTENT
# ============================================================

for region, data in REGIONS.items():

    # --------------------------------------------------------
    # FORAGE ITEMS
    # --------------------------------------------------------

    for forage in data["forage"]:

        iid = f"{region}_{sid(forage)}"

        add_item(
            item_id=iid,
            name=forage,
            category=f"ingredient_{region}",
            description=(
                f"A naturally occurring resource gathered in "
                f"{region.replace('_', ' ')} regions."
            ),
            value=5
        )

    add_tag_droplist(
        f"dl_forage_{region}",
        f"ingredient_{region}"
    )

    # --------------------------------------------------------
    # ANIMALS
    # --------------------------------------------------------

    for animal in data["animals"]:

        animal_sid = sid(animal)

        drop_item = f"{region}_{animal_sid}_hide"

        add_item(
            item_id=drop_item,
            name=f"{animal} Hide",
            category=f"animalpart_{region}",
            description=(
                f"Crafting material harvested from a "
                f"{animal.lower()}."
            ),
            value=15
        )

        dl_id = f"dl_{region}_{animal_sid}"

        add_item_droplist(dl_id, drop_item)

        monster_id = f"{region}_{animal_sid}"

        add_monster(
            monster_id=monster_id,
            name=animal,
            droplist=dl_id,
            spawn_group=f"{region}_animals"
        )

# ============================================================
# MINING ITEMS
# ============================================================

MINING_TYPES = [
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

for i in range(50):

    base = MINING_TYPES[i % len(MINING_TYPES)]

    iid = f"mining_{sid(base)}_{i}"

    add_item(
        item_id=iid,
        name=base,
        category="ingredient_mining",
        description=f"A valuable mining resource: {base.lower()}.",
        value=25
    )

add_tag_droplist(
    "dl_all_mining",
    "ingredient_mining"
)

# ============================================================
# GARDEN ITEMS
# ============================================================

GARDEN_TYPES = [
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

for i in range(50):

    crop = GARDEN_TYPES[i % len(GARDEN_TYPES)]

    crop_id = f"garden_{sid(crop)}_{i}"
    seed_id = f"seed_{sid(crop)}_{i}"

    add_item(
        item_id=crop_id,
        name=crop,
        category="ingredient_gardening",
        description=f"A cultivated garden crop: {crop.lower()}.",
        value=12
    )

    add_item(
        item_id=seed_id,
        name=f"{crop} Seed",
        category="ingredient_gardening",
        description=f"Seeds used to grow {crop.lower()}.",
        value=4
    )

add_tag_droplist(
    "dl_all_garden",
    "ingredient_gardening"
)

# ============================================================
# TOOLS
# ============================================================

add_item(
    "tool_pickaxe",
    "Pick Axe",
    "ingredient_mining",
    "A heavy mining tool.",
    value=100
)

add_item(
    "tool_hoe",
    "Hoe",
    "ingredient_gardening",
    "A gardening tool used for planting.",
    value=100
)

# ============================================================
# WRITE JSON FILES
# ============================================================

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

write_json(RAW / "itemlist_crafting.json", ITEMS)
write_json(RAW / "monsterlist_crafting.json", MONSTERS)
write_json(RAW / "droplists_crafting.json", DROPLISTS)
write_json(RAW / "itemcategories_crafting.json", ITEMCATEGORIES)

write_json(RAW / "actorconditions_crafting.json", [])
write_json(RAW / "conversationlist_crafting.json", [])
write_json(RAW / "questlist_crafting.json", [])

# ============================================================
# LOADRESOURCES.XML
# ============================================================

LOADRESOURCES = """<?xml version="1.0" encoding="utf-8"?>
<resources>

<string-array name="itemlists">
    <item>itemlist_crafting</item>
</string-array>

<string-array name="monsterlists">
    <item>monsterlist_crafting</item>
</string-array>

<string-array name="droplists">
    <item>droplists_crafting</item>
</string-array>

<string-array name="itemcategories">
    <item>itemcategories_crafting</item>
</string-array>

<string-array name="actorconditions">
    <item>actorconditions_crafting</item>
</string-array>

<string-array name="conversationlists">
    <item>conversationlist_crafting</item>
</string-array>

<string-array name="questlists">
    <item>questlist_crafting</item>
</string-array>

</resources>
"""

with open(VALUES / "loadresources.xml", "w", encoding="utf-8") as f:
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
print("Crafting content generation complete")
print("========================================")
print("")
print("Generated:")
print("  raw/itemlist_crafting.json")
print("  raw/itemcategories_crafting.json")
print("  raw/monsterlist_crafting.json")
print("  raw/droplists_crafting.json")
print("  raw/actorconditions_crafting.json")
print("  raw/conversationlist_crafting.json")
print("  raw/questlist_crafting.json")
print("  values/loadresources.xml")
print("  xml/*.tmx")
print("")
print(f"Items: {len(ITEMS)}")
print(f"Monsters: {len(MONSTERS)}")
print(f"Droplists: {len(DROPLISTS)}")
print("")
print("Done.")
