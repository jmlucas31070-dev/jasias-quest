#!/usr/bin/env python3
# jasia2.py — combined crafting + faction generator (pickpocket, jail, faction NPC dialogues)

import json
import os
import random
import runpy
import urllib.request
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from xml.dom import minidom

from at_format import write_json

# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent
OUTPUT_RAW = ROOT / "raw"
OUTPUT_VALUES = ROOT / "values"
OUTPUT_XML = ROOT / "xml"
TEMPLATE_TMX = ROOT / "template_faction.tmx"
TMX_TEMPLATE = ROOT / "template.tmx"
TMX_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/"
    "AndorsTrailRelease/andors-trail/"
    "refs/heads/master/AndorsTrail/res/xml/template.tmx"
)

TILE = 32
MAP_W = 30
MAP_H = 30

OUTPUT_RAW.mkdir(exist_ok=True)
OUTPUT_VALUES.mkdir(exist_ok=True)
OUTPUT_XML.mkdir(exist_ok=True)

random.seed()

# ============================================================
# RUN CRAFTING GENERATOR FIRST (skipped when run from jasia.py)
# ============================================================

if not os.environ.get("jasia_ORCHESTRATE"):
    print("=" * 50)
    print(" jasia2: running crafting.py")
    print("=" * 50)
    runpy.run_path(str(ROOT / "crafting.py"), run_name="__crafting__")

# ============================================================
# FACTION RESOURCE GENERATOR
# ============================================================

# ============================================================
# CONSTANTS
# ============================================================

ITEM_ICON = "items_armours:1"
MONSTER_ICON = "monsters_arulirs:1"
NPC_ICON = "npc_actors:1"

# ============================================================
# PICKPOCKET / JAIL (shared across factions)
# ============================================================

PICKPOCKET_ITEMS = []
PICKPOCKET_DROPLISTS = []
PICKPOCKET_CONVERSATIONS = []
JAIL_CONVERSATIONS = []
JAIL_MONSTERS = []
JAIL_DROPLISTS = []

BAIL_GOLD = 100


def make_conv(cid, message, replies=None, rewards=None):
    entry = {"id": cid, "message": message}
    if replies:
        entry["replies"] = replies
    if rewards:
        entry["rewards"] = rewards
    return entry


def req_thief_level(level):
    return {"requireType": "hasActorCondition", "requireID": f"thief_level_{level}"}


def req_inv_keep(item_id, qty=1):
    return {"requireType": "inventoryKeep", "requireID": item_id, "value": qty}


def r_drop_list(droplist_id):
    return {"rewardType": "dropList", "rewardID": droplist_id}


def r_mapchange(place, map_name="jail"):
    return {"rewardType": "mapchange", "rewardID": place, "mapName": map_name}


def r_give_item(item_id, qty=1):
    return {"rewardType": "giveItem", "rewardID": item_id, "value": qty}


def r_actor_cond(condition_id, duration=999):
    return {"rewardType": "actorCondition", "rewardID": condition_id, "value": duration}


def r_clear_actor_cond(condition_id):
    return {"rewardType": "actorCondition", "rewardID": condition_id, "value": -99}


def make_pp_item(item_id, name, desc, cost=0):
    return {
        "id": item_id,
        "name": name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": cost,
        "category": "misc",
        "description": desc,
    }


def make_pp_droplist(dl_id, item_id, chance, qty_min=1, qty_max=1):
    return {
        "id": dl_id,
        "items": [{
            "itemID": item_id,
            "chance": f"{chance}",
            "quantity": {"min": qty_min, "max": qty_max},
        }],
    }


def pickpocket_gold_chance(level):
    return min(100, 40 + (level - 1) * 5)


def pickpocket_gold_max(level):
    return 20 + (level - 1) * 10


def pickpocket_item_chance(level):
    return min(100, 50 + (level - 7) * 10)


def req_random(chance_pct):
    return {"requireType": "random", "requireID": str(chance_pct)}


def req_gold_pay(amount):
    return [
        {"requireType": "inventoryKeep", "requireID": "gold", "value": amount},
        {"requireType": "inventoryRemove", "requireID": "gold", "value": amount},
    ]


