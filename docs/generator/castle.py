#!/usr/bin/env python3

import json
import os
import random

# ============================================================
# CASTLE RESOURCE GENERATOR
#
# Generates:
#   ./raw/monsterlist_castle.json
#   ./raw/itemlist_weapon.json
#   ./raw/itemlist_armor.json
#   ./raw/itemlist_shop.json
#   ./raw/monsterlist_town.json
# ============================================================

OUTPUT_RAW = "./raw"
OUTPUT_VALUES = "./values"

os.makedirs(OUTPUT_RAW, exist_ok=True)
os.makedirs(OUTPUT_VALUES, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

ITEM_ICON = "items_armours:1"
MONSTER_ICON = "monsters_arulirs:1"
ACTORCONDITION_ICON = "actorconditions_1:0"

# ============================================================
# LOADRESOURCES.XML
# ============================================================

LOADRESOURCES_XML = """<?xml version="1.0" encoding="utf-8"?>
<resources>

    <array name="loadresource_items">
        <item>@raw/itemlist_armor</item>
        <item>@raw/itemlist_shop</item>
        <item>@raw/itemlist_weapon</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_castle</item>
        <item>@raw/monsterlist_town</item>
    </array>

</resources>
"""

# ============================================================
# DATA TABLES
# ============================================================

CASTLE_NPC_TYPES = [
    "Castle Guard",
    "Royal Knight",
    "Court Wizard",
    "Dungeon Keeper",
    "Royal Archer",
    "Castle Cook",
    "Stable Master",
    "Royal Priest",
    "Castle Blacksmith",
    "Royal Advisor",
    "Castle Servant",
    "Treasury Guard",
    "Gate Watchman",
    "Royal Captain",
    "Castle Scout",
    "Royal Messenger",
    "Barracks Soldier",
    "Royal Scribe",
    "Castle Alchemist",
    "Elite Knight",
    "Castle Butler",
    "Royal Champion",
    "Castle Hunter",
    "Training Master",
    "Royal Duelist"
]

TOWN_NPC_TYPES = [
    "Villager",
    "Merchant",
    "Blacksmith",
    "Farmer",
    "Innkeeper",
    "Hunter",
    "Traveler",
    "Guard",
    "Baker",
    "Tailor",
    "Miner",
    "Lumberjack",
    "Priest",
    "Herbalist",
    "Fisherman",
    "Scholar",
    "Stable Keeper",
    "Cook",
    "Messenger",
    "Carpenter",
    "Jeweler",
    "Tavern Bard",
    "Town Watchman",
    "Street Vendor",
    "Apprentice"
]

WEAPON_TYPES = [
    "Knife",
    "Sword",
    "Club",
    "Staff",
    "Mace",
    "Hammer",
    "Spear",
    "Dagger",
    "Battle Axe",
    "Longsword",
    "Shortsword",
    "Warhammer",
    "Halberd",
    "Flail",
    "Scythe",
    "Rapier",
    "Claymore",
    "Morningstar",
    "Crossbow",
    "Bow"
]

WEAPON_PREFIXES = [
    "Iron",
    "Steel",
    "Golden",
    "Ancient",
    "Royal",
    "Heavy",
    "Sharp",
    "Battle",
    "Knight",
    "Dark",
    "Silver",
    "Bronze",
    "Enchanted",
    "Runed",
    "Savage"
]

ARMOR_PREFIXES = [
    "Iron",
    "Steel",
    "Royal",
    "Golden",
    "Knight",
    "Heavy",
    "Blessed",
    "Ancient",
    "Runed",
    "Dark",
    "Silver",
    "Bronze",
    "Guardian",
    "Defender",
    "Battle"
]

SHOP_ITEMS = [
    "Torch",
    "Rope",
    "Bread",
    "Apple",
    "Health Potion",
    "Mana Potion",
    "Lockpick",
    "Camping Kit",
    "Lantern",
    "Fishing Rod",
    "Map",
    "Compass",
    "Bandage",
    "Arrow Bundle",
    "Water Flask",
    "Pickaxe",
    "Hammer",
    "Cooking Pot",
    "Traveler Boots",
    "Gloves",
    "Cape",
    "Tent",
    "Magic Scroll",
    "Herbs",
    "Gemstone",
    "Silver Ring",
    "Backpack",
    "Oil Flask",
    "Spyglass",
    "Needle Kit",
    "Book",
    "Feather Pen",
    "Bottle",
    "Wooden Shield",
    "Traveler Hat",
    "Fur Cloak",
    "Knife",
    "Ale Mug",
    "Dried Meat",
    "Cheese Wheel",
    "Fruit Basket",
    "Lucky Charm",
    "Bell",
    "Sleeping Bag",
    "Bone Necklace",
    "Iron Ore",
    "Coal Sack",
    "Leather Strap",
    "Travel Journal",
    "Magic Crystal"
]

ARMOR_SLOTS = [
    ("shield", "Shield"),
    ("head", "Helmet"),
    ("neck", "Amulet"),
    ("body", "Armor"),
    ("hand", "Gloves"),
    ("feet", "Boots"),
    ("leftring", "Ring")
]

# ============================================================
# OUTPUT ARRAYS
# ============================================================

castle_monsters = []
town_monsters = []

weapon_items = []
armor_items = []
shop_items = []

# ============================================================
# HELPERS
# ============================================================

def random_damage():
    low = random.randint(3, 20)
    high = low + random.randint(5, 20)
    return low, high

# ============================================================
# CREATE CASTLE NPCS
# ============================================================

def create_castle_npcs():

    for i in range(25):

        npc_type = CASTLE_NPC_TYPES[i]

        low, high = random_damage()

        npc = {
            "id": f"castle_npc_{i+1}",
            "name": npc_type,
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(80, 400),
            "attackChance": random.randint(40, 85),
            "attackDamage": {
                "min": low,
                "max": high
            },
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8)
        }

        castle_monsters.append(npc)

