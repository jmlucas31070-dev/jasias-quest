#!/usr/bin/env python3

import json
import os
import random

# ============================================================
# FACTION RESOURCE GENERATOR
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

    <array name="loadresource_droplists">
        <item>@raw/droplists_faction_centaur</item>
        <item>@raw/droplists_faction_dark_dwarf</item>
        <item>@raw/droplists_faction_deep_gnome</item>
        <item>@raw/droplists_faction_drow_elf</item>
        <item>@raw/droplists_faction_elf</item>
        <item>@raw/droplists_faction_faerie</item>
        <item>@raw/droplists_faction_giant</item>
        <item>@raw/droplists_faction_gnome</item>
        <item>@raw/droplists_faction_goblin</item>
        <item>@raw/droplists_faction_half_elf</item>
        <item>@raw/droplists_faction_halfling</item>
        <item>@raw/droplists_faction_hill_dwarf</item>
        <item>@raw/droplists_faction_hobgoblin</item>
        <item>@raw/droplists_faction_human</item>
        <item>@raw/droplists_faction_kender</item>
        <item>@raw/droplists_faction_kobold</item>
        <item>@raw/droplists_faction_minotaur</item>
        <item>@raw/droplists_faction_mountain_dwarf</item>
        <item>@raw/droplists_faction_ogre</item>
        <item>@raw/droplists_faction_orc</item>
        <item>@raw/droplists_faction_sea_elf</item>
        <item>@raw/droplists_faction_wood_elf</item>
    </array>

    <array name="loadresource_items">
        <item>@raw/itemlist_faction_centaur</item>
        <item>@raw/itemlist_faction_dark_dwarf</item>
        <item>@raw/itemlist_faction_deep_gnome</item>
        <item>@raw/itemlist_faction_drow_elf</item>
        <item>@raw/itemlist_faction_elf</item>
        <item>@raw/itemlist_faction_faerie</item>
        <item>@raw/itemlist_faction_giant</item>
        <item>@raw/itemlist_faction_gnome</item>
        <item>@raw/itemlist_faction_goblin</item>
        <item>@raw/itemlist_faction_half_elf</item>
        <item>@raw/itemlist_faction_halfling</item>
        <item>@raw/itemlist_faction_hill_dwarf</item>
        <item>@raw/itemlist_faction_hobgoblin</item>
        <item>@raw/itemlist_faction_human</item>
        <item>@raw/itemlist_faction_kender</item>
        <item>@raw/itemlist_faction_kobold</item>
        <item>@raw/itemlist_faction_minotaur</item>
        <item>@raw/itemlist_faction_mountain_dwarf</item>
        <item>@raw/itemlist_faction_ogre</item>
        <item>@raw/itemlist_faction_orc</item>
        <item>@raw/itemlist_faction_sea_elf</item>
        <item>@raw/itemlist_faction_wood_elf</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_faction_centaur</item>
        <item>@raw/monsterlist_faction_dark_dwarf</item>
        <item>@raw/monsterlist_faction_deep_gnome</item>
        <item>@raw/monsterlist_faction_drow_elf</item>
        <item>@raw/monsterlist_faction_elf</item>
        <item>@raw/monsterlist_faction_faerie</item>
        <item>@raw/monsterlist_faction_giant</item>
        <item>@raw/monsterlist_faction_gnome</item>
        <item>@raw/monsterlist_faction_goblin</item>
        <item>@raw/monsterlist_faction_half_elf</item>
        <item>@raw/monsterlist_faction_halfling</item>
        <item>@raw/monsterlist_faction_hill_dwarf</item>
        <item>@raw/monsterlist_faction_hobgoblin</item>
        <item>@raw/monsterlist_faction_human</item>
        <item>@raw/monsterlist_faction_kender</item>
        <item>@raw/monsterlist_faction_kobold</item>
        <item>@raw/monsterlist_faction_minotaur</item>
        <item>@raw/monsterlist_faction_mountain_dwarf</item>
        <item>@raw/monsterlist_faction_ogre</item>
        <item>@raw/monsterlist_faction_orc</item>
        <item>@raw/monsterlist_faction_sea_elf</item>
        <item>@raw/monsterlist_faction_wood_elf</item>
    </array>