def build_pickpocket_and_jail_content():
    """Shared pickpocket roll dialogues, jail NPCs, and bail conversations."""
    global PICKPOCKET_DROPLISTS, PICKPOCKET_CONVERSATIONS
    global JAIL_CONVERSATIONS, JAIL_MONSTERS

    for level in range(1, 13):
        chance = pickpocket_gold_chance(level)
        max_gold = pickpocket_gold_max(level)
        PICKPOCKET_DROPLISTS.append({
            "id": f"droplist_pp_gold_reward_{level}",
            "items": [{
                "itemID": "gold",
                "chance": "100",
                "quantity": {"min": 1, "max": max_gold},
            }],
        })
        PICKPOCKET_CONVERSATIONS.append(make_conv(
            f"conv_pp_gold_roll_{level}",
            "You slip a hand toward their belongings...",
            [{"text": "N", "nextPhraseID": f"conv_pp_gold_result_{level}"}],
        ))
        PICKPOCKET_CONVERSATIONS.append({
            "id": f"conv_pp_gold_result_{level}",
            "replies": [
                {
                    "text": "N",
                    "nextPhraseID": f"conv_pp_gold_success_{level}",
                    "requires": [req_random(chance)],
                },
                {"text": "N", "nextPhraseID": "conv_pp_caught"},
            ],
        })
        PICKPOCKET_CONVERSATIONS.append(make_conv(
            f"conv_pp_gold_success_{level}",
            f"You pocket some coins (1–{max_gold} gold).",
            [{"text": "Nice.", "nextPhraseID": "X"}],
            [r_drop_list(f"droplist_pp_gold_reward_{level}")],
        ))

    PICKPOCKET_CONVERSATIONS.append(make_conv(
        "conv_pp_caught",
        "You've been caught! Guards drag you to the jail.",
        [{"text": "...", "nextPhraseID": "X", "rewards": [r_mapchange("entry")]}],
    ))

    gold_route = []
    for level in range(12, 0, -1):
        entry = {"text": "N", "nextPhraseID": f"conv_pp_gold_roll_{level}"}
        if level > 1:
            entry["requires"] = [req_thief_level(level)]
        gold_route.append(entry)
    PICKPOCKET_CONVERSATIONS.append({"id": "conv_pp_gold_route", "replies": gold_route})

    JAIL_CONVERSATIONS.extend([
        make_conv(
            "conv_jail_guard",
            "Stay in your cell, criminal.",
            [{"text": "Yes, sir.", "nextPhraseID": "X"}],
        ),
        make_conv(
            "conv_jail_captain",
            "You're here until someone posts your bail.",
            [{"text": "Understood.", "nextPhraseID": "X"}],
        ),
        make_conv(
            "conv_jail_lawyer",
            f"I can post bail for {BAIL_GOLD} gold. Interested?",
            [
                {
                    "text": f"Pay bail ({BAIL_GOLD} gold)",
                    "nextPhraseID": "conv_jail_freed",
                    "requires": req_gold_pay(BAIL_GOLD),
                },
                {"text": "Not now.", "nextPhraseID": "X"},
            ],
        ),
        make_conv(
            "conv_jail_freed",
            "You're free. Try not to end up back here.",
            [{"text": "Thanks.", "nextPhraseID": "X", "rewards": [r_mapchange("exit")]}],
        ),
    ])

    JAIL_MONSTERS.extend([
        {
            "id": "npc_jail_guard",
            "name": "Jail Guard",
            "iconID": NPC_ICON,
            "maxHP": 200,
            "attackChance": 60,
            "attackDamage": {"min": 8, "max": 16},
            "moveCost": 6,
            "attackCost": 6,
            "spawnGroup": "jail",
            "conversation": "conversationlist_jail",
            "phraseID": "conv_jail_guard",
        },
        {
            "id": "npc_jail_captain",
            "name": "Jail Captain",
            "iconID": NPC_ICON,
            "maxHP": 350,
            "attackChance": 75,
            "attackDamage": {"min": 12, "max": 24},
            "moveCost": 5,
            "attackCost": 5,
            "spawnGroup": "jail",
            "conversation": "conversationlist_jail",
            "phraseID": "conv_jail_captain",
        },
        {
            "id": "npc_jail_lawyer",
            "name": "Defense Lawyer",
            "iconID": NPC_ICON,
            "maxHP": 120,
            "attackChance": 20,
            "attackDamage": {"min": 2, "max": 6},
            "moveCost": 4,
            "attackCost": 4,
            "spawnGroup": "jail",
            "conversation": "conversationlist_jail",
            "phraseID": "conv_jail_lawyer",
        },
    ])


def _pp_item_route_conversations(faction):
    """Selector for faction item theft (thief rank 7+)."""
    conv_id = f"conv_pp_item_route_{faction}"
    if any(c["id"] == conv_id for c in PICKPOCKET_CONVERSATIONS):
        return []
    route_replies = []
    for level in range(12, 6, -1):
        entry = {
            "text": "N",
            "nextPhraseID": f"conv_pp_item_roll_{faction}_{level}",
            "requires": [req_thief_level(level)],
        }
        route_replies.append(entry)
    return [{"id": conv_id, "replies": route_replies}]


def build_faction_npc_menus(faction):
    """Battle / Leave / pickpocket menus for faction_npc_1..20."""
    convs = []
    PICKPOCKET_CONVERSATIONS.extend(_pp_item_route_conversations(faction))

    for npc_i in range(1, 21):
        replies = [
            {"text": "Battle", "nextPhraseID": "F"},
            {"text": "Leave", "nextPhraseID": "X"},
            {
                "text": "Pickpocket",
                "nextPhraseID": "conv_pp_gold_route",
                "requires": [req_thief_level(1)],
            },
            {
                "text": "Steal faction item",
                "nextPhraseID": f"conv_pp_item_route_{faction}",
                "requires": [req_thief_level(7)],
            },
        ]
        convs.append(make_conv(
            f"conv_{faction}_npc_{npc_i}",
            "The warrior eyes you warily. What do you want?",
            replies,
        ))
    return convs


def build_faction_item_steal_conversations(faction, misc_item_ids):
    """Item theft roll/success dialogues for thief rank 7+."""
    convs = []
    reward_items = misc_item_ids[:8] if misc_item_ids else [f"{faction}_item_1"]
    for level in range(7, 13):
        chance = pickpocket_item_chance(level)
        PICKPOCKET_DROPLISTS.append({
            "id": f"droplist_pp_item_reward_{faction}_{level}",
            "items": [{
                "itemID": iid,
                "chance": f"{str(max(5, 100 // len(reward_items)))}",
                "quantity": {"min": 1, "max": 1},
            } for iid in reward_items],
        })
        convs.append(make_conv(
            f"conv_pp_item_roll_{faction}_{level}",
            "You try to lift something valuable without being seen...",
            [{"text": "N", "nextPhraseID": f"conv_pp_item_result_{faction}_{level}"}],
        ))
        convs.append({
            "id": f"conv_pp_item_result_{faction}_{level}",
            "replies": [
                {
                    "text": "N",
                    "nextPhraseID": f"conv_pp_item_success_{faction}_{level}",
                    "requires": [req_random(chance)],
                },
                {"text": "N", "nextPhraseID": "conv_pp_caught"},
            ],
        })
        convs.append(make_conv(
            f"conv_pp_item_success_{faction}_{level}",
            f"You slip away with a {faction_title(faction)} curio.",
            [{"text": "Excellent.", "nextPhraseID": "X"}],
            [r_drop_list(f"droplist_pp_item_reward_{faction}_{level}")],
        ))
    return convs


def faction_shop_conv(conv_id, message, shop_label):
    return make_conv(
        conv_id,
        message,
        [
            {"text": shop_label, "nextPhraseID": "S"},
            {"text": "Farewell.", "nextPhraseID": "X"},
        ],
    )


# ============================================================
# LOADRESOURCES.XML
# ============================================================

