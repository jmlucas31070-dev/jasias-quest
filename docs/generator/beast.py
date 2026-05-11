#!/usr/bin/env python3

import json
import os
import random

# ============================================================
# ASTRAL BEAST RESOURCE GENERATOR
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
# REGIONS
# ============================================================

REGIONS = [
    "Lumia",
    "Kranix",
    "Ignora",
    "Hesperia",
    "Lucidiah",
    "Illystrius",
    "Sejor",
    "Bellom",
    "Dorado"
]

BEASTS_PER_REGION = 90

# ============================================================
# ITEM SLOT ROTATION
# ============================================================

ITEM_SLOTS = [
    ("beast_weapon", "items_weapons"),
    ("beast_shield", "items_shields"),
    ("beast_head", "items_head"),
    ("beast_neck", "items_neck"),
    ("beast_body", "items_body"),
    ("beast_hand", "items_hands"),
    ("beast_feet", "items_feet"),
    ("beast_ring", "items_rings")
]

# ============================================================
# ITEM CATEGORIES
# ============================================================

ITEM_CATEGORIES = [
    {
        "id": "beast_weapon",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "weapon"
    },
    {
        "id": "beast_shield",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "shield"
    },
    {
        "id": "beast_head",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "head"
    },
    {
        "id": "beast_neck",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "neck"
    },
    {
        "id": "beast_body",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "body"
    },
    {
        "id": "beast_hand",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "hand"
    },
    {
        "id": "beast_feet",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "feet"
    },
    {
        "id": "beast_ring",
        "name": "Beast",
        "actionType": "equip",
        "size": "light",
        "inventorySlot": "leftring"
    }
]

# ============================================================
# NAME PARTS
# ============================================================

PREFIXES = [
    "Astral", "Void", "Celestial", "Lunar", "Solar",
    "Shadow", "Ancient", "Mystic", "Thunder", "Crystal",
    "Infernal", "Frozen", "Wild", "Storm", "Arcane"
]

CREATURES = [
    "Owlbear", "Drake", "Phoenix", "Wolf", "Tiger",
    "Hydra", "Golem", "Serpent", "Leviathan", "Manticore",
    "Wyvern", "Minotaur", "Cyclops", "Djinn", "Griffin",
    "Basilisk", "Kraken", "Specter", "Titan", "Chimera"
]

# ============================================================
# 90 MOVE / CONDITION NAMES
# ============================================================

MOVE_NAMES = [
    "Haste", "Berserk", "Guard", "Poison", "Burn",
    "Frostbite", "Focus", "Regeneration", "Weaken", "Stone Skin",
    "Thunderclap", "Venom Strike", "Iron Defense", "Quickstep", "Soul Drain",
    "Arcane Shield", "Blazing Fury", "Shadow Curse", "Toxic Mist", "Holy Light",
    "Lifesteal", "Bloodlust", "Earthquake", "Cyclone", "Meteor Crash",
    "Ice Prison", "Mind Break", "Phantom Strike", "Stormcall", "Healing Wind",
    "Firestorm", "Static Charge", "Dark Pact", "Light Beam", "Sandstorm",
    "Tidal Wave", "Skyfall", "Gravity Well", "Moonfire", "Solar Burst",
    "Chaos Bolt", "Spirit Link", "Death Mark", "Silence", "Hex",
    "Crushing Blow", "Battle Cry", "Magic Surge", "Soul Barrier", "Nightmare",
    "Dragon Roar", "Vengeance", "Curse", "Feral Rage", "Divine Blessing",
    "Blizzard", "Lava Burst", "Tornado", "Mirror Skin", "Shockwave",
    "Chain Lightning", "Crystal Armor", "Doom", "Corruption", "Purify",
    "Starfall", "Wind Slash", "Water Pulse", "Rock Smash", "Nature Touch",
    "Spirit Fire", "Void Pulse", "Rage", "Piercing Fang", "Energy Shield",
    "Mana Burn", "Smokescreen", "Battle Focus", "Blood Drain", "Time Warp",
    "Spectral Claw", "Inferno", "Frozen Heart", "Thunder Fang", "Sacred Flame",
    "Shadowstep", "Venom Cloud", "Iron Will", "Celestial Aura", "Astral Fury"
]

# ============================================================
# CONDITION EFFECTS
# ============================================================

def generate_effect(index):

    effect_type = index % 6

    if effect_type == 0:
        return {
            "increaseAttackChance": random.randint(5, 20)
        }

    elif effect_type == 1:
        return {
            "increaseCriticalSkill": random.randint(5, 15)
        }

    elif effect_type == 2:
        return {
            "increaseBlockChance": random.randint(5, 20)
        }

    elif effect_type == 3:
        return {
            "increaseArmor": random.randint(5, 30)
        }

    elif effect_type == 4:
        return {
            "increaseMovePoints": random.randint(1, 3)
        }

    else:
        return {
            "increaseAttackDamage": {
                "min": random.randint(2, 10),
                "max": random.randint(10, 25)
            }
        }