</resources>
"""

# ============================================================
# FACTIONS
# ============================================================

FACTIONS = [
    "human",
    "half_elf",
    "elf",
    "wood_elf",
    "sea_elf",
    "drow_elf",
    "hill_dwarf",
    "mountain_dwarf",
    "dark_dwarf",
    "kender",
    "gnome",
    "deep_gnome",
    "faerie",
    "goblin",
    "hobgoblin",
    "ogre",
    "centaur",
    "minotaur",
    "orc",
    "kobold",
    "giant",
    "halfling"
]

# ============================================================
# NPC CLASSES
# ============================================================

NPC_CLASSES = [
    "Warrior",
    "Guard",
    "Scout",
    "Hunter",
    "Mage",
    "Priest",
    "Archer",
    "Shaman",
    "Knight",
    "Assassin",
    "Raider",
    "Chief",
    "Captain",
    "Champion",
    "Berserker",
    "Mystic",
    "Witch",
    "Ranger",
    "Defender",
    "Mercenary",
    "Alchemist",
    "Beastmaster",
    "Warden",
    "Sentry",
    "Commander"
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
    "Hammer",
    "Battle Axe"
]

WEAPON_PREFIXES = [
    "Iron",
    "Steel",
    "Dark",
    "Shadow",
    "Ancient",
    "Savage",
    "Royal",
    "Heavy",
    "Mystic",
    "Runed",
    "Blood",
    "Golden"
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
# RACE DROP ITEMS
# ============================================================

RACE_ITEMS = {
    "human": ["Bread", "Torch", "Steel Coin", "Traveler Cloak"],
    "half_elf": ["Silver Pendant", "Forest Herb", "Elven Scroll"],
    "elf": ["Moon Crystal", "Elven Wine", "Silver Leaf"],
    "wood_elf": ["Oak Bowstring", "Forest Charm", "Nature Stone"],
    "sea_elf": ["Pearl Necklace", "Coral Gem", "Seaweed Potion"],
    "drow_elf": ["Spider Fang", "Shadow Crystal", "Dark Rune"],
    "hill_dwarf": ["Mining Pick", "Stone Mug", "Iron Nugget"],
    "mountain_dwarf": ["Forged Hammer", "Bronze Coin", "Steel Ore"],
    "dark_dwarf": ["Obsidian Shard", "Dark Ale", "Black Iron"],
    "kender": ["Lucky Dice", "Tiny Knife", "Travel Pouch"],
    "gnome": ["Clockwork Gear", "Small Hammer", "Magic Lens"],
    "deep_gnome": ["Crystal Dust", "Cave Gem", "Tunnel Map"],
    "faerie": ["Fairy Dust", "Glow Flower", "Tiny Bell"],
    "goblin": ["Rusty Knife", "Bone Charm", "Scrap Metal"],
    "hobgoblin": ["War Banner", "Iron Spike", "Battle Totem"],
    "ogre": ["Huge Club", "Raw Meat", "Heavy Chain"],
    "centaur": ["Horse Charm", "Forest Spear", "Leather Strap"],
    "minotaur": ["Horn Fragment", "Labyrinth Stone", "Battle Horn"],
    "orc": ["War Paint", "Orc Talisman", "Skull Trophy"],
    "kobold": ["Dragon Tooth", "Candle Stub", "Tiny Spear"],
    "giant": ["Giant Bone", "Huge Boulder", "Massive Chain"],
    "halfling": ["Pipe Weed", "Small Bread", "Lucky Ring"]
}

# ============================================================
# HELPERS
# ============================================================

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def random_damage():
    low = random.randint(4, 20)
    high = low + random.randint(5, 25)
    return low, high

# ============================================================
# CREATE FACTION FILES
# ============================================================

for faction in FACTIONS:

    faction_name = faction.replace("_", " ").title()

    monsters = []
    weapons = []
    armors = []
    misc_items = []
    droplists = []

    drop_pool = []

    # ========================================================
    # CREATE WEAPONS
    # ========================================================

    for i in range(9):

        weapon_name = (
            f"{faction_name} "
            f"{random.choice(WEAPON_PREFIXES)} "
            f"{random.choice(WEAPON_TYPES)}"
        )

        item_id = f"{faction}_weapon_{i+1}"

        item = {
            "id": item_id,
            "name": weapon_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(100, 2500),
            "category": "weapon",
            "description": f"A weapon crafted by the {faction_name}.",
            "equipEffect": {
                "increaseAttackChance": random.randint(5, 20),
                "increaseAttackDamage": {
                    "min": random.randint(5, 15),
                    "max": random.randint(20, 40)
                }
            }
        }

        weapons.append(item)
        drop_pool.append(item_id)

    # ========================================================
    # CREATE ARMOR
    # ========================================================

    for i in range(15):

        slot_id, slot_name = ARMOR_SLOTS[i % len(ARMOR_SLOTS)]

        armor_name = (
            f"{faction_name} "
            f"{random.choice(WEAPON_PREFIXES)} "
            f"{slot_name}"
        )

        item_id = f"{faction}_armor_{i+1}"

        item = {
            "id": item_id,
            "name": armor_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(150, 3000),
            "category": slot_id,
            "description": f"Armor worn by the {faction_name}.",
            "equipEffect": {
                "increaseArmor": random.randint(5, 40),
                "increaseMaxHP": random.randint(10, 100)
            }
        }

        armors.append(item)
        drop_pool.append(item_id)

    # ========================================================
    # CREATE RACE ITEMS
    # ========================================================

    race_item_pool = RACE_ITEMS.get(faction, ["Ancient Trinket"])

    for i in range(15):

        item_name = random.choice(race_item_pool)

        item_id = f"{faction}_item_{i+1}"

        item = {
            "id": item_id,
            "name": item_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(25, 1000),
            "category": "misc",
            "description": f"A common item carried by the {faction_name}."
        }

        misc_items.append(item)
        drop_pool.append(item_id)

    # ========================================================
    # CREATE NPCS + DROPLISTS
    # ========================================================

    for i in range(25):

        npc_name = (
            f"{faction_name} "
            f"{random.choice(NPC_CLASSES)}"
        )

        low, high = random_damage()

        droplist_id = f"droplist_{faction}_{i+1}"

        monster = {
            "id": f"{faction}_npc_{i+1}",
            "name": npc_name,
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(60, 600),
            "attackChance": random.randint(40, 90),
            "attackDamage": {
                "min": low,
                "max": high
            },
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8),
            "droplistID": droplist_id
        }

        monsters.append(monster)

        drop_item = random.choice(drop_pool)

        droplist = {
            "id": droplist_id,
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
            f"monsterlist_faction_{faction}.json"
        ),
        monsters
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"itemlist_faction_weapon_{faction}.json"
        ),
        weapons
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"itemlist_faction_armor_{faction}.json"
        ),
        armors
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"itemlist_faction_items_{faction}.json"
        ),
        misc_items
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            f"droplists_faction_{faction}.json"
        ),
        droplists
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
print(" Faction Resources Generated")
print("===================================================")
print("Factions:", len(FACTIONS))
print("Files created for each faction:")
print("  monsterlist_faction_*.json")
print("  itemlist_faction_weapon_*.json")
print("  itemlist_faction_armor_*.json")
print("  itemlist_faction_items_*.json")
print("  droplists_faction_*.json")
print("===================================================")