LOADRESOURCES_HEADER = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<resources>
"""

LOADRESOURCES_FOOTER = """
</resources>
"""

# ============================================================
# FACTIONS
# ============================================================

FACTIONS = [
    "human", "half_elf", "elf", "wood_elf", "sea_elf",
    "drow_elf", "hill_dwarf", "mountain_dwarf", "dark_dwarf", "kender",
    "gnome", "deep_gnome", "faerie", "goblin", "hobgoblin",
    "ogre", "centaur", "minotaur", "orc", "kobold",
    "giant", "halfling"
]

# ============================================================
# NPC CLASSES
# ============================================================

NPC_CLASSES = [
    "Warrior", "Guard", "Scout", "Hunter", "Mage",
    "Priest", "Archer", "Shaman", "Knight", "Assassin",
    "Raider", "Captain", "Champion", "Berserker",
    "Mystic", "Witch", "Ranger", "Defender", "Mercenary",
    "Alchemist", "Beastmaster", "Warden", "Sentry"
]

# ============================================================
# WEAPON DATA
# ============================================================

FACTION_WEAPON_TYPES = [
    "Knife", "Sword", "Club", "Staff", "Mace",
    "Dagger", "Spear", "Hammer", "Battle Axe"
]

FACTION_WEAPON_PREFIXES = [
    "Iron", "Steel", "Dark", "Shadow", "Ancient",
    "Savage", "Royal", "Heavy", "Mystic", "Runed",
    "Blood", "Golden"
]

# ============================================================
# ARMOR SLOTS
# ============================================================

FACTION_ARMOR_SLOTS = [
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
    "human": [
        "Steel Coin",
        "Traveler Token",
        "Merchant Ledger",
        "Guard Insignia",
        "Wax Seal",
        "Town Charter",
        "Prayer Beads",
        "Copper Badge",
        "Map Fragment",
        "Ink Bottle",
        "Dice Set",
        "Silver Button",
        "Rope Knot",
        "Wooden Charm",
        "Family Crest"
    ],

    "half_elf": [
        "Silver Pendant",
        "Forest Herb",
        "Elven Scroll",
        "Moonstone Charm",
        "Willow Branch",
        "Mystic Ink",
        "Fine Thread",
        "Song Crystal",
        "Spirit Totem",
        "Silverleaf Tea",
        "Woodland Emblem",
        "Feather Token",
        "Rune Tablet",
        "Ancient Leaf",
        "Moonwater Vial"
    ],

    "elf": [
        "Moon Crystal",
        "Silver Leaf",
        "Ancient Acorn",
        "Enchanted Bark",
        "Runed Feather",
        "Emerald Brooch",
        "Spirit Moss",
        "Celestial Dust",
        "Sacred Sap",
        "Star Charm",
        "Elven Relic",
        "Moon Sigil",
        "Crystal Tear",
        "Ancient Rune",
        "Forest Emblem"
    ],

    "wood_elf": [
        "Forest Charm",
        "Nature Stone",
        "Pine Resin",
        "Wolf Fang",
        "Wild Berry Seed",
        "Woodland Totem",
        "Bird Feather",
        "Herbal Poultice",
        "Oak Sapling",
        "Forest Emblem",
        "Nature Rune",
        "Moss Bundle",
        "Tree Symbol",
        "Whisper Leaf",
        "Spirit Branch"
    ],

    "sea_elf": [
        "Pearl Necklace",
        "Coral Gem",
        "Tidal Charm",
        "Salt Crystal",
        "Conch Shell",
        "Ocean Pearl",
        "Shark Tooth",
        "Driftwood Idol",
        "Wave Stone",
        "Siren Scale",
        "Water Rune",
        "Tide Symbol",
        "Sea Glass",
        "Blue Coral",
        "Ocean Relic"
    ],

    "drow_elf": [
        "Spider Fang",
        "Shadow Crystal",
        "Dark Rune",
        "Venom Sac",
        "Underdark Gem",
        "Black Candle",
        "Web Silk",
        "Moonless Orb",
        "Shadow Dust",
        "Bone Charm",
        "Darksteel Ring",
        "Night Sigil",
        "Obsidian Charm",
        "Whisper Stone",
        "Spider Idol"
    ],

    "hill_dwarf": [
        "Stone Mug",
        "Iron Nugget",
        "Copper Ore",
        "Coal Chunk",
        "Stone Idol",
        "Granite Shard",
        "Forge Emblem",
        "Tunnel Mark",
        "Iron Token",
        "Bronze Crest",
        "Stone Relic",
        "Mining Seal",
        "Rune Pebble",
        "Anvil Fragment",
        "Ore Sample"
    ],

    "mountain_dwarf": [
        "Bronze Coin",
        "Steel Ore",
        "Runed Anvil Fragment",
        "Iron Beard Ring",
        "Battle Mug",
        "Mountain Crest",
        "Ore Satchel",
        "Fire Crystal",
        "Forge Coal",
        "Stone Rune",
        "Granite Totem",
        "Ancestral Seal",
        "Forgemaster Token",
        "Deep Ore",
        "Mountain Relic"
    ],

    "dark_dwarf": [
        "Obsidian Shard",
        "Black Iron",
        "Deep Coal",
        "Bloodstone",
        "Molten Core",
        "Charred Bone",
        "Blacksmith Talisman",
        "Runed Coal",
        "Dark Emblem",
        "Ash Token",
        "Shadow Ore",
        "Burned Sigil",
        "Obsidian Rune",
        "Dark Relic",
        "Cinder Fragment"
    ],

    "kender": [
        "Lucky Dice",
        "Travel Pouch",
        "Stolen Spoon",
        "Marble Toy",
        "Button Collection",
        "Colorful Ribbon",
        "Old Coin",
        "String Bracelet",
        "Tiny Charm",
        "Pocket Token",
        "Lucky Pebble",
        "Traveler Badge",
        "Copper Trinket",
        "Curious Relic",
        "Miniature Idol"
    ],

    "gnome": [
        "Clockwork Gear",
        "Magic Lens",
        "Tiny Cogwheel",
        "Copper Spring",
        "Steam Valve",
        "Brass Compass",
        "Gadget Frame",
        "Glass Tube",
        "Pocket Watch",
        "Oil Flask",
        "Blueprint Scroll",
        "Mechanical Token",
        "Gear Emblem",
        "Brass Ring",
        "Inventor Seal"
    ],

    "deep_gnome": [
        "Crystal Dust",
        "Cave Gem",
        "Tunnel Map",
        "Glow Mushroom",
        "Echo Crystal",
        "Dark Rope Fragment",
        "Subterranean Compass",
        "Cave Moss",
        "Underground Relic",
        "Gemstone Ring",
        "Lantern Fuel",
        "Crystal Fragment",
        "Stone Symbol",
        "Underdark Seal",
        "Glow Crystal"
    ],

    "faerie": [
        "Fairy Dust",
        "Glow Flower",
        "Tiny Bell",
        "Moon Petal",
        "Sparkling Dew",
        "Butterfly Wing",
        "Pixie Charm",
        "Rainbow Thread",
        "Dream Essence",
        "Magic Acorn",
        "Whisper Leaf",
        "Mystic Pollen",
        "Crystal Dewdrop",
        "Enchanted Feather",
        "Sprite Token"
    ],

    "goblin": [
        "Bone Charm",
        "Scrap Metal",
        "Rat Tail",
        "Torn Sack",
        "Mud Totem",
        "Sharp Bone",
        "Rusty Nails",
        "Greasy Cloth",
        "Goblin Token",
        "Broken Idol",
        "Filthy Rag",
        "Cracked Coin",
        "Mud Stone",
        "Stolen Trinket",
        "Tribal Mark"
    ],

    "hobgoblin": [
        "War Banner",
        "Battle Totem",
        "Military Orders",
        "Chain Links",
        "Officer Medal",
        "War Paint",
        "Barracks Key",
        "Iron Crest",
        "Battle Sigil",
        "Command Seal",
        "War Drum Fragment",
        "Military Token",
        "Honor Mark",
        "Legion Emblem",
        "Blood Banner"
    ],

    "ogre": [
        "Heavy Chain",
        "Massive Bone",
        "Thick Hide",
        "Crude Necklace",
        "Large Skull",
        "Ogre Tooth",
        "Iron Shackles",
        "Animal Fur",
        "Torn Belt",
        "Bone Totem",
        "Giant Fang",
        "Savage Charm",
        "Hide Scrap",
        "War Mark",
        "Brute Emblem"
    ],

    "centaur": [
        "Horse Charm",
        "Leather Strap",
        "Trail Map",
        "Herbal Blend",
        "War Saddle Emblem",
        "Feather Token",
        "Bronze Horseshoe",
        "Forest Crest",
        "Wind Charm",
        "Travel Mark",
        "Swift Sigil",
        "Nature Totem",
        "Oak Relic",
        "Prairie Stone",
        "Spirit Bead"
    ],

    "minotaur": [
        "Horn Fragment",
        "Labyrinth Stone",
        "Bull Hide",
        "Maze Key",
        "Stone Tablet",
        "War Totem",
        "Bronze Ring",
        "Labyrinth Map",
        "Blood Pendant",
        "Chain Belt Fragment",
        "Horn Totem",
        "Maze Relic",
        "Ancient Sigil",
        "Bull Crest",
        "Labyrinth Rune"
    ],

    "orc": [
        "War Paint",
        "Orc Talisman",
        "Skull Trophy",
        "Bone Necklace",
        "Blood Flask",
        "Torn Banner",
        "Wolf Pelt",
        "War Drum Fragment",
        "Tooth Charm",
        "Chain Bracer Fragment",
        "Battle Token",
        "Clan Emblem",
        "Savage Sigil",
        "Orcish Rune",
        "Blood Mark"
    ],

    "kobold": [
        "Dragon Tooth",
        "Candle Stub",
        "Scale Fragment",
        "Trap Kit Fragment",
        "Mining Candle",
        "Cave Rope",
        "Lizard Hide",
        "Bone Needle",
        "Dragon Idol",
        "Scorched Stone",
        "Tail Ring",
        "Smoke Powder",
        "Scale Charm",
        "Dragon Rune",
        "Cave Token"
    ],

    "giant": [
        "Giant Bone",
        "Huge Boulder Fragment",
        "Massive Chain",
        "Stone Pillar Fragment",
        "Large Fur Cloak Scrap",
        "Massive Tooth",
        "Thunder Drum Fragment",
        "Colossal Belt Fragment",
        "Iron Boulder",
        "Mountain Trophy",
        "War Totem",
        "Thunder Stone",
        "Titan Relic",
        "Storm Rune",
        "Giant Emblem"
    ],

    "halfling": [
        "Pipe Weed",
        "Lucky Ring",
        "Garden Herb",
        "Copper Spoon",
        "Comfort Blanket Scrap",
        "Family Brooch",
        "Fishing Hook",
        "Mini Lantern Charm",
        "Picnic Token",
        "Lucky Pebble",
        "Village Crest",
        "Traveler Charm",
        "Harvest Ribbon",
        "Hearth Symbol",
        "Homestead Mark"
    ]
}
# ============================================================
# HELPERS
# ============================================================




def pretty_xml(element):
    rough = ET.tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="    ")



def write_xml(path, root):
    xml_data = pretty_xml(root)
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml_data)



def random_faction_damage(mult=1):
    low = random.randint(4, 20) * mult
    high = low + random.randint(5, 25) * mult
    return low, high



def faction_title(name):
    return name.replace("_", " ").title()



def make_item(
    item_id,
    name,
    category,
    description,
    cost,
    effects=None
):

    data = {
        "id": item_id,
        "name": name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": cost,
        "category": category,
        "description": description
    }

    if effects:
        data["equipEffect"] = effects

    return data



def make_droplist(drop_id, items):
    return {
        "id": drop_id,
        "items": items
    }



def make_drop_item(item_id, chance=100, min_qty=1, max_qty=1):
    return {
        "itemID": item_id,
        "quantity": {
            "min": min_qty,
            "max": max_qty
        },
        "chance": f"{chance}"
    }


# ============================================================
# GRANDMASTER TARGET ROTATION
# ============================================================

GRANDMASTER_TARGETS = {}

for idx, faction in enumerate(FACTIONS):
    target = FACTIONS[(idx + (len(FACTIONS) // 2)) % len(FACTIONS)]
    GRANDMASTER_TARGETS[faction] = target

# ============================================================
# LOADRESOURCE ARRAYS
# ============================================================

loadresource_items = []
loadresource_monsters = []
loadresource_droplists = []
loadresource_conversationlists = []
loadresource_quests = []

build_pickpocket_and_jail_content()

# ============================================================
# MAIN GENERATION LOOP
# ============================================================

for faction in FACTIONS:

    faction_name = faction_title(faction)

    faction_monsters = []
    faction_weapons = []
    faction_armors = []
    misc_items = []
    quest_items = []
    droplists = []
    conversations = []
    quests = []

    drop_pool = []
    store_inventory = []

    opposing_faction = GRANDMASTER_TARGETS[faction]
    opposing_name = faction_title(opposing_faction)

    # ========================================================
    # QUEST ITEM
    # ========================================================

    faction_token_id = f"{faction}_grandmaster_token"

    faction_token = make_item(
        faction_token_id,
        f"{faction_name} Grandmaster Sigil",
        "misc",
        f"A sigil stolen from the {faction_name} grandmaster.",
        5000
    )

    quest_items.append(faction_token)
    #drop_pool.append(faction_token_id)

    # ========================================================
    # CREATE WEAPONS
    # ========================================================

    for i in range(12):

        weapon_name = (
            f"{faction_name} "
            f"{random.choice(FACTION_WEAPON_PREFIXES)} "
            f"{random.choice(FACTION_WEAPON_TYPES)}"
        )

        item_id = f"{faction}_weapon_{i+1}"

        item = make_item(
            item_id,
            weapon_name,
            "weapon",
            f"A weapon crafted by the {faction_name}.",
            random.randint(200, 3500),
            {
                "increaseAttackChance": random.randint(5, 20),
                "increaseAttackDamage": {
                    "min": random.randint(5, 15),
                    "max": random.randint(20, 45)
                }
            }
        )

        faction_weapons.append(item)
        drop_pool.append(item_id)
        store_inventory.append(item_id)

    # ========================================================
    # CREATE ARMOR
    # ========================================================

    for i in range(16):

        slot_id, slot_name = FACTION_ARMOR_SLOTS[i % len(FACTION_ARMOR_SLOTS)]

        armor_name = (
            f"{faction_name} "
            f"{random.choice(FACTION_WEAPON_PREFIXES)} "
            f"{slot_name}"
        )

        item_id = f"{faction}_armor_{i+1}"

        item = make_item(
            item_id,
            armor_name,
            slot_id,
            f"Armor worn by the {faction_name}.",
            random.randint(250, 4000),
            {
                "increaseArmor": random.randint(5, 45),
                "increaseMaxHP": random.randint(10, 120)
            }
        )

        faction_armors.append(item)
        drop_pool.append(item_id)
        store_inventory.append(item_id)

    # ========================================================
    # MISC ITEMS
    # ========================================================

    race_item_pool = RACE_ITEMS.get(faction, ["Ancient Trinket"])

    for i in range(15):

        item_name = random.choice(race_item_pool)
        item_id = f"{faction}_item_{i+1}"

        item = make_item(
            item_id,
            item_name,
            "misc",
            f"A common item carried by the {faction_name}.",
            random.randint(50, 1200)
        )

        misc_items.append(item)
        drop_pool.append(item_id)

    # ========================================================
    # SPECIAL GRANDMASTER GEAR
    # ========================================================

    gm_weapon_id = f"{faction}_grandmaster_weapon"
    gm_armor_id = f"{faction}_grandmaster_armor"

    gm_weapon = make_item(
        gm_weapon_id,
        f"{faction_name} Grandmaster Blade",
        "weapon",
        f"The personal weapon of the {faction_name} grandmaster.",
        12000,
        {
            "increaseAttackChance": 35,
            "increaseAttackDamage": {
                "min": 40,
                "max": 85
            }
        }
    )

    gm_armor = make_item(
        gm_armor_id,
        f"{faction_name} Grandmaster Armor",
        "body",
        f"Legendary armor worn by the {faction_name} grandmaster.",
        14000,
        {
            "increaseArmor": 60,
            "increaseMaxHP": 250
        }
    )

    faction_weapons.append(gm_weapon)
    faction_armors.append(gm_armor)


    # ========================================================
    # STANDARD NPCS
    # ========================================================

    standard_weapon_ids = [item["id"] for item in faction_weapons[:12]]
    standard_armor_ids = [item["id"] for item in faction_armors[:16]]
    standard_misc_ids = [item["id"] for item in misc_items]

    standard_droplist_id = f"droplist_{faction}_standard"

    # ====================================================
    # SHARED STANDARD NPC DROPLIST
    # ====================================================

    shared_standard_drops = []

    # Even split between weapon / armor / misc pools
    for item_id in standard_weapon_ids:
        shared_standard_drops.append(
            make_drop_item(item_id, 3)
        )

    for item_id in standard_armor_ids:
        shared_standard_drops.append(
            make_drop_item(item_id, 3)
        )

    for item_id in standard_misc_ids:
        shared_standard_drops.append(
            make_drop_item(item_id, 3)
        )

    # Additional lower chance secondary drops
    for item_id in random.sample(standard_misc_ids, min(8, len(standard_misc_ids))):
        shared_standard_drops.append(
            make_drop_item(item_id, 1)
        )

    droplists.append(
        make_droplist(
            standard_droplist_id,
            shared_standard_drops
        )
    )

    # ====================================================
    # CREATE STANDARD NPCS
    # ====================================================

    for i in range(20):

        npc_name = (
            f"{faction_name} "
            f"{random.choice(NPC_CLASSES)}"
        )

        low, high = random_faction_damage()

        npc_num = i + 1
        monster = {
            "id": f"{faction}_npc_{npc_num}",
            "name": npc_name,
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(80, 650),
            "attackChance": random.randint(45, 90),
            "attackDamage": {
                "min": low,
                "max": high
            },
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8),
            "droplistID": standard_droplist_id,
            "spawnGroup": "faction",
            "faction": faction,
            "conversation": f"conversationlist_faction_{faction}",
            "phraseID": f"conv_{faction}_npc_{npc_num}",
        }

        faction_monsters.append(monster)

    # ========================================================
    # WEAPONER
    # ========================================================

    weaponer_id = f"{faction}_weaponer"
    weaponer_drop = f"droplist_{weaponer_id}"
    weaponer_phrase = f"conv_{weaponer_id}"

    faction_monsters.append({
        "id": weaponer_id,
        "name": f"{faction_name} Weaponer",
        "iconID": NPC_ICON,
        "maxHP": 500,
        "attackChance": 65,
        "attackDamage": {
            "min": 20,
            "max": 35
        },
        "moveCost": 4,
        "attackCost": 4,
        "droplistID": weaponer_drop,
        "conversation": f"conversationlist_faction_{faction}",
        "phraseID": weaponer_phrase,
        "spawnGroup": "faction",
        "faction": faction
    })

    droplists.append(make_droplist(
        weaponer_drop,
        [make_drop_item(item["id"], 100) for item in faction_weapons[:8]]
    ))

    conversations.append(faction_shop_conv(
        weaponer_phrase,
        f"The finest weapons of the {faction_name} are forged here.",
        "Show me your weapons.",
    ))

    # ========================================================
    # ARMORER
    # ========================================================

    armorer_id = f"{faction}_armorer"
    armorer_drop = f"droplist_{armorer_id}"
    armorer_phrase = f"conv_{armorer_id}"

    faction_monsters.append({
        "id": armorer_id,
        "name": f"{faction_name} Armorer",
        "iconID": NPC_ICON,
        "maxHP": 550,
        "attackChance": 70,
        "attackDamage": {
            "min": 25,
            "max": 40
        },
        "moveCost": 4,
        "attackCost": 4,
        "droplistID": armorer_drop,
        "conversation": f"conversationlist_faction_{faction}",
        "phraseID": armorer_phrase,
        "spawnGroup": "faction",
        "faction": faction
    })

    droplists.append(make_droplist(
        armorer_drop,
        [make_drop_item(item["id"], 100) for item in faction_armors[:10]]
    ))

    conversations.append(faction_shop_conv(
        armorer_phrase,
        f"Our armor protects the warriors of the {faction_name}.",
        "Show me your armor.",
    ))

    # ========================================================
    # SHOPKEEPER
    # ========================================================

    shopkeeper_id = f"{faction}_shopkeeper"
    shopkeeper_drop = f"droplist_{shopkeeper_id}"
    shopkeeper_phrase = f"conv_{shopkeeper_id}"

    faction_monsters.append({
        "id": shopkeeper_id,
        "name": f"{faction_name} Shopkeeper",
        "iconID": NPC_ICON,
        "maxHP": 400,
        "attackChance": 50,
        "attackDamage": {
            "min": 12,
            "max": 24
        },
        "moveCost": 4,
        "attackCost": 4,
        "droplistID": shopkeeper_drop,
        "conversation": f"conversationlist_faction_{faction}",
        "phraseID": shopkeeper_phrase,
        "spawnGroup": "faction",
        "faction": faction
    })

    # ====================================================
    # SHOPKEEPER INVENTORY
    # ====================================================

    misc_inventory = [item["id"] for item in misc_items]

    shopkeeper_inventory = (
        misc_inventory
    )

    droplists.append(make_droplist(
        shopkeeper_drop,
        [
            make_drop_item(item_id, 100)
            for item_id in shopkeeper_inventory
        ]
    ))

    conversations.append(faction_shop_conv(
        shopkeeper_phrase,
        (
            f"Travelers are always welcome among the {faction_name}. "
            f"I also collect many curios and cultural items from our people."
        ),
        "Show me your goods.",
    ))

    # ========================================================
    # LEADER
    # ========================================================

    leader_id = f"{faction}_leader"
    leader_drop = f"droplist_{leader_id}"
    leader_phrase = f"conv_{leader_id}"
    leader_quest_id = f"quest_{faction}_retrieve_sigil"

    faction_monsters.append({
        "id": leader_id,
        "name": f"{faction_name} Leader",
        "iconID": NPC_ICON,
        "maxHP": 900,
        "attackChance": 82,
        "attackDamage": {
            "min": 30,
            "max": 60
        },
        "moveCost": 4,
        "attackCost": 4,
        "droplistID": leader_drop,
        "conversation": f"conversationlist_faction_{faction}",
        "phraseID": leader_phrase,
        "spawnGroup": "faction",
        "faction": faction
    })

    droplists.append(make_droplist(
        leader_drop,
        [
            make_drop_item(random.choice(drop_pool), 100)
        ]
    ))

    conversations.append(make_conv(
        leader_phrase,
        (
            f"The {opposing_name} grandmaster stole our sacred sigil. "
            f"Bring it back and you shall earn our favor."
        ),
        [
            {
                "text": "I will retrieve the sigil.",
                "nextPhraseID": "X",
                "rewards": [
                    {"rewardType": "questProgress", "rewardID": leader_quest_id, "value": 10}
                ],
            },
            {
                "text": "I have the sigil.",
                "nextPhraseID": "X",
                "requires": [
                    {"requireType": "inventoryKeep", "requireID": faction_token_id, "value": 1},
                    {"requireType": "inventoryRemove", "requireID": faction_token_id, "value": 1},
                ],
                "rewards": [
                    {"rewardType": "questProgress", "rewardID": leader_quest_id, "value": 100}
                ],
            },
            {"text": "Farewell.", "nextPhraseID": "X"},
        ],
    ))

    misc_ids = [item["id"] for item in misc_items]
    conversations.extend(build_faction_npc_menus(faction))
    conversations.extend(build_faction_item_steal_conversations(faction, misc_ids))
    conversations.extend(PICKPOCKET_CONVERSATIONS)

    quests.append({
        "id": leader_quest_id,
        "name": f"Retrieve the {faction_name} Sigil",
        "description": (
            f"Recover the stolen sigil from the {opposing_name} grandmaster."
        ),
        "objective": (
            f"Bring the {faction_name} Grandmaster Sigil to the {faction_name} leader."
        ),
        "requiredItems": [
            {
                "itemID": faction_token_id,
                "quantity": 1
            }
        ],
        "rewardExperience": 5000,
        "rewardGold": 2500
    })

    # ========================================================
    # GRANDMASTER
    # ========================================================

    grandmaster_id = f"{faction}_grandmaster"
    grandmaster_drop = f"droplist_{grandmaster_id}"

    gm_low, gm_high = random_faction_damage(4)

    faction_monsters.append({
        "id": grandmaster_id,
        "name": f"{faction_name} Grandmaster",
        "iconID": MONSTER_ICON,
        "maxHP": 3500,
        "attackChance": 98,
        "attackDamage": {
            "min": gm_low,
            "max": gm_high
        },
        "moveCost": 3,
        "attackCost": 3,
        "droplistID": grandmaster_drop,
        "spawnGroup": "faction",
        "faction": faction
    })

    opposing_token = f"{opposing_faction}_grandmaster_token"

    droplists.append(make_droplist(
        grandmaster_drop,
        [
            make_drop_item(opposing_token, 100),
            make_drop_item(gm_weapon_id, 100),
            make_drop_item(gm_armor_id, 100)
        ]
    ))

    # ========================================================
    # WRITE RESOURCE FILES
    # ========================================================

    item_output = (
        faction_weapons +
        faction_armors +
        misc_items +
        quest_items
    )

    write_json(OUTPUT_RAW / f"itemlist_faction_{faction}.json", item_output)
    write_json(OUTPUT_RAW / f"monsterlist_faction_{faction}.json", faction_monsters)
    write_json(OUTPUT_RAW / f"droplists_faction_{faction}.json", droplists)
    write_json(OUTPUT_RAW / f"conversationlist_faction_{faction}.json", conversations)
    write_json(OUTPUT_RAW / f"questlist_faction_{faction}.json", quests)

    # ========================================================
    # TMX MAP CREATION
    # ========================================================

    if os.path.exists(TEMPLATE_TMX):

        tree = ET.parse(TEMPLATE_TMX)
        root = tree.getroot()

        spawn_layer = None

        for layer in root.findall("objectgroup"):
            if layer.attrib.get("name", "").lower() == "spawn":
                spawn_layer = layer
                break

        if spawn_layer is not None:

            spawn_layer.clear()

            spawn_layer.attrib = {
                "id": "6",
                "name": "Spawn"
            }

            special_spawns = [
                ("grandmaster", f"{faction}_grandmaster", 64, 416),
                ("leader", f"{faction}_leader", 160, 416),
                ("weaponer", f"{faction}_weaponer", 256, 416),
                ("armorer", f"{faction}_armorer", 352, 416),
                ("shopkeeper", f"{faction}_shopkeeper", 448, 416)
            ]

            object_id = 2

            for display_name, monster_id, x, y in special_spawns:

                obj = ET.SubElement(spawn_layer, "object")

                obj.attrib = {
                    "id": str(object_id),
                    "name": display_name,
                    "type": "spawn",
                    "x": str(x),
                    "y": str(y),
                    "width": "32",
                    "height": "32"
                }

                properties = ET.SubElement(obj, "properties")

                prop = ET.SubElement(properties, "property")

                prop.attrib = {
                    "name": "spawngroup",
                    "value": monster_id
                }

                object_id += 1

        # ====================================================
        # PRETTY FORMAT XML WITHOUT EXTRA BLANK LINES
        # ====================================================

        xml_string = ET.tostring(root, encoding="utf-8")

        parsed_xml = minidom.parseString(xml_string)

        pretty_xml = parsed_xml.toprettyxml(indent=" ")

        # Remove blank lines added by minidom
        pretty_xml = "\n".join(
            [line for line in pretty_xml.split("\n") if line.strip()]
        )

        with open(
            OUTPUT_XML / f"faction_{faction}.tmx",
            "w",
            encoding="utf-8",
            newline="\n"
        ) as xml_file:

            xml_file.write(pretty_xml)

    # ========================================================
    # LOADRESOURCE ENTRIES
    # ========================================================

    loadresource_items.append(
        f"        <item>@raw/itemlist_faction_{faction}</item>"
    )

    loadresource_monsters.append(
        f"        <item>@raw/monsterlist_faction_{faction}</item>"
    )

    loadresource_droplists.append(
        f"        <item>@raw/droplists_faction_{faction}</item>"
    )

    loadresource_conversationlists.append(
        f"        <item>@raw/conversationlist_faction_{faction}</item>"
    )

    loadresource_quests.append(
        f"        <item>@raw/questlist_faction_{faction}</item>"
    )

# ============================================================
# JAIL MAP (jail.tmx)
# ============================================================

def download_main_template():
    if TMX_TEMPLATE.exists():
        return
    print("Downloading template.tmx for jail map...")
    urllib.request.urlretrieve(TMX_TEMPLATE_URL, TMX_TEMPLATE)


def build_jail_tmx():
    download_main_template()
    if not TMX_TEMPLATE.exists():
        print("Warning: template.tmx missing; skipping jail.tmx")
        return

    root = ET.parse(TMX_TEMPLATE).getroot()
    root = deepcopy(root)

    mapevents = None
    spawn_layer = None
    for layer in root.findall("objectgroup"):
        if layer.get("name") == "Mapevents":
            mapevents = layer
        if layer.get("name", "").lower() == "spawn":
            spawn_layer = layer

    if mapevents is None:
        mapevents = ET.SubElement(root, "objectgroup", {"name": "Mapevents"})
    if spawn_layer is None:
        spawn_layer = ET.SubElement(root, "objectgroup", {"name": "Spawn"})

    oid = 50

    def add_obj(parent, name, otype, tx, ty, tw=1, th=1, props=None):
        nonlocal oid
        obj = ET.SubElement(parent, "object", {
            "id": str(oid),
            "name": name,
            "type": otype,
            "x": str(tx * TILE),
            "y": str(ty * TILE),
            "width": str(tw * TILE),
            "height": str(th * TILE),
        })
        oid += 1
        if props:
            p = ET.SubElement(obj, "properties")
            for k, v in props.items():
                ET.SubElement(p, "property", {"name": k, "value": str(v)})

    add_obj(mapevents, "entry", "mapchange", 14, 0, 2, 1)
    add_obj(mapevents, "exit", "mapchange", 14, 29, 2, 1,
            {"map": "faction_human", "place": "entry"})

    for idx, (npc_id, phrase) in enumerate([
        ("npc_jail_guard", "conv_jail_guard"),
        ("npc_jail_captain", "conv_jail_captain"),
        ("npc_jail_lawyer", "conv_jail_lawyer"),
    ]):
        add_obj(spawn_layer, npc_id, "spawn", 6 + idx * 4, 14, 1, 1,
                {"spawngroup": npc_id, "phrase": phrase})

    ET.indent(root)
    ET.ElementTree(root).write(
        OUTPUT_XML / "jail.tmx",
        encoding="utf-8",
        xml_declaration=True,
    )


# ============================================================
# WRITE SHARED JAIL / PICKPOCKET RESOURCES
# ============================================================

write_json(OUTPUT_RAW / "conversationlist_jail.json", JAIL_CONVERSATIONS)
write_json(OUTPUT_RAW / "monsterlist_jail.json", JAIL_MONSTERS)
write_json(OUTPUT_RAW / "droplists_pickpocket.json", PICKPOCKET_DROPLISTS)
if PICKPOCKET_ITEMS:
    write_json(OUTPUT_RAW / "itemlist_pickpocket.json", PICKPOCKET_ITEMS)

build_jail_tmx()

# ============================================================
# LOADRESOURCES (full merge standalone, fragment when orchestrated)
# ============================================================


def _write_jasia2_loadresource_fragment():
    """Faction/jail/pickpocket entries for jasia.py to merge."""
    fragment = [LOADRESOURCES_HEADER]
    blocks = [
        ("loadresource_items", loadresource_items),
        ("loadresource_monsters", loadresource_monsters),
        ("loadresource_droplists", loadresource_droplists),
        ("loadresource_conversationlists", loadresource_conversationlists),
        ("loadresource_quests", loadresource_quests),
    ]
    for array_name, entries in blocks:
        if not entries:
            continue
        fragment.append(f'    <array name="{array_name}">')
        fragment.extend(entries)
        if array_name == "loadresource_items" and PICKPOCKET_ITEMS:
            fragment.append("        <item>@raw/itemlist_pickpocket</item>")
        if array_name == "loadresource_monsters":
            fragment.append("        <item>@raw/monsterlist_jail</item>")
        if array_name == "loadresource_droplists":
            fragment.append("        <item>@raw/droplists_pickpocket</item>")
        if array_name == "loadresource_conversationlists":
            fragment.append("        <item>@raw/conversationlist_jail</item>")
        fragment.append("    </array>")
        fragment.append("")
    fragment.append(LOADRESOURCES_FOOTER.strip())
    (OUTPUT_VALUES / "loadresources_jasia2_fragment.xml").write_text(
        "\n".join(fragment), encoding="utf-8"
    )


if os.environ.get("jasia_ORCHESTRATE"):
    _write_jasia2_loadresource_fragment()
else:
    CRAFTING_LR = OUTPUT_VALUES / "loadresources.xml"
    loadresources = [LOADRESOURCES_HEADER]
    loadresources.append("    <array name=\"loadresource_items\">")
    if CRAFTING_LR.exists():
        crafting_xml = CRAFTING_LR.read_text(encoding="utf-8")
        in_items = False
        for line in crafting_xml.splitlines():
            if "<array name=\"loadresource_items\">" in line:
                in_items = True
                continue
            if in_items:
                if "</array>" in line:
                    break
                if "<item>" in line:
                    loadresources.append(line)
    loadresources.extend(loadresource_items)
    if PICKPOCKET_ITEMS:
        loadresources.append("        <item>@raw/itemlist_pickpocket</item>")
    loadresources.append("    </array>\n")

    loadresources.append("    <array name=\"loadresource_monsters\">")
    if CRAFTING_LR.exists():
        in_mon = False
        for line in crafting_xml.splitlines():
            if "<array name=\"loadresource_monsters\">" in line:
                in_mon = True
                continue
            if in_mon:
                if "</array>" in line:
                    break
                if "<item>" in line:
                    loadresources.append(line)
    loadresources.extend(loadresource_monsters)
    loadresources.append("        <item>@raw/monsterlist_jail</item>")
    loadresources.append("    </array>\n")

    loadresources.append("    <array name=\"loadresource_droplists\">")
    if CRAFTING_LR.exists():
        in_dl = False
        for line in crafting_xml.splitlines():
            if "<array name=\"loadresource_droplists\">" in line:
                in_dl = True
                continue
            if in_dl:
                if "</array>" in line:
                    break
                if "<item>" in line:
                    loadresources.append(line)
    loadresources.extend(loadresource_droplists)
    loadresources.append("        <item>@raw/droplists_pickpocket</item>")
    loadresources.append("    </array>\n")

    loadresources.append("    <array name=\"loadresource_conversationlists\">")
    if CRAFTING_LR.exists():
        in_conv = False
        for line in crafting_xml.splitlines():
            if "<array name=\"loadresource_conversationlists\">" in line:
                in_conv = True
                continue
            if in_conv:
                if "</array>" in line:
                    break
                if "<item>" in line:
                    loadresources.append(line)
    loadresources.extend(loadresource_conversationlists)
    loadresources.append("        <item>@raw/conversationlist_jail</item>")
    loadresources.append("    </array>\n")

    loadresources.append("    <array name=\"loadresource_quests\">")
    if CRAFTING_LR.exists():
        in_q = False
        for line in crafting_xml.splitlines():
            if "<array name=\"loadresource_quests\">" in line:
                in_q = True
                continue
            if in_q:
                if "</array>" in line:
                    break
                if "<item>" in line:
                    loadresources.append(line)
    loadresources.extend(loadresource_quests)
    loadresources.append("    </array>")
    loadresources.append(LOADRESOURCES_FOOTER)
    (OUTPUT_VALUES / "loadresources.xml").write_text(
        "\n".join(loadresources), encoding="utf-8"
    )

# ============================================================
# SUMMARY
# ============================================================

print("===================================================")
print(" jasia2: crafting + faction generation complete")
print("===================================================")
print("Factions:", len(FACTIONS))
print("Pickpocket droplists:", len(PICKPOCKET_DROPLISTS))
print("Jail conversations:", len(JAIL_CONVERSATIONS))
print("Generated:")
print("  itemlist_faction_*.json")
print("  monsterlist_faction_*.json")
print("  droplists_faction_*.json")
print("  conversationlist_faction_*.json")
print("  questlist_faction_*.json")
print("  faction_*.tmx")
print("  jail.tmx")
print("  conversationlist_jail.json")
print("  droplists_pickpocket.json")
print("  values/loadresources.xml (merged with crafting)")
print("===================================================")