# ============================================================
# CREATE ACTOR CONDITIONS
# ============================================================

ACTORCONDITIONS = []

for i, move_name in enumerate(MOVE_NAMES):

    ACTORCONDITIONS.append({
        "id": f"beast_condition_{i+1}",
        "name": move_name,
        "iconID": ACTORCONDITION_ICON,
        "isNegative": 0,
        "abilityEffect": generate_effect(i)
    })

# ============================================================
# TRAINERS
# ============================================================

def create_region_trainers():

    trainers = []

    for region in REGIONS:

        for gym in range(1, 10):

            leader = {
                "id": f"{region.lower()}_gymleader_{gym}",
                "name": f"{region} Gym Leader {gym}",
                "iconID": MONSTER_ICON,
                "maxHP": 250 + (gym * 20),
                "attackChance": 70,
                "attackDamage": {
                    "min": 15,
                    "max": 35
                }
            }

            trainers.append(leader)

            for t in range(1, 4):

                trainer = {
                    "id": f"{region.lower()}_trainer_{gym}_{t}",
                    "name": f"{region} Gym Trainer {gym}-{t}",
                    "iconID": MONSTER_ICON,
                    "maxHP": 100 + (gym * 10),
                    "attackChance": 55,
                    "attackDamage": {
                        "min": 8,
                        "max": 18
                    }
                }

                trainers.append(trainer)

        grandmaster = {
            "id": f"{region.lower()}_grandmaster",
            "name": f"{region} Grandmaster",
            "iconID": MONSTER_ICON,
            "maxHP": 800,
            "attackChance": 95,
            "attackDamage": {
                "min": 50,
                "max": 100
            }
        }

        trainers.append(grandmaster)

    return trainers

# ============================================================
# CREATE BEASTS / ITEMS / TRAINERS / DROPLISTS
# ============================================================

def create_beasts():

    monsters = []
    items = []
    beast_droplists = []

    trainer_monsters = []
    trainer_droplists = []

    slot_index = 0
    icon_counter = 1

    for region in REGIONS:

        for i in range(BEASTS_PER_REGION):

            # ====================================================
            # NAME
            # ====================================================

            prefix = random.choice(PREFIXES)
            creature = random.choice(CREATURES)

            beast_name = f"{prefix} {creature}"

            full_name = f"{beast_name} from {region} region"

            beast_id = f"beast_{region.lower()}_{i+1}"

            item_id = f"item_{beast_id}"

            condition = random.choice(ACTORCONDITIONS)

            # ====================================================
            # STATS
            # ====================================================

            max_hp = random.randint(50, 500)

            min_damage = random.randint(5, 35)
            max_damage = min_damage + random.randint(5, 35)

            # ====================================================
            # BEAST DROP LIST
            # ====================================================

            beast_droplist_id = f"droplist_{beast_id}"

            beast_droplist = {
                "id": beast_droplist_id,
                "items": [
                    {
                        "item": "gold",
                        "quantity": {
                            "min": int(max_hp / 10),
                            "max": int(max_hp / 10)
                        },
                        "chance": "100"
                    }
                ]
            }

            beast_droplists.append(beast_droplist)

            # ====================================================
            # BEAST MONSTER
            # ====================================================

            monster = {
                "id": beast_id,
                "name": full_name,
                "iconID": MONSTER_ICON,
                "maxHP": max_hp,
                "attackChance": random.randint(50, 90),
                "attackDamage": {
                    "min": min_damage,
                    "max": max_damage
                },
                "moveCost": random.randint(3, 8),
                "attackCost": random.randint(3, 8),
                "droplistID": beast_droplist_id,
                "hitEffect": {
                    "conditionsSource": [
                        {
                            "condition": condition["id"],
                            "chance": 100,
                            "magnitude": 1
                        }
                    ]
                }
            }

            monsters.append(monster)

            # ====================================================
            # ITEM
            # ====================================================

            category, icon_prefix = ITEM_SLOTS[
                slot_index % len(ITEM_SLOTS)
            ]

            item = {
                "id": item_id,
                "name": full_name,
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "hasManualPrice": 1,
                "baseMarketCost": max_hp * 10,
                "category": category,
                "description": f"This is a {beast_name} caught in the {region} region.",
                "hitEffect": {
                    "conditionsSource": [
                        {
                            "condition": condition["id"],
                            "magnitude": 1,
                            "duration": 999,
                            "chance": 100
                        }
                    ]
                },
                "equipEffect": {
                    "increaseAttackDamage": {
                        "min": random.randint(5, 20),
                        "max": random.randint(20, 50)
                    },
                    "increaseAttackChance": random.randint(5, 20)
                }
            }

            items.append(item)

            # ====================================================
            # TRAINER DROPLIST
            # ====================================================

            trainer_id = f"trainer_{beast_id}"

            trainer_droplist_id = f"droplist_{trainer_id}"

            trainer_droplist = {
                "id": trainer_droplist_id,
                "items": [
                    {
                        "item": item_id,
                        "quantity": {
                            "min": 1,
                            "max": 1
                        },
                        "chance": "100"
                    }
                ]
            }

            trainer_droplists.append(trainer_droplist)

            # ====================================================
            # TRAINER MONSTER
            # ====================================================

            trainer_monster = {
                "id": trainer_id,
                "name": f"{beast_name} Trainer",
                "iconID": MONSTER_ICON,
                "maxHP": max_hp + random.randint(50, 150),
                "attackChance": random.randint(50, 90),
                "attackDamage": {
                    "min": min_damage + 5,
                    "max": max_damage + 10
                },
                "moveCost": random.randint(3, 8),
                "attackCost": random.randint(3, 8),
                "droplistID": trainer_droplist_id,
                "hitEffect": {
                    "conditionsSource": [
                        {
                            "condition": condition["id"],
                            "chance": 100,
                            "magnitude": 1
                        }
                    ]
                }
            }

            trainer_monsters.append(trainer_monster)

            slot_index += 1
            icon_counter += 1

    return (
        monsters,
        items,
        beast_droplists,
        trainer_monsters,
        trainer_droplists
    )

