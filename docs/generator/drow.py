#!/usr/bin/env python3

import json
import os
import random

# ============================================================
# DROW + DRAGON RESOURCE GENERATOR
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

    <array name="loadresource_actorconditions">
        <item>@raw/actorconditions_dragon</item>
    </array>

    <array name="loadresource_droplists">
        <item>@raw/droplists_drow_astral</item>
        <item>@raw/droplists_drow_base</item>
        <item>@raw/droplists_drow_electric</item>
        <item>@raw/droplists_drow_fire</item>
        <item>@raw/droplists_drow_light</item>
        <item>@raw/droplists_drow_shadow</item>
        <item>@raw/droplists_drow_smoke</item>
        <item>@raw/droplists_drow_stone</item>
        <item>@raw/droplists_dragon</item>
    </array>

    <array name="loadresource_items">
        <item>@raw/itemlist_drow_armor_astral</item>
        <item>@raw/itemlist_drow_armor_base</item>
        <item>@raw/itemlist_drow_armor_electric</item>
        <item>@raw/itemlist_drow_armor_fire</item>
        <item>@raw/itemlist_drow_armor_light</item>
        <item>@raw/itemlist_drow_armor_shadow</item>
        <item>@raw/itemlist_drow_armor_smoke</item>
        <item>@raw/itemlist_drow_armor_stone</item>
        <item>@raw/itemlist_drow_weapon_astral</item>
        <item>@raw/itemlist_drow_weapon_base</item>
        <item>@raw/itemlist_drow_weapon_electric</item>
        <item>@raw/itemlist_drow_weapon_fire</item>
        <item>@raw/itemlist_drow_weapon_light</item>
        <item>@raw/itemlist_drow_weapon_shadow</item>
        <item>@raw/itemlist_drow_weapon_smoke</item>
        <item>@raw/itemlist_drow_weapon_stone</item>
        <item>@raw/itemlist_dragon</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_drow_astral</item>
        <item>@raw/monsterlist_drow_base</item>
        <item>@raw/monsterlist_drow_electric</item>
        <item>@raw/monsterlist_drow_fire</item>
        <item>@raw/monsterlist_drow_light</item>
        <item>@raw/monsterlist_drow_shadow</item>
        <item>@raw/monsterlist_drow_smoke</item>
        <item>@raw/monsterlist_drow_stone</item>
        <item>@raw/monsterlist_dragon</item>
    </array>