# ============================================================
# CREATE TOWN NPCS
# ============================================================

def create_town_npcs():

    for i in range(50):

        npc_type = random.choice(TOWN_NPC_TYPES)

        low, high = random_damage()

        npc = {
            "id": f"town_npc_{i+1}",
            "name": npc_type,
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(40, 250),
            "attackChance": random.randint(20, 65),
            "attackDamage": {
                "min": low,
                "max": high
            },
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8)
        }

        town_monsters.append(npc)

# ============================================================
# CREATE WEAPONS
# ============================================================

def create_weapons():

    for i in range(25):

        prefix = random.choice(WEAPON_PREFIXES)
        weapon = random.choice(WEAPON_TYPES)

        low = random.randint(4, 15)
        high = low + random.randint(5, 20)

        item = {
            "id": f"weapon_{i+1}",
            "name": f"{prefix} {weapon}",
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(100, 2000),
            "category": "weapon",
            "description": f"A {weapon.lower()} commonly used by adventurers.",
            "equipEffect": {
                "increaseAttackDamage": {
                    "min": low,
                    "max": high
                },
                "increaseAttackChance": random.randint(2, 15)
            }
        }

        weapon_items.append(item)

# ============================================================
# CREATE ARMOR
# ============================================================

def create_armor():

    armor_count = 15

    for i in range(armor_count):

        slot_id, slot_name = ARMOR_SLOTS[i % len(ARMOR_SLOTS)]

        prefix = random.choice(ARMOR_PREFIXES)

        item = {
            "id": f"armor_{slot_id}_{i+1}",
            "name": f"{prefix} {slot_name}",
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(150, 2500),
            "category": slot_id,
            "description": f"A protective {slot_name.lower()} worn by adventurers.",
            "equipEffect": {
                "increaseArmor": random.randint(5, 40),
                "increaseMaxHP": random.randint(10, 100)
            }
        }

        armor_items.append(item)

# ============================================================
# CREATE SHOP ITEMS
# ============================================================

def create_shop_items():

    for i in range(50):

        item_name = random.choice(SHOP_ITEMS)

        item = {
            "id": f"shop_item_{i+1}",
            "name": item_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(5, 500),
            "category": "misc",
            "description": f"A useful item commonly sold in shops."
        }

        shop_items.append(item)

# ============================================================
# GENERATE EVERYTHING
# ============================================================

create_castle_npcs()
create_town_npcs()

create_weapons()
create_armor()
create_shop_items()

# ============================================================
# WRITE FILES
# ============================================================

with open(
    os.path.join(OUTPUT_RAW, "monsterlist_castle.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(castle_monsters, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "monsterlist_town.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(town_monsters, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "itemlist_weapon.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(weapon_items, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "itemlist_armor.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(armor_items, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "itemlist_shop.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(shop_items, f, indent=4)

with open(
    os.path.join(OUTPUT_VALUES, "loadresources.xml"),
    "w",
    encoding="utf-8"
) as f:

    f.write(LOADRESOURCES_XML)

# ============================================================
# SUMMARY
# ============================================================

print("===================================================")
print(" Castle Resources Generated")
print("===================================================")
print(f"Castle NPCs: {len(castle_monsters)}")
print(f"Town NPCs: {len(town_monsters)}")
print(f"Weapons: {len(weapon_items)}")
print(f"Armor Items: {len(armor_items)}")
print(f"Shop Items: {len(shop_items)}")
print("===================================================")
print("./raw/monsterlist_castle.json")
print("./raw/monsterlist_town.json")
print("./raw/itemlist_weapon.json")
print("./raw/itemlist_armor.json")
print("./raw/itemlist_shop.json")
print("===================================================")
