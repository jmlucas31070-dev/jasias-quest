#!/usr/bin/env python3

import json
import os
import random

from at_format import make_capture_conversation_set, write_json

# ============================================================
# ASTRAL BEAST RESOURCE GENERATOR
# ============================================================

OUTPUT_RAW = "./raw"
OUTPUT_VALUES = "./values"
OUTPUT_CONVERSATIONS = "./raw"
OUTPUT_BREEDING = "./raw"
OUTPUT_SHOPS = "./raw"
OUTPUT_QUESTS = "./raw"

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
    "Lumia", "Kranix", "Ignora", "Hesperia", "Lucidiah", "Illystrius", "Sejor", "Bellom", "Dorado"
]

BEASTS_PER_REGION = 90
LEGENDARY_BEASTS_PER_REGION = 3
MYTHICAL_BEASTS_PER_REGION = 2

# ============================================================
# BEAST_ITEM SLOT ROTATION
# ============================================================

BEAST_ITEM_SLOTS = [
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
# BEAST_ITEM CATEGORIES
# ============================================================

BEAST_ITEM_CATEGORIES = [
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

SPIRIT_ORB_ITEMS = [
    {
        "id": "spirit_orb_basic",
        "name": "Basic Spirit Orb",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 100,
        "category": "beast_ring",
        "description": "A weak orb used to capture beasts."
    },
    {
        "id": "spirit_orb_greater",
        "name": "Greater Spirit Orb",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 500,
        "category": "beast_ring",
        "description": "A stronger orb with improved capture power."
    },
    {
        "id": "spirit_orb_astral",
        "name": "Astral Spirit Orb",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 2500,
        "category": "beast_ring",
        "description": "An advanced orb capable of containing legendary beasts."
    }
]

HEAL_POTION_ITEMS = [
    {
        "id": "heal_potion_small",
        "name": "Small Heal Potion",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 50,
        "category": "beast_ring",
        "description": "Restores a small amount of health."
    },
    {
        "id": "heal_potion_medium",
        "name": "Medium Heal Potion",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 200,
        "category": "beast_ring",
        "description": "Restores moderate health."
    },
    {
        "id": "heal_potion_large",
        "name": "Large Heal Potion",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 750,
        "category": "beast_ring",
        "description": "Restores a massive amount of health."
    }
]

REGION_BADGE_ITEMS = []
REGION_RIBBON_ITEMS = []

for region in REGIONS:

    REGION_BADGE_ITEMS.append({
        "id": f"{region.lower()}_gym_badge",
        "name": f"{region} Gym Badge",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 5000,
        "category": "beast_ring",
        "description": f"A badge earned by defeating {region} gym leaders."
    })

    REGION_RIBBON_ITEMS.append({
        "id": f"{region.lower()}_grandmaster_ribbon",
        "name": f"{region} Grandmaster Ribbon",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 25000,
        "category": "beast_ring",
        "description": f"A ribbon awarded for defeating the {region} Grandmaster."
    })

PROFESSOR_REWARD_ITEMS = [
    {
        "id": "professor_master_orb",
        "name": "Professor Master Orb",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 500000,
        "category": "beast_weapon",
        "description": "A legendary orb awarded for catching every beast."
    }
]

REGION_COMPLETION_REWARDS = []

for region in REGIONS:

    REGION_COMPLETION_REWARDS.append({
        "id": f"{region.lower()}_completion_medal",
        "name": f"{region} Completion Medal",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": 25000,
        "category": "beast_ring",
        "description": (
            f"Awarded for catching every beast "
            f"in the {region} region."
        )
    })

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

LEGENDARY_PREFIXES = [
    "Eternal", "Primordial", "Divine", "Astral", "Ancient"
]

LEGENDARY_CREATURES = [
    "Titan", "Leviathan", "Celestigon", "Voidwyrm", "Star Phoenix"
]

MYTHICAL_PREFIXES = [
    "Dream", "Arc", "Cosmic", "Mystic", "Fable"
]

MYTHICAL_CREATURES = [
    "Kitsune", "Seraph", "Moon Drake", "Spirit Wolf", "Oracle Owl"
]

BREEDER_PREFIXES = [
    "Fusion",
    "Hybrid",
    "Twilight",
    "Nova",
    "Eclipse",
    "Primal",
    "Rune",
    "Mythic",
    "Chaos"
]

BREEDER_SUFFIXES = [
    "Drake",
    "Wolf",
    "Phoenix",
    "Titan",
    "Serpent",
    "Wyvern",
    "Hydra",
    "Golem",
    "Leviathan"
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

REGION_MENTAL_CONDITIONS = []

for region in REGIONS:

    REGION_MENTAL_CONDITIONS.append({
        "id": f"beast_region_{region.lower()}",
        "name": f"{region} Beast Mastery",
        "category": "mental",

        "iconID": ACTORCONDITION_ICON,

        "effects": {
            "increaseAttackChance": 10,
            "increaseCriticalSkill": 10,
            "increaseMovePoints": 1
        },

        "description": (
            f"Mental synchronization with "
            f"the beasts of the {region} region."
        )
    })

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

BEAST_ACTORCONDITIONS = []

for i, move_name in enumerate(MOVE_NAMES):
    BEAST_ACTORCONDITIONS.append({
        "id": f"beast_condition_{i+1}",
        "name": move_name,
        "iconID": ACTORCONDITION_ICON,
        "isNegative": 0,
        "abilityEffect": generate_effect(i)
    })

# ============================================================
# TRAINERS
# ============================================================

def get_region_beasts(beast_monsters, region):

    normal = []
    legendary = []
    mythical = []

    region_prefix = f"beast_{region.lower()}"

    for beast in beast_monsters:

        beast_id = beast["id"]

        if not beast_id.startswith(region_prefix):
            continue

        if "legendary" in beast_id:
            legendary.append(beast_id)

        elif "mythical" in beast_id:
            mythical.append(beast_id)

        else:
            normal.append(beast_id)

    return normal, legendary, mythical

def create_region_trainers(beast_monsters):
    trainers = []
    trainer_droplists = []
    for region in REGIONS:
        (
            region_normal_beasts,
            region_legendary_beasts,
            region_mythical_beasts
        ) = get_region_beasts(beast_monsters, region)
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
            random_legendary = random.choice(
                region_legendary_beasts
            )

            leader["droplistID"] = (
                f"droplist_{leader['id']}"
            )
            trainers.append(leader)

            trainer_droplists.append({
                "id": f"droplist_{leader['id']}",
                "items": [
                    {
                        "item": f"{region.lower()}_gym_badge",
                        "quantity": {
                            "min": 1,
                            "max": 1
                        },
                        "chance": "100"
                    },
                    {
                        "item": f"item_{random_legendary}",
                        "quantity": {
                            "min": 1,
                            "max": 1
                        },
                        "chance": "100"
                    }
                ]
            })
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
                random_beast = random.choice(region_normal_beasts)

                trainer["droplistID"] = (
                    f"droplist_{trainer['id']}"
                )
                trainers.append(trainer)

                trainer_droplists.append({
                    "id": f"droplist_{trainer['id']}",
                    "items": [
                        {
                            "item": f"item_{random_beast}",
                            "quantity": {
                                "min": 1,
                                "max": 1
                            },
                            "chance": "100"
                        }
                    ]
                })
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
        random_mythical = random.choice(
            region_mythical_beasts
        )

        grandmaster["droplistID"] = (
            f"droplist_{grandmaster['id']}"
        )
        trainers.append(grandmaster)

        trainer_droplists.append({
            "id": f"droplist_{grandmaster['id']}",
            "items": [
                {
                    "item": f"{region.lower()}_grandmaster_ribbon",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                },
                {
                    "item": f"item_{random_mythical}",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                }
            ]
        })
    return trainers, trainer_droplists

# ============================================================
# CREATE BEASTS / ITEMS / TRAINERS / DROPLISTS
# ============================================================

def create_special_beast(
    region,
    rarity,
    index,
    condition
):

    if rarity == "legendary":
        prefix = random.choice(LEGENDARY_PREFIXES)
        creature = random.choice(LEGENDARY_CREATURES)

        max_hp = random.randint(900, 1400)
        min_damage = random.randint(55, 90)
        max_damage = min_damage + random.randint(40, 90)

    else:
        prefix = random.choice(MYTHICAL_PREFIXES)
        creature = random.choice(MYTHICAL_CREATURES)

        max_hp = random.randint(700, 1100)
        min_damage = random.randint(45, 75)
        max_damage = min_damage + random.randint(35, 70)

    beast_name = f"{prefix} {creature}"
    full_name = f"{beast_name} of the {region} region"

    beast_id = f"beast_{region.lower()}_{rarity}_{index}"
    item_id = f"item_{beast_id}"

    droplist_id = f"droplist_{beast_id}"

    droplist = {
        "id": droplist_id,
        "items": [
            {
                "item": "gold",
                "quantity": {
                    "min": int(max_hp / 5),
                    "max": int(max_hp / 4)
                },
                "chance": "100"
            }
        ]
    }

    monster = {
        "id": beast_id,
        "name": full_name,
        "iconID": MONSTER_ICON,
        "maxHP": max_hp,
        "attackChance": 95,
        "attackDamage": {
            "min": min_damage,
            "max": max_damage
        },
        "moveCost": 3,
        "attackCost": 3,
        "droplistID": droplist_id,
        "conversation": f"conversation_{beast_id}",
        "spawnGroup": f"beast_{region.lower()}_{rarity}",
        "faction": "beast",
        "rarity": rarity,
        "hitEffect": {
            "conditionsSource": [
                {
                    "condition": condition["id"],
                    "chance": 100,
                    "magnitude": 2
                }
            ]
        }
    }

    item = {
        "id": item_id,
        "name": full_name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": max_hp * 50,
        "category": "beast_ring",
        "description": f"A {rarity} beast from the {region} region.",
        "equipEffect": {
            "increaseAttackDamage": {
                "min": random.randint(30, 70),
                "max": random.randint(70, 150)
            },
            "increaseAttackChance": random.randint(15, 40),
            "increaseCriticalSkill": random.randint(10, 25)
        }
    }

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

    trainer_monster = {
        "id": trainer_id,
        "name": f"{beast_name} Master",
        "iconID": MONSTER_ICON,
        "maxHP": max_hp + 250,
        "attackChance": 95,
        "attackDamage": {
            "min": min_damage + 15,
            "max": max_damage + 25
        },
        "moveCost": 2,
        "attackCost": 2,
        "droplistID": trainer_droplist_id,
        "spawnGroup": f"trainer_{rarity}_{region.lower()}",
        "faction": "trainer"
    }

    return (
        monster,
        item,
        droplist,
        trainer_monster,
        trainer_droplist
    )


def create_beasts():
    beast_monsters = []
    beast_items = []
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
            condition = random.choice(BEAST_ACTORCONDITIONS)
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
                "conversation": f"conversation_{beast_id}",
                "spawnGroup": f"beast_{region.lower()}",
                "faction": "beast",
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
            beast_monsters.append(monster)
            # ====================================================
            # ITEM
            # ====================================================
            category, icon_prefix = BEAST_ITEM_SLOTS[
                slot_index % len(BEAST_ITEM_SLOTS)
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
            beast_items.append(item)
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
                "spawnGroup": f"trainer_{beast_name.lower()}",
                "faction": "trainer",
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
        # ====================================================
        # LEGENDARY BEASTS
        # ====================================================

        for legendary_index in range(1, LEGENDARY_BEASTS_PER_REGION + 1):

            condition = random.choice(BEAST_ACTORCONDITIONS)

            (
                monster,
                item,
                droplist,
                trainer_monster,
                trainer_droplist
            ) = create_special_beast(
                region,
                "legendary",
                legendary_index,
                condition
            )

            beast_monsters.append(monster)
            beast_items.append(item)
            beast_droplists.append(droplist)
            trainer_monsters.append(trainer_monster)
            trainer_droplists.append(trainer_droplist)

        # ====================================================
        # MYTHICAL BEASTS
        # ====================================================

        for mythical_index in range(1, MYTHICAL_BEASTS_PER_REGION + 1):

            condition = random.choice(BEAST_ACTORCONDITIONS)

            (
                monster,
                item,
                droplist,
                trainer_monster,
                trainer_droplist
            ) = create_special_beast(
                region,
                "mythical",
                mythical_index,
                condition
            )

            beast_monsters.append(monster)
            beast_items.append(item)
            beast_droplists.append(droplist)
            trainer_monsters.append(trainer_monster)
            trainer_droplists.append(trainer_droplist)

    return (
        beast_monsters,
        beast_items,
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
        <item>@raw/actorconditions_regions</item>
    </array>

    <array name="loadresource_conversationlists">
        <item>@raw/conversationlist_beast</item>
        <item>@raw/conversationlist_bellom</item>
        <item>@raw/conversationlist_breeding_bellom</item>
        <item>@raw/conversationlist_breeding_dorado</item>
        <item>@raw/conversationlist_breeding_hesperia</item>
        <item>@raw/conversationlist_breeding_ignora</item>
        <item>@raw/conversationlist_breeding_illystrius</item>
        <item>@raw/conversationlist_breeding_kranix</item>
        <item>@raw/conversationlist_breeding_lucidiah</item>
        <item>@raw/conversationlist_breeding_lumia</item>
        <item>@raw/conversationlist_breeding_sejor</item>
        <item>@raw/conversationlist_dorado</item>
        <item>@raw/conversationlist_hesperia</item>
        <item>@raw/conversationlist_ignora</item>
        <item>@raw/conversationlist_illystrius</item>
        <item>@raw/conversationlist_kranix</item>
        <item>@raw/conversationlist_lucidiah</item>
        <item>@raw/conversationlist_lumia</item>
        <item>@raw/conversationlist_professor.json</item>
        <item>@raw/conversationlist_sejor.json</item>
        <item>@raw/conversationlist_shop.json</item>
        <item>@raw/conversationlist_region.json</item>
    </array>

    <array name="loadresource_droplists">
        <item>@raw/droplists_beast</item>
        <item>@raw/droplists_beast_shops</item>
    </array>

    <array name="loadresource_itemcategories">
        <item>@raw/itemcategories_beast</item>
    </array>

    <array name="loadresource_items">
        <item>@raw/itemlist_beast</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_beast</item>
        <item>@raw/monsterlist_beast_npc</item>
        <item>@raw/monsterlist_trainer</item>
    </array>

    <array name="loadresource_quests">
        <item>@raw/questlist_professor</item>
        <item>@raw/questlist_region</item>
    </array>

</resources>
"""

# ============================================================
# WRITE JSON
# ============================================================

def build_beast_lookup(beast_monsters):

    lookup = {}

    for beast in beast_monsters:

        short_name = beast["name"].split(" from ")[0]

        lookup[beast["id"]] = {
            "name": short_name,
            "monster": beast
        }

    return lookup

def create_evolution_conversations(beast_monsters):
    # ========================================================
    # BUILD LOOKUP TABLE
    # ========================================================

    beast_lookup = {}

    for beast in beast_monsters:

        # Removes " from Lumia region"
        short_name = beast["name"].split(" from ")[0]

        beast_lookup[beast["id"]] = short_name

    region_conversations = {}

    for region in REGIONS:

        conversations = []

        scholar_id = f"{region.lower()}_evolution_scholar"

        intro_conversation = {
            "id": f"conversation_{scholar_id}_intro",
            "text": (
                f"I am the Evolution Scholar of {region}. "
                f"Bring me beast relics and I shall evolve them."
            ),
            "replies": [
                {
                    "text": "Show me evolution options.",
                    "nextPhraseID": f"conversation_{scholar_id}_options"
                },
                {
                    "text": "Goodbye.",
                    "nextPhraseID": "X"
                }
            ]
        }

        conversations.append(intro_conversation)

        options = {
            "id": f"conversation_{scholar_id}_options",
            "text": "Choose a beast evolution.",
            "replies": []
        }

        # ====================================================
        # EVOLUTION CHAINS
        # ====================================================

        for chain_start in range(1, 91, 3):

            beast_1 = chain_start
            beast_2 = chain_start + 1
            beast_3 = chain_start + 2

            beast1_id = f"item_beast_{region.lower()}_{beast_1}"
            beast2_id = f"item_beast_{region.lower()}_{beast_2}"
            beast3_id = f"item_beast_{region.lower()}_{beast_3}"

            beast1_name = beast_lookup[f"beast_{region.lower()}_{beast_1}"]
            beast2_name = beast_lookup[f"beast_{region.lower()}_{beast_2}"]
            beast3_name = beast_lookup[f"beast_{region.lower()}_{beast_3}"]

            evolve_1_id = (
                f"conversation_{region.lower()}_evolve_"
                f"{beast_1}_to_{beast_2}"
            )

            evolve_2_id = (
                f"conversation_{region.lower()}_evolve_"
                f"{beast_2}_to_{beast_3}"
            )

            # ================================================
            # OPTIONS MENU
            # ================================================

            options["replies"].append({
                "text": (
                    f"Evolve {beast1_name} into {beast2_name}"
                ),
                "nextPhraseID": evolve_1_id
            })

            options["replies"].append({
                "text": (
                    f"Evolve {beast2_name} into {beast3_name}"
                ),
                "nextPhraseID": evolve_2_id
            })

            # ================================================
            # EVOLUTION 1 -> 2
            # ================================================

            evolve_1 = {
                "id": evolve_1_id,
                "text": (
                    f"I can evolve {beast1_name} into "
                    f"{beast2_name}."
                ),
                "requirements": [
                    {
                        "item": beast1_id,
                        "quantity": 1
                    }
                ],
                "actions": [
                    {
                        "removeItem": beast1_id,
                        "quantity": 1
                    },
                    {
                        "giveItem": beast2_id,
                        "quantity": 1
                    },
                    {
                        "completeQuestObjectives": [beast2_id]
                    }
                ],
                "replies": [
                    {
                        "text": "Evolve my beast.",
                        "nextPhraseID": "X"
                    },
                    {
                        "text": "Maybe later.",
                        "nextPhraseID": "X"
                    }
                ]
            }

            conversations.append(evolve_1)

            # ================================================
            # EVOLUTION 2 -> 3
            # ================================================

            evolve_2 = {
                "id": evolve_2_id,
                "text": (
                    f"I can evolve {beast2_name} into "
                    f"{beast3_name}."
                ),
                "requirements": [
                    {
                        "item": beast2_id,
                        "quantity": 1
                    }
                ],
                "actions": [
                    {
                        "removeItem": beast2_id,
                        "quantity": 1
                    },
                    {
                        "giveItem": beast3_id,
                        "quantity": 1
                    },
                    {
                        "completeQuestObjectives": [beast3_id]
                    }
                ],
                "replies": [
                    {
                        "text": "Evolve my beast.",
                        "nextPhraseID": "X"
                    },
                    {
                        "text": "Maybe later.",
                        "nextPhraseID": "X"
                    }
                ]
            }

            conversations.append(evolve_2)

        conversations.append(options)

        region_conversations[region] = {
            "scholar_id": scholar_id,
            "conversations": conversations
        }

    return region_conversations

def create_evolution_scholars():

    scholars = []

    for region in REGIONS:

        scholars.append({
            "id": f"{region.lower()}_evolution_scholar",
            "name": f"{region} Evolution Scholar",
            "iconID": MONSTER_ICON,
            "maxHP": 500,
            "attackChance": 0,
            "attackDamage": {
                "min": 0,
                "max": 0
            },
            "faction": "neutral",
            "conversation": (
                f"conversation_{region.lower()}_evolution_scholar_intro"
            )
        })

    return scholars

def create_breeding_system(beast_monsters):

    lookup = build_beast_lookup(beast_monsters)

    breeding_items = []
    breeding_monsters = []
    breeding_droplists = []
    breeding_conversations = {}
    breeder_npcs = []

    # ====================================================
    # REGION BREEDERS
    # ====================================================

    for region in REGIONS:

        breeder_id = f"{region.lower()}_breeder"

        breeder_npcs.append({
            "id": breeder_id,
            "name": f"{region} Beast Breeder",
            "iconID": MONSTER_ICON,
            "maxHP": 500,
            "attackChance": 0,
            "attackDamage": {
                "min": 0,
                "max": 0
            },
            "faction": "neutral",
            "conversation": f"conversation_{breeder_id}_intro"
        })

        conversations = []

        intro = {
            "id": f"conversation_{breeder_id}_intro",
            "text": (
                f"Welcome to the {region} breeding sanctuary. "
                f"I can fuse beasts into stronger hybrid forms."
            ),
            "replies": [
                {
                    "text": "Show breeding combinations.",
                    "nextPhraseID": f"conversation_{breeder_id}_menu"
                },
                {
                    "text": "Goodbye.",
                    "nextPhraseID": "X"
                }
            ]
        }

        conversations.append(intro)

        menu = {
            "id": f"conversation_{breeder_id}_menu",
            "text": "Choose a breeding fusion.",
            "replies": []
        }

        # ====================================================
        # SAME REGION BREEDING
        # ====================================================

        combinations = [
            (1, 2),
            (1, 3),
            (2, 3)
        ]

        hybrid_index = 1

        for level_a, level_b in combinations:

            for hybrid_number in range(1, 10):

                beast_a_index = ((hybrid_number - 1) * 3) + level_a
                beast_b_index = ((hybrid_number - 1) * 3) + level_b

                beast_a_id = f"beast_{region.lower()}_{beast_a_index}"
                beast_b_id = f"beast_{region.lower()}_{beast_b_index}"

                beast_a_name = lookup[beast_a_id]["name"]
                beast_b_name = lookup[beast_b_id]["name"]

                hybrid_name = (
                    f"{random.choice(BREEDER_PREFIXES)} "
                    f"{random.choice(BREEDER_SUFFIXES)}"
                )

                hybrid_monster_id = (
                    f"hybrid_{region.lower()}_{level_a}_{level_b}_"
                    f"{hybrid_number}"
                )

                hybrid_item_id = f"item_{hybrid_monster_id}"

                droplist_id = f"droplist_{hybrid_monster_id}"

                droplist = {
                    "id": droplist_id,
                    "items": [
                        {
                            "item": "gold",
                            "quantity": {
                                "min": 100,
                                "max": 300
                            },
                            "chance": "100"
                        }
                    ]
                }

                breeding_droplists.append(droplist)

                hybrid_monster = {
                    "id": hybrid_monster_id,
                    "name": hybrid_name,
                    "iconID": MONSTER_ICON,
                    "maxHP": random.randint(500, 1200),
                    "attackChance": random.randint(75, 95),
                    "attackDamage": {
                        "min": random.randint(35, 70),
                        "max": random.randint(80, 150)
                    },
                    "moveCost": 3,
                    "attackCost": 3,
                    "droplistID": droplist_id,
                    "conversation": f"conversation_{hybrid_monster_id}",
                    "spawnGroup": f"hybrid_{region.lower()}",
                    "faction": "beast"
                }

                breeding_monsters.append(hybrid_monster)

                parent_a = lookup[beast_a_id]["monster"]
                parent_b = lookup[beast_b_id]["monster"]

                condition_a = (
                    parent_a["hitEffect"]
                    ["conditionsSource"][0]
                    ["condition"]
                )

                condition_b = (
                    parent_b["hitEffect"]
                    ["conditionsSource"][0]
                    ["condition"]
                )

                hybrid_item = {
                    "id": hybrid_item_id,
                    "name": hybrid_name,
                    "iconID": ITEM_ICON,
                    "displaytype": "ordinary",
                    "hasManualPrice": 1,
                    "baseMarketCost": 50000,
                    "category": "beast_weapon",
                    "description": (
                        f"A fusion weapon forged from "
                        f"{beast_a_name} and {beast_b_name}."
                    ),

                    # ====================================================
                    # BOTH PARENT CONDITIONS
                    # ====================================================

                    "hitEffect": {
                        "conditionsSource": [
                            {
                                "condition": condition_a,
                                "magnitude": 1,
                                "duration": 999,
                                "chance": 100
                            },
                            {
                                "condition": condition_b,
                                "magnitude": 1,
                                "duration": 999,
                                "chance": 100
                            }
                        ]
                    },

                    # ====================================================
                    # STRONGER HYBRID STATS
                    # ====================================================

                    "equipEffect": {
                        "increaseAttackDamage": {
                            "min": random.randint(40, 90),
                            "max": random.randint(100, 220)
                        },
                        "increaseAttackChance": random.randint(15, 35),
                        "increaseCriticalSkill": random.randint(10, 30)
                    }
                }

                breeding_items.append(hybrid_item)

                conversation_id = (
                    f"conversation_breed_{region.lower()}_"
                    f"{hybrid_index}"
                )

                menu["replies"].append({
                    "text": (
                        f"Breed {beast_a_name} with {beast_b_name}"
                    ),
                    "nextPhraseID": conversation_id
                })

                conversations.append({
                    "id": conversation_id,
                    "text": (
                        f"I can breed {beast_a_name} and "
                        f"{beast_b_name} into {hybrid_name}."
                    ),
                    "requirements": [
                        {
                            "item": f"item_{beast_a_id}",
                            "quantity": 1
                        },
                        {
                            "item": f"item_{beast_b_id}",
                            "quantity": 1
                        }
                    ],
                    "actions": [
                        {
                            "removeItem": f"item_{beast_a_id}",
                            "quantity": 1
                        },
                        {
                            "removeItem": f"item_{beast_b_id}",
                            "quantity": 1
                        },
                        {
                            "giveItem": hybrid_item_id,
                            "quantity": 1
                        }
                    ],
                    "replies": [
                        {
                            "text": "Begin breeding.",
                            "nextPhraseID": "X"
                        },
                        {
                            "text": "Cancel.",
                            "nextPhraseID": "X"
                        }
                    ]
                })

                hybrid_index += 1

        conversations.append(menu)

        breeding_conversations[region] = conversations

    # ====================================================
    # CROSS REGION BREEDING
    # ====================================================

    for region_a in REGIONS:

        for region_b in REGIONS:

            if region_a == region_b:
                continue

            combinations = [
                (1, 2),
                (1, 3),
                (2, 3)
            ]

            for level_a, level_b in combinations:

                for hybrid_number in range(1, 10):

                    beast_a_index = ((hybrid_number - 1) * 3) + level_a
                    beast_b_index = ((hybrid_number - 1) * 3) + level_b

                    beast_a_id = (
                        f"beast_{region_a.lower()}_{beast_a_index}"
                    )

                    beast_b_id = (
                        f"beast_{region_b.lower()}_{beast_b_index}"
                    )

                    if beast_a_id not in lookup:
                        continue

                    if beast_b_id not in lookup:
                        continue

                    beast_a_name = lookup[beast_a_id]["name"]
                    beast_b_name = lookup[beast_b_id]["name"]

                    hybrid_name = (
                        f"{region_a[:3]}-{region_b[:3]} "
                        f"{random.choice(BREEDER_SUFFIXES)}"
                    )

                    hybrid_monster_id = (
                        f"cross_hybrid_"
                        f"{region_a.lower()}_"
                        f"{region_b.lower()}_"
                        f"{level_a}_{level_b}_"
                        f"{hybrid_number}"
                    )

                    hybrid_item_id = f"item_{hybrid_monster_id}"

                    breeding_monsters.append({
                        "id": hybrid_monster_id,
                        "name": hybrid_name,
                        "iconID": MONSTER_ICON,
                        "maxHP": random.randint(700, 1500),
                        "attackChance": random.randint(80, 98),
                        "attackDamage": {
                            "min": random.randint(50, 100),
                            "max": random.randint(120, 220)
                        },
                        "moveCost": 2,
                        "attackCost": 2,
                        "conversation": f"conversation_{hybrid_monster_id}",
                        "spawnGroup": (
                            f"cross_hybrid_"
                            f"{region_a.lower()}_"
                            f"{region_b.lower()}"
                        ),
                        "faction": "beast"
                    })

                    parent_a = lookup[beast_a_id]["monster"]
                    parent_b = lookup[beast_b_id]["monster"]

                    condition_a = (
                        parent_a["hitEffect"]
                        ["conditionsSource"][0]
                        ["condition"]
                    )

                    condition_b = (
                        parent_b["hitEffect"]
                        ["conditionsSource"][0]
                        ["condition"]
                    )

                    breeding_items.append({
                        "id": hybrid_item_id,
                        "name": hybrid_name,
                        "iconID": ITEM_ICON,
                        "displaytype": "ordinary",
                        "hasManualPrice": 1,
                        "baseMarketCost": 100000,
                        "category": "beast_weapon",
                        "description": (
                            f"A forbidden hybrid forged from "
                            f"{beast_a_name} and {beast_b_name}."
                        ),

                        "hitEffect": {
                            "conditionsSource": [
                                {
                                    "condition": condition_a,
                                    "magnitude": 1,
                                    "duration": 999,
                                    "chance": 100
                                },
                                {
                                    "condition": condition_b,
                                    "magnitude": 1,
                                    "duration": 999,
                                    "chance": 100
                                }
                            ]
                        },

                        "equipEffect": {
                            "increaseAttackDamage": {
                                "min": random.randint(60, 120),
                                "max": random.randint(140, 300)
                            },
                            "increaseAttackChance": random.randint(20, 40),
                            "increaseCriticalSkill": random.randint(15, 35)
                        }
                    })

    return (
        breeding_monsters,
        breeding_items,
        breeding_droplists,
        breeding_conversations,
        breeder_npcs
    )

def create_region_shopkeepers():

    shopkeepers = []
    shops = []
    convo = []

    for region in REGIONS:

        shop_id = f"shop_{region.lower()}"

        shopkeepers.append({
            "id": f"{region.lower()}_shopkeeper",
            "name": f"{region} Spirit Merchant",
            "iconID": MONSTER_ICON,
            "maxHP": 500,
            "attackChance": 0,
            "attackDamage": {
                "min": 0,
                "max": 0
            },
            "conversation": f"conversation_{region.lower()}_shopkeeper",
            "droplistID": f"shop_{region.lower()}",
            "faction": "neutral",
        })

        shops.append({
            "id": shop_id,
            "name": f"{region} Spirit Shop",
            "items": [
                {
                    "item": "spirit_orb_basic",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                },
                {
                    "item": "spirit_orb_greater",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                },
                {
                    "item": "spirit_orb_astral",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                },
                {
                    "item": "heal_potion_small",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                },
                {
                    "item": "heal_potion_medium",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                },
                {
                    "item": "heal_potion_large",
                    "quantity": {
                        "min": 1,
                        "max": 1
                    },
                    "chance": "100"
                }
            ]
        })

        convo.append([
            {
                "ID": f"conversation_{region.lower()}_shopkeeper",
                "text": f"Welcome to the {region} Spirit Shop.",
                "replies": [
                    {
                        "text": "Show me your wares.",
                        "nextPhraseID": "S"
                    },
                    {
                        "text": "Leave.",
                        "nextPhraseID": "X"
                    }
                ]
            }
        ])

    return shopkeepers, shops, convo

def get_capture_rate(beast_id):

    if "legendary" in beast_id:
        return 50

    if "mythical" in beast_id:
        return 50

    if "hybrid" in beast_id:
        return 50

    try:
        number = int(beast_id.split("_")[-1])
    except:
        return 50

    level_position = ((number - 1) % 3) + 1

    if level_position == 1:
        return 80

    if level_position == 2:
        return 72

    return 65


def create_capture_conversations(beast_monsters):

    conversationlists = {}

    for beast in beast_monsters:

        beast_id = beast["id"]
        beast_name = beast["name"].split(" from ")[0]

        item_id = f"item_{beast_id}"

        capture_rate = get_capture_rate(beast_id)

        conversationlists[beast_id] = make_capture_conversation_set(
            beast_id, beast_name, item_id, capture_rate
        )

    return conversationlists

def get_non_hybrid_beasts(beast_monsters):

    valid = []

    for beast in beast_monsters:

        beast_id = beast["id"]

        if "hybrid" in beast_id:
            continue

        valid.append(beast_id)

    return valid


def get_region_non_hybrid_beasts(beast_monsters, region):

    region_beasts = []

    for beast in beast_monsters:

        beast_id = beast["id"]

        if "hybrid" in beast_id:
            continue

        if beast_id.startswith(f"beast_{region.lower()}"):
            region_beasts.append(beast_id)

    return region_beasts

def create_professor_system(beast_monsters):

    professor = {
        "id": "beast_professor",
        "name": "Professor Astralis",
        "iconID": MONSTER_ICON,
        "maxHP": 1000,
        "attackChance": 0,
        "attackDamage": {
            "min": 0,
            "max": 0
        },
        "faction": "neutral",
        "conversation": "conversation_professor_intro"
    }

    all_required = get_non_hybrid_beasts(beast_monsters)

    conversations = []

    # ====================================================
    # INTRO
    # ====================================================

    conversations.append({
        "ID": "conversation_professor_intro",
        "text": (
            "Welcome, Beast Keeper. "
            "Your mission is to catch every beast "
            "across all regions."
        ),
        "replies": [
            {
                "text": "I will catch every beast.",
                "nextPhraseID": "conversation_professor_regions",
                "startQuest": "quest_catch_them_all"
            },
            {
                "text": "I will return later.",
                "nextPhraseID": "X"
            }
        ]
    })

    # ====================================================
    # REGION CHECKS
    # ====================================================

    conversations.append({
        "ID": "conversation_professor_regions",
        "text": (
            "Complete every region collection "
            "to earn medals and rare rewards."
        ),
        "replies": []
    })

    for region in REGIONS:

        region_beasts = get_region_non_hybrid_beasts(
            beast_monsters,
            region
        )

        check_id = (
            f"conversation_professor_complete_"
            f"{region.lower()}"
        )

        conversations[1]["replies"].append({
            "text": f"Complete {region} Region",
            "nextPhraseID": check_id
        })

        conversations.append({
            "ID": check_id,
            "text": (
                f"You present your completed "
                f"{region} beast collection."
            ),
            "replies": [
                {
                    "text": "Claim regional reward.",
                    "nextPhraseID": "X",

                    "requiresQuestProgress": region_beasts,

                    "rewardItems": [
                        {
                            "itemID": (
                                f"{region.lower()}_completion_medal"
                            ),
                            "quantity": 1
                        }
                    ]
                }
            ]
        })

    # ====================================================
    # FINAL COMPLETION
    # ====================================================

    conversations[1]["replies"].append({
        "text": "Complete the entire collection",
        "nextPhraseID": "conversation_professor_final"
    })

    conversations.append({
        "ID": "conversation_professor_final",
        "text": (
            "You have completed the greatest "
            "beast collection ever assembled."
        ),
        "replies": [
            {
                "text": "Claim final reward.",
                "nextPhraseID": "X",

                "requiresQuestProgress": all_required,

                "rewardItems": [
                    {
                        "itemID": "professor_master_orb",
                        "quantity": 1
                    }
                ]
            }
        ]
    })

    return professor, conversations
def create_professor_quest(beast_monsters):

    all_required = []

    regional_objectives = {}

    for region in REGIONS:

        regional_objectives[region] = []

    for beast in beast_monsters:

        beast_id = beast["id"]

        # ====================================================
        # EXCLUDE HYBRIDS
        # ====================================================

        if "hybrid" in beast_id:
            continue

        all_required.append(beast_id)

        for region in REGIONS:

            if beast_id.startswith(f"beast_{region.lower()}"):

                regional_objectives[region].append(beast_id)

    # ========================================================
    # QUEST OBJECTIVES
    # ========================================================

    objectives = []

    for beast_id in all_required:

        objectives.append({
            "id": beast_id,
            "name": f"Catch {beast_id}",
            "isCompleted": 0
        })

    # ========================================================
    # QUEST
    # ========================================================

    quest = {
        "id": "quest_catch_them_all",
        "name": "Catch Them All",
        "description": (
            "Professor Astralis has tasked you with "
            "catching every beast in every region."
        ),

        "objectives": objectives,

        "rewards": [
            {
                "itemID": "professor_master_orb",
                "quantity": 1
            }
        ]
    }

    return quest

def create_region_leader_system():

    leader_npcs = []
    leader_conversations = []
    leader_quests = []

    for region in REGIONS:

        # ====================================================
        # IDS
        # ====================================================

        quest_id = (
            f"quest_{region.lower()}_league"
        )

        npc_id = (
            f"{region.lower()}_league_master"
        )

        conversation_intro = (
            f"conversation_{region.lower()}_league_intro"
        )

        conversation_complete = (
            f"conversation_{region.lower()}_league_complete"
        )

        # ====================================================
        # QUEST
        # ====================================================


        quest = {
            "id": quest_id,

            "name": (
                f"{region} Regional League"
            ),

            "description": (
                f"Defeat all 9 gym leaders and "
                f"the champion of {region}."
            ),

            "objectives": [
                {
                    "id": f"{region.lower()}_league_progress",
                    "name": (
                        f"Complete the {region} League"
                    ),
                    "isCompleted": 0
                }
            ],

            "rewards": [
                {
                    "itemID": (
                        f"{region.lower()}_grandmaster_ribbon"
                    ),
                    "quantity": 1
                }
            ]
        }
        leader_quests.append(quest)

        # ====================================================
        # NPC
        # ====================================================

        leader_npcs.append({
            "id": npc_id,
            "name": (
                f"{region} League Master"
            ),
            "iconID": MONSTER_ICON,
            "maxHP": 1000,
            "attackChance": 0,
            "attackDamage": {
                "min": 0,
                "max": 0
            },
            "faction": "neutral",
            "conversation": conversation_intro
        })

        # ====================================================
        # INTRO CONVERSATION
        # ====================================================

        leader_conversations.append({
            "ID": conversation_intro,

            "text": (
                f"Welcome challenger. "
                f"Collect all 9 gym badges "
                f"and defeat the {region} Grandmaster."
            ),

            "replies": [
                {
                    "text": (
                        "I will conquer the league."
                    ),

                    "nextPhraseID": (
                        f"{region.lower()}_league_check"
                    ),

                    "startQuest": quest_id
                },

                {
                    "text": "Maybe later.",
                    "nextPhraseID": "X"
                }
            ]
        })

        leader_conversations.append({
            "ID": f"{region.lower()}_league_check",

            "text": (
                f"Show me proof of your victories."
            ),

            "replies": [
                {
                    "text": (
                        "Present all gym badges and "
                        "grandmaster ribbon."
                    ),

                    "nextPhraseID": (
                        f"{region.lower()}_league_complete"
                    ),

                    "requiresItems": [
                        {
                            "itemID": (
                                f"{region.lower()}_gym_badge"
                            ),
                            "quantity": 9
                        },
                        {
                            "itemID": (
                                f"{region.lower()}_grandmaster_ribbon"
                            ),
                            "quantity": 1
                        }
                    ]
                },

                {
                    "text": "I am still working on it.",
                    "nextPhraseID": "X"
                }
            ]
        })

        # ====================================================
        # COMPLETION CONVERSATION
        # ====================================================

        leader_conversations.append({
            "ID": conversation_complete,

            "text": (
                f"You have conquered the "
                f"{region} League."
            ),

            "replies": [
                {
                    "text": (
                        "Claim regional mastery."
                    ),

                    "nextPhraseID": "X",

                    "consumeItems": [
                        {
                            "itemID": (
                                f"{region.lower()}_gym_badge"
                            ),
                            "quantity": 9
                        },
                        {
                            "itemID": (
                                f"{region.lower()}_grandmaster_ribbon"
                            ),
                            "quantity": 1
                        }
                    ],

                    "rewardConditions": [
                        {
                            "conditionID": (
                                f"beast_region_{region.lower()}"
                            ),
                            "magnitude": 1,
                            "duration": -1
                        }
                    ],

                    "completeQuestObjectives": [
                        f"{region.lower()}_league_progress"
                    ]
                }
            ]
        })

    return (
        leader_npcs,
        leader_conversations,
        leader_quests
    )

# ============================================================
# MAIN
# ============================================================

def main():

    (beast_monsters, beast_items, beast_droplists, trainer_monsters, trainer_droplists) = create_beasts()
    (breeding_monsters, breeding_items, breeding_droplists, breeding_conversations, breeder_npcs) = create_breeding_system(beast_monsters)

    shopkeepers, shops, convo = create_region_shopkeepers()
    capture_conversations = create_capture_conversations(beast_monsters)

    region_trainers, region_trainer_droplists = (create_region_trainers(beast_monsters))
    evolution_scholars = create_evolution_scholars()
    professor_npc, professor_conversations = (create_professor_system(beast_monsters))
    professor_quest = create_professor_quest(beast_monsters)
    (league_npcs, league_conversations, league_quests) = create_region_leader_system()

    combined_trainers = trainer_monsters + region_trainers + [professor_npc] + league_npcs
    combined_droplists = (beast_droplists + trainer_droplists + region_trainer_droplists + breeding_droplists)
    combined_questlists = league_quests
    evolution_conversations = create_evolution_conversations(beast_monsters)

    # ========================================================
    # WRITE FILES
    # ========================================================

    write_json(
        os.path.join(OUTPUT_RAW, "actorconditions_beast.json"),
        BEAST_ACTORCONDITIONS
    )

    write_json(
        os.path.join(
            OUTPUT_RAW,
            "actorconditions_regions.json"
        ),
        REGION_MENTAL_CONDITIONS
    )

    write_json(
        os.path.join(OUTPUT_RAW, "droplists_beast.json"),
        combined_droplists
    )

    write_json(
        os.path.join(OUTPUT_RAW, "itemcategories_beast.json"),
        BEAST_ITEM_CATEGORIES
    )

    write_json(
        os.path.join(OUTPUT_RAW, "itemlist_beast.json"),
        beast_items + breeding_items + SPIRIT_ORB_ITEMS + HEAL_POTION_ITEMS + REGION_BADGE_ITEMS + REGION_RIBBON_ITEMS + PROFESSOR_REWARD_ITEMS + REGION_COMPLETION_REWARDS
    )

    write_json(
        os.path.join(OUTPUT_RAW, "monsterlist_beast.json"),
        beast_monsters + breeding_monsters
    )

    write_json(
        os.path.join(OUTPUT_RAW, "monsterlist_beast_npc.json"),
        breeder_npcs + shopkeepers + evolution_scholars
    )

    write_json(
        os.path.join(OUTPUT_RAW, "monsterlist_trainer.json"),
        combined_trainers
    )

    write_json(
        os.path.join(OUTPUT_SHOPS, "droplists_beast_shops.json"),
        shops
    )

    write_json(
        os.path.join(
            OUTPUT_QUESTS,
            "questlist_professor.json"
        ),
        [professor_quest]
    )

    write_json(
        os.path.join(
            OUTPUT_QUESTS,
            "questlist_region.json"
        ),
        league_quests
    )
    # ========================================================
    # EVOLUTION CONVERSATIONS
    # ========================================================

    for region, data in evolution_conversations.items():

        write_json(
            os.path.join(
                OUTPUT_CONVERSATIONS,
                f"conversationlist_{region.lower()}.json"
            ),
            data["conversations"]
        )

    for region, conversations in breeding_conversations.items():

        write_json(
            os.path.join(
                OUTPUT_BREEDING,
                f"conversationlist_breeding_{region.lower()}.json"
            ),
            conversations
        )

    all_beast_conversations = []
    for conversations in capture_conversations.values():
        all_beast_conversations.extend(conversations)
    write_json(
        os.path.join(
            OUTPUT_CONVERSATIONS,
            "conversationlist_beast.json"
        ),
        all_beast_conversations
    )

    all_shop_conversations = []
    for conversations in convo:
        all_shop_conversations.extend(conversations)
    write_json(
        os.path.join(
            OUTPUT_CONVERSATIONS,
            "conversationlist_shop.json"
        ),
        all_shop_conversations
    )

    write_json(
        os.path.join(
            OUTPUT_CONVERSATIONS,
            "conversationlist_professor.json"
        ),
        professor_conversations
    )

    write_json(
        os.path.join(
            OUTPUT_CONVERSATIONS,
            "conversationlist_region.json"
        ),
        league_conversations
    )

    if not os.environ.get("JASIA3_ORCHESTRATE"):
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
    print(f"Beasts: {len(beast_monsters)}")
    print(f"Hybrid Beasts: {len(breeding_monsters)}")
    print(f"Trainer Monsters: {len(trainer_monsters)}")
    print(f"Region Trainers: {len(region_trainers)}")
    print(f"Actor Conditions: {len(BEAST_ACTORCONDITIONS)+len(REGION_MENTAL_CONDITIONS)}")
    print(f"Beast Items: {len(beast_items)+len(breeding_items)}")
    print(f"Items: {len(SPIRIT_ORB_ITEMS) + len(HEAL_POTION_ITEMS) + len(REGION_BADGE_ITEMS) + len(REGION_RIBBON_ITEMS) + len(PROFESSOR_REWARD_ITEMS) + len(REGION_COMPLETION_REWARDS)}")
    print(f"Droplists: {len(combined_droplists)}")
    print(f"Questlists: {len(combined_questlists)+1}")
    print("===================================================")

if __name__ == "__main__":
    main()