</resources>
"""

# ============================================================
# DROW RACES
# ============================================================

DROW_RACES = [
    "base",
    "shadow",
    "light",
    "smoke",
    "electric",
    "fire",
    "stone",
    "astral"
]

# ============================================================
# DROW NPC TYPES
# ============================================================

DROW_CLASSES = [
    "Assassin",
    "Priestess",
    "Shadowblade",
    "Scout",
    "Warlock",
    "Guard",
    "Beastmaster",
    "Spider Tamer",
    "Witch",
    "Hunter",
    "Raider",
    "Sorcerer",
    "Executioner",
    "Champion",
    "Knight",
    "Mage",
    "Archer",
    "Poisoner",
    "Dark Cleric",
    "Royal Guard",
    "Crypt Stalker",
    "Nightblade",
    "Tunnel Scout",
    "Webspinner",
    "Dark Summoner"
]

# ============================================================
# WEAPON DATA
# ============================================================

WEAPON_TYPES = [
    "Knife",
    "Sword",
    "Club",
    "Staff",
    "Mace",
    "Dagger",
    "Spear",
    "Whip",
    "Crossbow"
]

WEAPON_PREFIXES = [
    "Dark",
    "Shadow",
    "Venom",
    "Night",
    "Ancient",
    "Poison",
    "Moon",
    "Blood",
    "Spider",
    "Void"
]

# ============================================================
# ARMOR SLOTS
# ============================================================

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
# DRAGON DATA
# ============================================================

DRAGON_AGES = [
    "Wyrmling",
    "Youngster",
    "Adult",
    "Elder",
    "Ancient"
]

DRAGON_TYPES = [
    "Black",
    "Blue",
    "Green",
    "White",
    "Red",
    "Chromatic",
    "Brass",
    "Bronze",
    "Copper",
    "Silver",
    "Gold",
    "Platinum"
]

# ============================================================
# DRAGON SPELLS
# ============================================================

DRAGON_SPELLS = [
    "Flame Breath",
    "Frost Breath",
    "Lightning Storm",
    "Poison Cloud",
    "Meteor Strike",
    "Arcane Roar",
    "Shadow Flame",
    "Crystal Breath",
    "Thunder Breath",
    "Inferno Blast",
    "Acid Spray",
    "Divine Roar",
    "Storm Call",
    "Earthquake",
    "Dragon Fear",
    "Void Breath",
    "Celestial Fire",
    "Mana Burst",
    "Soul Burn",
    "Ancient Wrath",
    "Plasma Surge",
    "Astral Nova",
    "Death Breath",
    "Skyfire",
    "Dragon Rage"
]

# ============================================================
# DRAGON TREASURE
# ============================================================

DRAGON_TREASURE = [
    "Dragon Scale",
    "Dragon Fang",
    "Ancient Coin",
    "Golden Crown",
    "Ruby Necklace",
    "Emerald Ring",
    "Crystal Orb",
    "Dragon Egg",
    "Treasure Chest",
    "Ancient Relic",
    "Silver Chalice",
    "Royal Banner",
    "Enchanted Gem",
    "Dragon Claw",
    "Ancient Scroll",
    "Sacred Idol",
    "Golden Statue",
    "Dragon Heart",
    "Mystic Rune",
    "Magic Crystal",
    "Ancient Sword",
    "Royal Armor",
    "Treasure Map",
    "Dragon Eye",
    "Ancient Artifact"
]

# ============================================================
# HELPERS
# ============================================================

def random_damage():
    low = random.randint(5, 25)
    high = low + random.randint(5, 30)
    return low, high

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ============================================================
# DRAGON SPELL CONDITIONS
# ============================================================

dragon_conditions = []

for i, spell in enumerate(DRAGON_SPELLS):

    condition = {
        "id": f"dragon_spell_{i+1}",
        "name": spell,
        "iconID": ACTORCONDITION_ICON,
        "isNegative": 0,
        "abilityEffect": {
            "increaseAttackDamage": {
                "min": random.randint(10, 30),
                "max": random.randint(40, 80)
            }
        }
    }

    dragon_conditions.append(condition)

# ============================================================
# CREATE DROW CONTENT
# ============================================================

def create_drow_race(race):

    monsters = []
    droplists = []

    weapons = []
    armors = []

    equipment_ids = []

    race_name = race.capitalize()

    # ========================================================
    # WEAPONS
    # ========================================================

    for i in range(9):

        weapon_name = (
            f"{race_name} "
            f"{random.choice(WEAPON_PREFIXES)} "
            f"{random.choice(WEAPON_TYPES)}"
        )

        weapon_id = f"{race}_weapon_{i+1}"

        item = {
            "id": weapon_id,
            "name": weapon_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(200, 2500),
            "category": "weapon",
            "description": f"A weapon forged by {race_name} drow.",
            "equipEffect": {
                "increaseAttackChance": random.randint(5, 20),
                "increaseAttackDamage": {
                    "min": random.randint(5, 15),
                    "max": random.randint(20, 40)
                }
            }
        }

        weapons.append(item)
        equipment_ids.append(weapon_id)

    # ========================================================
    # ARMOR
    # ========================================================

    for i in range(15):

        slot_id, slot_name = ARMOR_SLOTS[i % len(ARMOR_SLOTS)]

        armor_name = (
            f"{race_name} "
            f"{random.choice(WEAPON_PREFIXES)} "
            f"{slot_name}"
        )

        armor_id = f"{race}_armor_{i+1}"

        item = {
            "id": armor_id,
            "name": armor_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(200, 3000),
            "category": slot_id,
            "description": f"Armor worn by {race_name} drow.",
            "equipEffect": {
                "increaseArmor": random.randint(5, 35),
                "increaseMaxHP": random.randint(10, 100)
            }
        }

        armors.append(item)
        equipment_ids.append(armor_id)

    # ========================================================
    # NPCS + DROPS
    # ========================================================

    for i in range(25):

        npc_name = (
            f"{race_name} Drow "
            f"{random.choice(DROW_CLASSES)}"
        )

        low, high = random_damage()

        drop_id = f"droplist_{race}_{i+1}"

        monster = {
            "id": f"{race}_drow_{i+1}",
            "name": npc_name,
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(80, 600),
            "attackChance": random.randint(45, 90),
            "attackDamage": {
                "min": low,
                "max": high
            },
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8),
            "droplistID": drop_id
        }

        monsters.append(monster)

        drop_item = random.choice(equipment_ids)

        droplist = {
            "id": drop_id,
            "items": [
                {
                    "item": drop_item,
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                }
            ]
        }

        droplists.append(droplist)

    # ========================================================
    # WRITE FILES
    # ========================================================

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"monsterlist_drow_{race}.json"
        ),
        monsters
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"droplists_drow_{race}.json"
        ),
        droplists
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"itemlist_drow_weapon_{race}.json"
        ),
        weapons
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"itemlist_drow_armor_{race}.json"
        ),
        armors
    )

# ============================================================
# GENERATE ALL DROW RACES
# ============================================================

for race in DROW_RACES:
    create_drow_race(race)

# ============================================================
# CREATE DRAGONS
# ============================================================

dragon_monsters = []
dragon_items = []
dragon_droplists = []

# ============================================================
# DRAGON TREASURE ITEMS
# ============================================================

for i in range(25):

    item = {
        "id": f"dragon_treasure_{i+1}",
        "name": random.choice(DRAGON_TREASURE),
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": random.randint(500, 10000),
        "category": "misc",
        "description": "A treasure hoarded by dragons."
    }

    dragon_items.append(item)

# ============================================================
# DRAGONS
# ============================================================

dragon_index = 1

for dragon_type in DRAGON_TYPES:

    for age in DRAGON_AGES:

        low, high = random_damage()

        max_hp = {
            "Wyrmling": 100,
            "Youngster": 250,
            "Adult": 600,
            "Elder": 1000,
            "Ancient": 1800
        }[age]

        drop_id = f"droplist_dragon_{dragon_index}"

        monster = {
            "id": f"dragon_{dragon_index}",
            "name": f"{age} {dragon_type} Dragon",
            "iconID": MONSTER_ICON,
            "maxHP": max_hp,
            "attackChance": random.randint(50, 95),
            "attackDamage": {
                "min": low + 10,
                "max": high + 30
            },
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8),
            "droplistID": drop_id
        }

        # ====================================================
        # SPELLS FOR STRONGER DRAGONS
        # ====================================================

        if age in ["Adult", "Elder", "Ancient"]:

            condition = random.choice(dragon_conditions)

            monster["hitEffect"] = {
                "conditionsSource": [
                    {
                        "condition": condition["id"],
                        "chance": 100,
                        "magnitude": 1
                    }
                ]
            }

        dragon_monsters.append(monster)

        # ====================================================
        # DROP LIST
        # ====================================================

        treasure = random.choice(dragon_items)

        droplist = {
            "id": drop_id,
            "items": [
                {
                    "item": treasure["id"],
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                }
            ]
        }

        dragon_droplists.append(droplist)

        dragon_index += 1

# ============================================================
# WRITE DRAGON FILES
# ============================================================

write_json(
    os.path.join(
        OUTPUT_RAW,
        "monsterlist_dragon.json"
    ),
    dragon_monsters
)

write_json(
    os.path.join(
        OUTPUT_RAW,
        "actorconditions_dragon.json"
    ),
    dragon_conditions
)

write_json(
    os.path.join(
        OUTPUT_RAW,
        "itemlist_dragon.json"
    ),
    dragon_items
)

write_json(
    os.path.join(
        OUTPUT_RAW,
        "droplists_dragon.json"
    ),
    dragon_droplists
)

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
print(" Drow + Dragon Resources Generated")
print("===================================================")
print("Drow Races:", len(DROW_RACES))
print("Dragon Monsters:", len(dragon_monsters))
print("Dragon Spells:", len(dragon_conditions))
print("Dragon Treasure Items:", len(dragon_items))
print("===================================================")
print("./raw/monsterlist_drow_*.json")
print("./raw/droplists_drow_*.json")
print("./raw/itemlist_drow_weapon_*.json")
print("./raw/itemlist_drow_armor_*.json")
print("./raw/monsterlist_dragon.json")
print("./raw/actorconditions_dragon.json")
print("./raw/itemlist_dragon.json")
print("./raw/droplists_dragon.json")
print("===================================================")