# ============================================================
# LOADRESOURCES.XML
# ============================================================

LOADRESOURCES_XML = """<?xml version="1.0" encoding="utf-8"?>
<resources>

    <array name="loadresource_actorconditions">
        <item>@raw/actorconditions_beast</item>
    </array>

    <array name="loadresource_droplists">
        <item>@raw/droplists_beast</item>
    </array>

    <array name="loadresource_itemcategories">
        <item>@raw/itemcategories_beast</item>
    </array>

    <array name="loadresource_items">
        <item>@raw/itemlist_beast</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_beast</item>
        <item>@raw/monsterlist_trainer</item>
    </array>

</resources>
"""

# ============================================================
# WRITE JSON
# ============================================================

def write_json(path, data):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ============================================================
# MAIN
# ============================================================

def main():

    (
        monsters,
        items,
        beast_droplists,
        trainer_monsters,
        trainer_droplists
    ) = create_beasts()

    region_trainers = create_region_trainers()

    combined_trainers = trainer_monsters + region_trainers

    combined_droplists = (
        beast_droplists +
        trainer_droplists
    )

    # ========================================================
    # WRITE FILES
    # ========================================================

    write_json(
        os.path.join(OUTPUT_RAW, "actorconditions_beast.json"),
        ACTORCONDITIONS
    )

    write_json(
        os.path.join(OUTPUT_RAW, "droplists_beast.json"),
        combined_droplists
    )

    write_json(
        os.path.join(OUTPUT_RAW, "itemcategories_beast.json"),
        ITEM_CATEGORIES
    )

    write_json(
        os.path.join(OUTPUT_RAW, "itemlist_beast.json"),
        items
    )

    write_json(
        os.path.join(OUTPUT_RAW, "monsterlist_beast.json"),
        monsters
    )

    write_json(
        os.path.join(OUTPUT_RAW, "monsterlist_trainer.json"),
        combined_trainers
    )

    with open(
        os.path.join(OUTPUT_VALUES, "loadresources.xml"),
        "w",
        encoding="utf-8"
    ) as f:

        f.write(LOADRESOURCES_XML)

    # ========================================================
    # SUMMARY
    # ========================================================

    print("===================================================")
    print(" Astral Beast Resources Generated")
    print("===================================================")
    print(f"Regions: {len(REGIONS)}")
    print(f"Beasts: {len(monsters)}")
    print(f"Trainer Monsters: {len(trainer_monsters)}")
    print(f"Region Trainers: {len(region_trainers)}")
    print(f"Actor Conditions: {len(ACTORCONDITIONS)}")
    print(f"Items: {len(items)}")
    print(f"Droplists: {len(combined_droplists)}")
    print("===================================================")
    print("Generated Files:")
    print("./raw/actorconditions_beast.json")
    print("./raw/droplists_beast.json")
    print("./raw/itemcategories_beast.json")
    print("./raw/itemlist_beast.json")
    print("./raw/monsterlist_beast.json")
    print("./raw/monsterlist_trainer.json")
    print("./values/loadresources.xml")
    print("===================================================")

if __name__ == "__main__":
    main()
