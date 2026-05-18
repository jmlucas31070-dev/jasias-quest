#!/usr/bin/env python3
# jasia1.py — combined castle + holiday generator (Search for Sunny, That Time of Year, haunted dungeons, towers)

import json
import os
import random
import urllib.request
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

from at_format import write_json

OUTPUT_RAW = "./raw"
OUTPUT_VALUES = "./values"
OUTPUT_XML = Path("./xml")
ROOT = Path(".")
TMX_TEMPLATE = ROOT / "template.tmx"
TMX_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/"
    "AndorsTrailRelease/andors-trail/"
    "refs/heads/master/AndorsTrail/res/xml/template.tmx"
)

TILE = 32
MAP_W = 30
MAP_H = 30

os.makedirs(OUTPUT_RAW, exist_ok=True)
os.makedirs(OUTPUT_VALUES, exist_ok=True)
os.makedirs(OUTPUT_XML, exist_ok=True)

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
        <item>@raw/actorconditions_sunny</item>
        <item>@raw/actorconditions_holiday</item>
    </array>

    <array name="loadresource_conversationlists">
        <item>@raw/conversationlist_castle</item>
        <item>@raw/conversationlist_town</item>
        <item>@raw/conversationlist_sunny</item>
        <item>@raw/conversationlist_holiday</item>
        <item>@raw/conversationlist_horror</item>
        <item>@raw/conversationlist_tower</item>
    </array>

    <array name="loadresource_quests">
        <item>@raw/questlist_castle</item>
        <item>@raw/questlist_sunny</item>
        <item>@raw/questlist_holiday</item>
        <item>@raw/questlist_horror</item>
        <item>@raw/questlist_tower</item>
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
        <item>@raw/droplists_castle_blacksmith</item>
        <item>@raw/droplists_castle_alchemist</item>
        <item>@raw/droplists_psychotic_mage</item>
        <item>@raw/droplists_horror</item>
        <item>@raw/droplists_tower</item>
    </array>

    <array name="loadresource_items">
        <item>@raw/itemlist_armor</item>
        <item>@raw/itemlist_shop</item>
        <item>@raw/itemlist_weapon</item>
        <item>@raw/itemlist_potions</item>
        <item>@raw/itemlist_quest</item>
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
        <item>@raw/itemlist_holiday</item>
        <item>@raw/itemlist_horror</item>
        <item>@raw/itemlist_tower</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_castle</item>
        <item>@raw/monsterlist_town</item>
        <item>@raw/monsterlist_drow_astral</item>
        <item>@raw/monsterlist_drow_base</item>
        <item>@raw/monsterlist_drow_electric</item>
        <item>@raw/monsterlist_drow_fire</item>
        <item>@raw/monsterlist_drow_light</item>
        <item>@raw/monsterlist_drow_shadow</item>
        <item>@raw/monsterlist_drow_smoke</item>
        <item>@raw/monsterlist_drow_stone</item>
        <item>@raw/monsterlist_dragon</item>
        <item>@raw/monsterlist_holiday</item>
        <item>@raw/monsterlist_horror</item>
        <item>@raw/monsterlist_tower</item>
    </array>

</resources>
"""

# ============================================================
# DATA TABLES
# ============================================================

CASTLE_NPC_TYPES = [
    "Castle Guard", "Royal Knight", "Court Wizard", "Dungeon Keeper", "Royal Archer",
    "Castle Cook", "Stable Master", "Royal Priest", "Castle Blacksmith", "Royal Advisor",
    "Castle Servant", "Treasury Guard", "Gate Watchman", "Royal Captain", "Castle Scout",
    "Royal Messenger", "Barracks Soldier", "Royal Scribe", "Castle Alchemist", "Elite Knight",
    "Castle Butler", "Royal Champion", "Castle Hunter", "Training Master", "Royal Duelist"
]

TOWN_NPC_TYPES = [
    "Villager", "Merchant", "Blacksmith", "Farmer", "Innkeeper",
    "Hunter", "Traveler", "Guard", "Baker", "Tailor",
    "Miner", "Lumberjack", "Priest", "Herbalist", "Fisherman",
    "Scholar", "Stable Keeper", "Cook", "Messenger", "Carpenter",
    "Jeweler", "Tavern Bard", "Town Watchman", "Street Vendor", "Apprentice"
]

WEAPON_TYPES = [
    "Knife", "Sword", "Club", "Staff", "Mace",
    "Hammer", "Spear", "Dagger", "Battle Axe", "Longsword",
    "Shortsword", "Warhammer", "Halberd", "Flail", "Scythe",
    "Rapier", "Claymore", "Morningstar", "Crossbow", "Bow"
]

WEAPON_PREFIXES = [
    "Iron", "Steel", "Golden", "Ancient", "Royal",
    "Heavy", "Sharp", "Battle", "Knight", "Dark",
    "Silver", "Bronze", "Enchanted", "Runed", "Savage"
]

ARMOR_PREFIXES = [
    "Iron", "Steel", "Royal", "Golden", "Knight",
    "Heavy", "Blessed", "Ancient", "Runed", "Dark",
    "Silver", "Bronze", "Guardian", "Defender", "Battle"
]

SHOP_ITEMS = [
    "Torch", "Rope", "Bread", "Apple", "Health Potion",
    "Mana Potion", "Lockpick", "Camping Kit", "Lantern", "Fishing Rod",
    "Map", "Compass", "Bandage", "Arrow Bundle", "Water Flask",
    "Pickaxe", "Hammer", "Cooking Pot", "Traveler Boots", "Gloves",
    "Cape", "Tent", "Magic Scroll", "Herbs", "Gemstone",
    "Silver Ring", "Backpack", "Oil Flask", "Spyglass", "Needle Kit",
    "Book", "Feather Pen", "Bottle", "Wooden Shield", "Traveler Hat",
    "Fur Cloak", "Knife", "Ale Mug", "Dried Meat", "Cheese Wheel",
    "Fruit Basket", "Lucky Charm", "Bell", "Sleeping Bag", "Bone Necklace",
    "Iron Ore", "Coal Sack", "Leather Strap", "Travel Journal", "Magic Crystal"
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
# DROW RACES
# ============================================================

DROW_RACES = ["base", "shadow", "light", "smoke", "electric", "fire", "stone", "astral" ]

# ============================================================
# DROW NPC TYPES
# ============================================================

DROW_CLASSES = [
    "Assassin", "Priestess", "Shadowblade", "Scout", "Warlock",
    "Guard", "Beastmaster", "Spider Tamer", "Witch", "Hunter",
    "Raider", "Sorcerer", "Executioner", "Champion", "Knight",
    "Mage", "Archer", "Poisoner", "Dark Cleric", "Royal Guard",
    "Crypt Stalker", "Nightblade", "Tunnel Scout", "Webspinner", "Dark Summoner"
]

# ============================================================
# WEAPON DATA
# ============================================================

DROW_WEAPON_TYPES = ["Knife", "Sword", "Club", "Staff", "Mace", "Dagger", "Spear", "Whip", "Crossbow"]

DROW_WEAPON_PREFIXES = ["Dark", "Shadow", "Venom", "Night", "Ancient", "Poison", "Moon", "Blood", "Spider", "Void"]

# ============================================================
# ARMOR SLOTS
# ============================================================

DROW_ARMOR_SLOTS = [
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

DRAGON_AGES = ["Wyrmling", "Youngster", "Adult", "Elder", "Ancient"]

DRAGON_TYPES = [
    "Black", "Blue", "Green", "White", "Red", "Chromatic",
    "Brass", "Bronze", "Copper", "Silver", "Gold", "Platinum"
]

# ============================================================
# DRAGON SPELLS
# ============================================================

DRAGON_SPELLS = [
    "Flame Breath", "Frost Breath", "Lightning Storm", "Poison Cloud", "Meteor Strike",
    "Arcane Roar", "Shadow Flame", "Crystal Breath", "Thunder Breath", "Inferno Blast",
    "Acid Spray", "Divine Roar", "Storm Call", "Earthquake", "Dragon Fear",
    "Void Breath", "Celestial Fire", "Mana Burst", "Soul Burn", "Ancient Wrath",
    "Plasma Surge", "Astral Nova", "Death Breath", "Skyfire", "Dragon Rage"
]

# ============================================================
# DRAGON TREASURE
# ============================================================

DRAGON_TREASURE = [
    "Dragon Scale", "Dragon Fang", "Ancient Coin", "Golden Crown", "Ruby Necklace",
    "Emerald Ring", "Crystal Orb", "Dragon Egg", "Treasure Chest", "Ancient Relic",
    "Silver Chalice", "Royal Banner", "Enchanted Gem", "Dragon Claw", "Ancient Scroll",
    "Sacred Idol", "Golden Statue", "Dragon Heart", "Mystic Rune", "Magic Crystal",
    "Ancient Sword", "Royal Armor", "Treasure Map", "Dragon Eye", "Ancient Artifact"
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

def random_drow_damage():
    low = random.randint(5, 25)
    high = low + random.randint(5, 30)
    return low, high

def download_template():
    if TMX_TEMPLATE.exists():
        return
    print("Downloading template.tmx...")
    urllib.request.urlretrieve(TMX_TEMPLATE_URL, TMX_TEMPLATE)
    print("Downloaded template.tmx")

# ============================================================
# TMX / MAP HELPERS
# ============================================================

_object_id = 1

def next_object_id():
    global _object_id
    oid = _object_id
    _object_id += 1
    return oid

def reset_object_ids():
    global _object_id
    _object_id = 1

def tile_xy(tx, ty):
    return tx * TILE, ty * TILE

def add_properties(parent, props):
    if not props:
        return
    properties = ET.SubElement(parent, "properties")
    for name, value in props.items():
        if value is None:
            continue
        ET.SubElement(properties, "property", name=name, value=str(value))

def add_mapchange(mapevents, name, tx, ty, tw, th, target_map, place):
    obj = ET.SubElement(
        mapevents,
        "object",
        name=name,
        type="mapchange",
        id=str(next_object_id()),
        x=str(tx),
        y=str(ty),
        width=str(tw),
        height=str(th),
    )
    add_properties(obj, {"map": target_map, "place": place})

def add_spawn(group, name, tx, ty, spawngroup, phrase=None, extra=None):
    obj = ET.SubElement(
        group,
        "object",
        name=name,
        type="spawn",
        id=str(next_object_id()),
        x=str(tx),
        y=str(ty),
        width=str(TILE),
        height=str(TILE),
    )
    props = {"spawngroup": spawngroup}
    if phrase:
        props["phrase"] = phrase
    if extra:
        props.update(extra)
    add_properties(obj, props)

def add_key(group, name, tx, ty, phrase, extra=None):
    obj = ET.SubElement(
        group,
        "object",
        name=name,
        type="key",
        id=str(next_object_id()),
        x=str(tx),
        y=str(ty),
        width=str(TILE),
        height=str(TILE),
    )
    props = {"phrase": phrase}
    if extra:
        props.update(extra)
    add_properties(obj, props)

def opposite_place(direction):
    return {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]

def edge_mapchange(direction):
    mid = 14
    if direction == "north":
        return (mid * TILE, 0, TILE * 2, TILE)
    if direction == "south":
        return (mid * TILE, (MAP_H - 1) * TILE, TILE * 2, TILE)
    if direction == "west":
        return (0, mid * TILE, TILE, TILE * 2)
    return ((MAP_W - 1) * TILE, mid * TILE, TILE, TILE * 2)

def build_map_tmx(map_id, links, spawns=None, keys=None, extra_groups=None):
    """Create one TMX from template.tmx with mapchanges and optional spawns/keys."""
    reset_object_ids()
    root = deepcopy(template_root)
    mapevents = None
    for layer in root.findall("objectgroup"):
        if layer.get("name") == "Mapevents":
            mapevents = layer
            break
    if mapevents is None:
        mapevents = ET.SubElement(root, "objectgroup", name="Mapevents", width=str(MAP_W), height=str(MAP_H))

    for direction, target in links.items():
        if not target:
            continue
        x, y, w, h = edge_mapchange(direction)
        add_mapchange(mapevents, f"to_{target}_{direction}", x, y, w, h, target, opposite_place(direction))

    spawn_layer = None
    keys_layer = None
    for layer in root.findall("objectgroup"):
        if layer.get("name") == "Spawn":
            spawn_layer = layer
        if layer.get("name") == "Keys":
            keys_layer = layer

    if spawns:
        for idx, spawn in enumerate(spawns):
            layer = spawn_layer
            if spawn.get("layer") == "named":
                layer_name = spawn.get("layer_name", f"Spawn_{map_id}")
                layer = None
                for og in root.findall("objectgroup"):
                    if og.get("name") == layer_name:
                        layer = og
                        break
                if layer is None:
                    layer = ET.SubElement(root, "objectgroup", name=layer_name, color="#dddd00")
            elif spawn.get("layer") == "custom":
                layer_name = spawn["layer_name"]
                layer = None
                for og in root.findall("objectgroup"):
                    if og.get("name") == layer_name:
                        layer = og
                        break
                if layer is None:
                    layer = ET.SubElement(root, "objectgroup", name=layer_name, color=spawn.get("color", "#dddd00"))
            tx, ty = spawn.get("pos", (4 + (idx % 5) * 2, 6 + (idx // 5) * 2))
            add_spawn(
                layer,
                spawn.get("name", spawn["id"]),
                *tile_xy(tx, ty),
                spawn["id"],
                spawn.get("phrase"),
                spawn.get("extra"),
            )

    if keys:
        for idx, key in enumerate(keys):
            layer = keys_layer
            if key.get("layer") == "custom":
                layer_name = key["layer_name"]
                layer = None
                for og in root.findall("objectgroup"):
                    if og.get("name") == layer_name:
                        layer = og
                        break
                if layer is None:
                    layer = ET.SubElement(root, "objectgroup", name=layer_name, color=key.get("color", "#ffaa00"))
            tx, ty = key.get("pos", (4 + idx * 2, 10))
            add_key(layer, key["name"], *tile_xy(tx, ty), key["phrase"], key.get("extra"))

    if extra_groups:
        for group_name, objects in extra_groups.items():
            group = ET.SubElement(root, "objectgroup", name=group_name, color="#aaccff")
            for obj in objects:
                if obj["type"] == "spawn":
                    tx, ty = obj.get("pos", (8, 8))
                    add_spawn(group, obj["name"], *tile_xy(tx, ty), obj["id"], obj.get("phrase"), obj.get("extra"))
                elif obj["type"] == "key":
                    tx, ty = obj.get("pos", (8, 8))
                    add_key(group, obj["name"], *tile_xy(tx, ty), obj["phrase"], obj.get("extra"))

    ET.indent(root)
    tree = ET.ElementTree(root)
    tree.write(OUTPUT_XML / f"{map_id}.tmx", encoding="utf-8", xml_declaration=True)

def grid_links(grid, extra_links=None):
    """Build N/E/S/W link dicts for a 2D grid of map ids (None = no link)."""
    rows = len(grid)
    cols = max(len(row) for row in grid) if grid else 0
    padded = [row + [None] * (cols - len(row)) for row in grid]
    result = {}
    for r, row in enumerate(padded):
        for c, map_id in enumerate(row):
            if not map_id:
                continue
            links = {}
            if r > 0 and padded[r - 1][c]:
                links["north"] = padded[r - 1][c]
            if r + 1 < rows and padded[r + 1][c]:
                links["south"] = padded[r + 1][c]
            if c > 0 and row[c - 1]:
                links["west"] = row[c - 1]
            if c + 1 < cols and row[c + 1]:
                links["east"] = row[c + 1]
            if extra_links and map_id in extra_links:
                links.update(extra_links[map_id])
            result[map_id] = links
    return result

# ============================================================
# MAP LAYOUTS
# ============================================================

CASTLE_MAIN_GRID = [
    ["castle_garden", "castle_waiting", "castle_throne", "castle_workroom"],
    ["castle_kitchen", "castle_inner", "castle_dining", "castle_bedroom"],
    ["castle_library", "castle_center", "castle_trophy", "sunny_bedroom"],
    ["home", "castle_hall", "castle_hall_s", "castle_hall_se"],
    ["castle_hall_sw", "castle_entry", "castle_guest", "castle_staff"],
]

CASTLE_UPPER_GRID = [
    ["castle_northwest", "castle_north", "castle_northeast"],
    ["castle_west", "castle_top", "castle_east"],
    ["castle_southwest", "castle_south", "castle_southeast"],
]

CASTLE_LOWER_GRID = [
    [None, "castle_warden", None],
    ["castle_armory", "castle_lower", "castle_guards"],
    ["castle_cell_nw", "castle_cells_n", "castle_cell_ne"],
    ["castle_cell_w", "castle_cells", "castle_cell_e"],
    ["castle_cell_sw", "castle_cells_s", "castle_cell_se"],
    [None, "castle_cell_s", None],
]

DROW_LAIR_GRID = [
    ["drow_weaponer", "drow_cave_nw", "drow_cave_n", "drow_cave_ne", "drow_armorer"],
    ["drow_shaman", "drow_cave_w", "drow_cave", "drow_cave_e", "drow_chief"],
    ["drow_family", "drow_cave_sw", "drow_cave_s", "drow_cave_se", "drow_alchemist"],
]

DROW_TUNNEL_GRID = [
    ["drow_tunnel_nw", "drow_tunnel_n", "drow_tunnel_ne"],
    ["drow_tunnel_w", "drow_tunnel", "drow_tunnel_e", "drow_end"],
    ["drow_tunnel_sw", "drow_tunnel_s", "drow_tunnel_se"],
    [None, "drow_entry", "drow_shop"],
]

DRAGON_GRID = [
    ["dragon_platinum", "dragon_throne", "dragon_chromatic"],
    ["dragon_gold", "dragon_cave_5", "dragon_red"],
    ["dragon_silver", "dragon_cave_4", "dragon_blue"],
    ["dragon_copper", "dragon_cave_3", "dragon_black"],
    ["dragon_bronze", "dragon_cave_2", "dragon_white"],
    ["dragon_brass", "dragon_cave_1", "dragon_yellow"],
    ["dragon_baby_good", "dragon_cave_s", "dragon_baby_evil"],
    [None, "dragon_entry", None],
]

RING_GRID = [
    ["ring_woods", "ring_village", "ring_lake"],
    ["ring_entry", "ring_clearing", "ring_mountain"],
    [None, "ring_rocket", None],
]

MOON_COLORS = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

HAUNTED_LOCATIONS = [
    "haunted_house", "haunted_mansion", "haunted_asylum",
    "haunted_prison", "haunted_crypt", "haunted_mausoleum", "haunted_graveyard",
]

LLOTH_ITEMS = [
    "lloth_reagent_shadow", "lloth_reagent_blood", "lloth_reagent_moon",
    "lloth_reagent_spider", "lloth_reagent_void", "lloth_reagent_silk",
    "lloth_reagent_ash", "lloth_reagent_venom", "lloth_reagent_tear",
]

# ============================================================
# HOLIDAY + EVENT + HORROR + TOWER DATA (from holiday.py)
# ============================================================

HOLIDAYS = {
    "new_years": [
        "Firework Bundle", "Golden Champagne", "Celebration Horn", "Lucky Coin", "Party Mask",
        "Clock Pendant", "Sparkler Wand", "Festive Banner", "New Year Cake", "Crystal Confetti",
        "Silver Goblet", "Fortune Scroll", "Midnight Lantern", "Moonfire Rocket", "Lucky Ribbon",
        "Joyful Drum", "Celestial Crown", "Starburst Orb", "Resolution Journal", "Golden Watch",
        "Festival Charm", "Victory Medal", "Sunrise Crystal", "Holiday Trumpet", "Prosperity Ring",
    ],
    "easter": [
        "Painted Egg", "Golden Bunny", "Spring Basket", "Chocolate Rabbit", "Flower Crown",
        "Pastel Ribbon", "Easter Candle", "Sunrise Egg", "Blooming Rose", "Spring Lantern",
        "Carrot Pie", "Sacred Lily", "Blessed Basket", "Honey Cookie", "Rabbit Charm",
        "Spring Bell", "Pasture Necklace", "Butterfly Brooch", "Daisy Bracelet", "Tulip Ring",
        "Eggshell Pendant", "Spring Cloak", "Joy Bouquet", "Festival Bonnet", "Bloom Pendant",
    ],
    "fourth_of_july": [
        "Patriot Banner", "Liberty Torch", "Firecracker Box", "Freedom Medal", "Festival Drum",
        "Rocket Firework", "Star Shield", "Liberty Ring", "Celebration Cape", "Freedom Flag",
        "Spark Fountain", "Patriot Necklace", "Honor Badge", "Festival Lantern", "Glory Ribbon",
        "Red White Cloak", "Blue Ember", "Victory Charm", "Liberty Crown", "Festival Gloves",
        "Star Pendant", "Skyfire Orb", "Rocket Tube", "Freedom Bracelet", "Celebration Staff",
    ],
    "halloween": [
        "Pumpkin Lantern", "Witch Hat", "Ghost Cloak", "Candy Basket", "Spider Ring",
        "Bat Pendant", "Haunted Doll", "Skull Mask", "Night Candle", "Bone Wand",
        "Cursed Pumpkin", "Black Rose", "Phantom Bell", "Shadow Orb", "Moonlit Charm",
        "Ghoul Lantern", "Specter Cloak", "Spider Brooch", "Raven Feather", "Dark Apple",
        "Tomb Key", "Soul Candle", "Crypt Pendant", "Monster Fang", "Necro Tome",
    ],
    "thanksgiving": [
        "Harvest Basket", "Golden Turkey", "Autumn Leaf", "Cornucopia", "Pumpkin Pie",
        "Harvest Lantern", "Family Necklace", "Warm Blanket", "Autumn Ring", "Festival Bread",
        "Harvest Bell", "Thankful Charm", "Corn Necklace", "Wooden Goblet", "Maple Cloak",
        "Autumn Crown", "Festival Mug", "Harvest Gloves", "Golden Wheat", "Oak Pendant",
        "Harvest Drum", "Warm Candle", "Blessing Scroll", "Turkey Feather", "Autumn Crystal",
    ],
    "christmas": [
        "Candy Cane", "Santa Hat", "Snow Globe", "Christmas Bell", "Winter Cloak",
        "Holiday Stocking", "Frost Lantern", "Silver Snowflake", "Toy Soldier", "Holiday Ribbon",
        "Christmas Candle", "Frozen Ornament", "Reindeer Charm", "Yule Log", "Winter Crown",
        "Gift Box", "Holiday Mittens", "Snow Crystal", "Elf Boots", "North Star Ring",
        "Jingle Pendant", "Holiday Drum", "Ice Bell", "Mistletoe Pendant", "Frostfire Orb",
    ],
    "birthday": [
        "Birthday Cake", "Party Balloon", "Gift Ribbon", "Celebration Hat", "Birthday Candle",
        "Golden Present", "Festival Necklace", "Party Horn", "Celebration Cloak", "Joy Bracelet",
        "Birthday Bell", "Candy Necklace", "Party Lantern", "Friendship Ring", "Gift Basket",
        "Celebration Gloves", "Birthday Medal", "Confetti Orb", "Golden Cake Slice", "Party Mask",
        "Friendship Charm", "Birthday Rose", "Festival Crown", "Spark Candle", "Party Crystal",
    ],
    "graduation": [
        "Graduate Cap", "Honor Medal", "Diploma Scroll", "Scholar Ring", "Wisdom Pendant",
        "Achievement Trophy", "Knowledge Tome", "Golden Feather", "Academic Cloak", "Victory Ribbon",
        "Scholar Gloves", "Graduation Bell", "Mastery Crown", "Achievement Badge", "Honor Bracelet",
        "Wisdom Orb", "Learning Crystal", "Graduate Lantern", "Study Journal", "Knowledge Charm",
        "Scholar Staff", "Honor Banner", "Success Medal", "Academic Brooch", "Victory Crown",
    ],
    "wedding": [
        "Wedding Ring", "White Rose", "Ceremony Candle", "Love Pendant", "Bride Veil",
        "Golden Bouquet", "Marriage Scroll", "Silver Goblet", "Sacred Ribbon", "Wedding Crown",
        "Unity Bracelet", "Ceremony Lantern", "Heart Charm", "Celebration Cloak", "Love Crystal",
        "Golden Promise", "Blessing Bell", "White Gloves", "Wedding Necklace", "Rose Crown",
        "Sacred Flame", "Love Brooch", "Marriage Seal", "Heart Ring", "Ceremony Orb",
    ],
    "funeral": [
        "Black Rose", "Memorial Candle", "Grief Pendant", "Silver Cross", "Funeral Veil",
        "Memory Ring", "Sacred Ashes", "Prayer Scroll", "Soul Lantern", "Remembrance Charm",
        "Silent Bell", "Mourning Cloak", "Cemetery Flower", "Spirit Candle", "Grave Token",
        "Blessed Ribbon", "Angel Feather", "Remembrance Medal", "Funeral Gloves", "Silent Rose",
        "Soul Crystal", "Prayer Beads", "Memorial Bracelet", "Peace Pendant", "Funeral Crown",
    ],
}

EVENTS = {
    "spring_festival": [
        "Bloom Crown", "Rain Charm", "Meadow Ribbon", "Butterfly Wing", "Dew Crystal",
        "Green Lantern", "Flower Wreath", "Spring Flute", "Sunpetal", "River Stone",
        "Nest Egg", "Blossom Cake", "Wind Chime", "Grass Bracelet", "Pollen Orb",
        "Seed Pouch", "Robin Feather", "Moss Pendant", "Fern Cloak", "Hive Honey",
        "Sprout Staff", "Rainbow Shard", "Brook Token", "Thorn Rose", "Verdant Bell",
    ],
    "summer_solstice": [
        "Sun Crown", "Heat Ruby", "Solstice Flame", "Beach Shell", "Solar Medallion",
        "Wave Pendant", "Sand Dollar", "Tidal Charm", "Bonfire Ash", "Longday Candle",
        "Goldleaf", "Surf Token", "Ember Wine", "Sunflare", "Horizon Ring",
        "Dune Crystal", "Kite String", "Lagoon Pearl", "Blaze Feather", "Midsummer Mask",
        "Scorch Orb", "Palm Frond", "Gull Feather", "Sunthread", "Solstice Drum",
    ],
    "harvest_moon": [
        "Moon Wheat", "Lantern Gourd", "Harvest Sigil", "Cider Mug", "Sheaf Bundle",
        "Amber Moon", "Scarecrow Hat", "Field Bell", "Granary Key", "Pumpkin Ale",
        "Maize Charm", "Twilight Husk", "Reaper Scythe Mini", "Hay Crown", "Root Pendant",
        "Cobalt Night", "Grain Mother", "Stubble Cloak", "Owl Token", "Furrow Map",
        "Moon Cider", "Stalk Wand", "Barn Sigil", "GoldSheaf", "Harvest Horn",
    ],
    "founders_day": [
        "Founders Medal", "Liberty Quill", "Town Banner", "Bronze Key", "Charter Scroll",
        "Bell of Union", "Cobblestone", "Guild Seal", "Market Coin", "Bridge Stone",
        "Council Ring", "Hearth Token", "Flag Pin", "Archive Wax", "Stone Tablet",
        "Hall Lantern", "Treaty Ink", "Plaza Flower", "Guard Badge", "Well Charm",
        "Clock Tower Gear", "Foundry Nail", "Harbor Rope", "Mill Flour", "Founders Cake",
    ],
}

HORROR_LOCATION_MONSTERS = {
    "haunted_house": ["Ghost", "Phantom", "Cursed Child", "Possessed Doll", "Haunted Butler"],
    "haunted_mansion": ["Spectral Noble", "Ghost Baron", "Phantom Maid", "Shadow Knight", "Cursed Duchess"],
    "haunted_mausoleum": ["Bone Priest", "Ancient Wraith", "Tomb Guardian", "Soul Keeper", "Crypt Specter"],
    "haunted_crypt": ["Crypt Ghoul", "Bone Horror", "Dark Skeleton", "Tomb Spider", "Crypt Phantom"],
    "haunted_graveyard": ["Zombie", "Restless Spirit", "Grave Keeper", "Cemetery Ghoul", "Night Stalker"],
    "haunted_prison": ["Ghost Prisoner", "Executioner", "Chain Specter", "Prison Shade", "Cursed Warden"],
    "haunted_asylum": ["Mad Spirit", "Insane Patient", "Dark Doctor", "Twisted Nurse", "Asylum Beast"],
}

HORROR_DROP_NAMES = [
    "Haunted Bone", "Cursed Lantern", "Dark Crystal", "Soul Fragment", "Ancient Skull",
    "Necro Dust", "Ghost Cloth", "Phantom Ring", "Spirit Orb", "Shadow Fang",
]

MAGE_TOWER_COLORS = ["red", "blue", "green", "violet"]
CLERIC_CRYSTAL_TYPES = ["ruby", "sapphire", "emerald", "diamond"]
DRUID_ORE_TYPES = ["iron", "copper", "gold", "mithril"]
TOWER_LEVELS = 5
TOWER_BOSS_LEVEL = 6
BOX_CORNERS = ["nw", "ne", "sw", "se"]

TOWER_RANKS = {
    "mage": ["Medium", "Seer", "Conjurer", "Theurgist", "Thaumaturgist", "Archmage"],
    "cleric": ["Acolyte", "Adept", "Priestess", "Curate", "Bishop", "Hierophant"],
    "druid": ["Aspirant", "Ovate", "Initiate", "Druid", "Archdruid", "Great Druid"],
}

GRAND_WIZARD_QUOTES = [
    "The towers test every guild in turn.",
    "Magic without wisdom is a candle in the wind.",
    "Clerics heal what mages break.",
    "Druids remember what others forget.",
    "Only the worthy reach my chamber.",
]

# ============================================================
# QUEST / CONVERSATION CONTAINERS
# ============================================================

CONVERSATIONS = []
QUESTS = []
ACTORCONDITIONS_QUEST = []
STORY_NPCS = []
POTION_ITEMS = []
QUEST_ITEMS = []
HOLIDAY_CONVERSATIONS = []
HOLIDAY_QUESTS = []
ACTORCONDITIONS_HOLIDAY = []
HORROR_CONVERSATIONS = []
HORROR_QUESTS = []
TOWER_CONVERSATIONS = []
TOWER_QUESTS = []
holiday_items = []
holiday_monsters = []
horror_items = []
horror_monsters = []
horror_droplists = []
tower_items = []
tower_monsters = []
tower_droplists = []

def conv(cid, message, replies=None, rewards=None):
    entry = {"id": cid, "message": message}
    if replies:
        entry["replies"] = replies
    if rewards:
        entry["rewards"] = rewards
    CONVERSATIONS.append(entry)

def quest_stage(progress, log_text, finishes=0, reward_exp=0, reward_gold=0):
    stage = {"progress": progress, "logText": log_text, "finishesQuest": finishes}
    if reward_exp:
        stage["rewardExperience"] = reward_exp
    if reward_gold:
        stage["rewardGold"] = reward_gold
    return stage

def qp_reward(quest_id, value):
    return {"rewardType": "questProgress", "rewardID": quest_id, "value": value}

def qp_require(quest_id, value):
    return {"requireType": "questProgress", "requireID": quest_id, "value": str(value)}

def mapchange_reward(target_map, place):
    return {"rewardType": "mapchange", "rewardID": place, "mapName": target_map}

def activate_group_reward(map_name, group_name):
    return {"rewardType": "activateMapObjectGroup", "rewardID": group_name, "mapName": map_name}

def deactivate_group_reward(map_name, group_name):
    return {"rewardType": "deactivateMapObjectGroup", "rewardID": group_name, "mapName": map_name}

def give_item_reward(item_id, count=1):
    return {"rewardType": "giveItem", "rewardID": item_id, "value": count}

def ac_apply(condition_id):
    return {"rewardType": "actorCondition", "rewardID": condition_id, "value": 999}

def ac_remove(condition_id):
    return {"rewardType": "actorCondition", "rewardID": condition_id, "value": -99}

def hconv(cid, message, replies=None, rewards=None):
    entry = {"id": cid, "message": message}
    if replies:
        entry["replies"] = replies
    if rewards:
        entry["rewards"] = rewards
    HOLIDAY_CONVERSATIONS.append(entry)

def friendly_npc(npc_id, name, conversation=None, questlist=None, shop=None, droplist=None, icon="npc_human:1"):
    entry = {"id": npc_id, "name": name, "iconID": icon, "spawnGroup": npc_id}
    if conversation:
        entry["conversation"] = conversation
    if questlist:
        entry["questlist"] = questlist
    if shop:
        entry["shop"] = shop
    if droplist:
        entry["droplist"] = droplist
    return entry

# ============================================================
# CREATE CASTLE NPCS
# ============================================================

def create_castle_npcs():
    for i in range(25):
        npc_type = CASTLE_NPC_TYPES[i]
        npc_id = f"castle_npc_{i+1}"
        low, high = random_damage()
        if npc_type == "Castle Blacksmith":
            castle_monsters.append(friendly_npc(
                npc_id, npc_type,
                conversation="conversationlist_castle",
                shop="itemlist_weapon",
                droplist="droplist_castle_blacksmith",
            ))
            continue
        if npc_type == "Castle Alchemist":
            castle_monsters.append(friendly_npc(
                npc_id, npc_type,
                conversation="conversationlist_castle",
                shop="itemlist_potions",
                droplist="droplist_castle_alchemist",
            ))
            continue
        npc = {
            "id": npc_id,
            "name": npc_type,
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(80, 400),
            "attackChance": random.randint(40, 85),
            "attackDamage": {"min": low, "max": high},
            "moveCost": random.randint(3, 8),
            "attackCost": random.randint(3, 8),
            "spawnGroup": "castle_npc",
            "faction": "castle",
            "conversation": "conversationlist_castle",
            "questlist": "questlist_castle",
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
            "attackCost": random.randint(3, 8),
            "spawnGroup": "town_npc",
            "faction": "town",
            "conversation": "conversationlist_town",
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
# HOLIDAY / HORROR / TOWER ASSETS
# ============================================================

def gift_item_id(kind, key, gift_name):
    return f"item_{kind}_{key}_{gift_name.lower().replace(' ', '_')}"

def create_holiday_horror_tower_assets():
    for kind, table in (("holiday", HOLIDAYS), ("event", EVENTS)):
        for key, gifts in table.items():
            host_id = f"npc_{key}"
            holiday_monsters.append(friendly_npc(
                host_id,
                key.replace("_", " ").title() + (" Host" if kind == "holiday" else " Herald"),
                "conversationlist_holiday",
                icon="npc_human:20",
            ))
            cond_id = f"{kind}_active_{key}"
            ACTORCONDITIONS_HOLIDAY.append({
                "id": cond_id,
                "name": f"Active: {key.replace('_', ' ').title()}",
                "iconID": ACTORCONDITION_ICON,
                "isNegative": 0,
            })
            for gift in gifts:
                iid = gift_item_id(kind, key, gift)
                holiday_items.append({
                    "id": iid,
                    "name": gift,
                    "iconID": ITEM_ICON,
                    "displaytype": "ordinary",
                    "hasManualPrice": 1,
                    "baseMarketCost": random.randint(50, 500),
                    "category": "misc",
                    "description": f"A special {key.replace('_', ' ')} gift.",
                })

    holiday_monsters.append(friendly_npc(
        "npc_timekeeper", "Timekeeper", "conversationlist_holiday", "questlist_holiday", icon="npc_human:19",
    ))
    holiday_monsters.append(friendly_npc(
        "npc_priest", "Priest", "conversationlist_horror", "questlist_horror", icon="npc_human:18",
    ))
    holiday_monsters.append(friendly_npc(
        "npc_grand_wizard", "Grand Wizard", "conversationlist_tower", "questlist_tower", icon="npc_human:17",
    ))

    for loc in HAUNTED_LOCATIONS:
        boss_id = f"boss_{loc}"
        trophy_id = f"quest_item_{loc}"
        horror_items.append({
            "id": trophy_id,
            "name": f"Trophy of {loc.replace('_', ' ').title()}",
            "iconID": ITEM_ICON,
            "displaytype": "quest",
            "category": "misc",
            "description": f"Proof the {loc.replace('_', ' ')} boss was defeated.",
        })
        droplist_id = f"droplist_{boss_id}"
        horror_droplists.append({
            "id": droplist_id,
            "items": [{"item": trophy_id, "quantity": {"min": 1, "max": 1}, "chance": "100"}],
        })
        low, high = random_damage()
        horror_monsters.append({
            "id": boss_id,
            "name": f"Lord of the {loc.replace('_', ' ').title()}",
            "iconID": MONSTER_ICON,
            "maxHP": random.randint(400, 900),
            "attackChance": random.randint(55, 90),
            "attackDamage": {"min": low + 15, "max": high + 30},
            "moveCost": random.randint(3, 7),
            "attackCost": random.randint(3, 7),
            "droplistID": droplist_id,
            "spawnGroup": boss_id,
            "faction": "haunted",
        })
        for i in range(20):
            names = HORROR_LOCATION_MONSTERS.get(loc, ["Spirit"])
            item_id = f"item_{loc}_drop_{i+1}"
            drop_id = f"droplist_{loc}_{i+1}"
            horror_items.append({
                "id": item_id,
                "name": random.choice(HORROR_DROP_NAMES),
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "hasManualPrice": 1,
                "baseMarketCost": random.randint(80, 800),
                "category": "misc",
                "description": f"A relic from {loc.replace('_', ' ')}.",
            })
            horror_droplists.append({
                "id": drop_id,
                "items": [{"item": item_id, "quantity": {"min": 1, "max": 1}, "chance": "100"}],
            })
            low, high = random_damage()
            horror_monsters.append({
                "id": f"monster_{loc}_{i+1}",
                "name": f"{random.choice(names)} of {loc.replace('_', ' ')}",
                "iconID": MONSTER_ICON,
                "maxHP": random.randint(60, 450),
                "attackChance": random.randint(40, 85),
                "attackDamage": {"min": low, "max": high},
                "moveCost": random.randint(3, 8),
                "attackCost": random.randint(3, 8),
                "droplistID": drop_id,
                "spawnGroup": f"haunt_{loc}",
                "faction": "haunted",
            })

    tower_specs = []
    for color in MAGE_TOWER_COLORS:
        tower_specs.append(("mage", color))
    for crystal in CLERIC_CRYSTAL_TYPES:
        tower_specs.append(("cleric", crystal))
    for ore in DRUID_ORE_TYPES:
        tower_specs.append(("druid", ore))

    for guild, variant in tower_specs:
        trophy_id = f"quest_item_tower_{guild}_{variant}"
        tower_items.append({
            "id": trophy_id,
            "name": f"{variant.title()} {guild.title()} Tower Sigil",
            "iconID": ITEM_ICON,
            "displaytype": "quest",
            "category": "misc",
            "description": f"Earned by defeating the {variant} {guild} tower boss.",
        })
        boss_id = f"boss_tower_{guild}_{variant}"
        drop_id = f"droplist_{boss_id}"
        tower_droplists.append({
            "id": drop_id,
            "items": [{"item": trophy_id, "quantity": {"min": 1, "max": 1}, "chance": "100"}],
        })
        ranks = TOWER_RANKS[guild]
        for level in range(1, TOWER_BOSS_LEVEL + 1):
            is_boss = level == TOWER_BOSS_LEVEL
            mid = boss_id if is_boss else f"monster_tower_{guild}_{variant}_{level}"
            name = ranks[min(level - 1, len(ranks) - 1)]
            low, high = random_damage()
            entry = {
                "id": mid,
                "name": f"{variant.title()} {name}",
                "iconID": MONSTER_ICON,
                "maxHP": random.randint(80, 200) + level * 80,
                "attackChance": random.randint(40, 85),
                "attackDamage": {"min": low + level * 2, "max": high + level * 5},
                "moveCost": random.randint(3, 8),
                "attackCost": random.randint(3, 8),
                "spawnGroup": f"tower_{guild}_{variant}",
                "faction": "tower",
            }
            if is_boss:
                entry["droplistID"] = drop_id
            tower_monsters.append(entry)

    for i in range(15):
        tower_items.append({
            "id": f"item_tower_loot_{i+1}",
            "name": random.choice(["Rusty Key", "Worn Scroll", "Crystal Shard", "Arcane Token"]),
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "hasManualPrice": 1,
            "baseMarketCost": random.randint(50, 400),
            "category": "misc",
            "description": "Found in a guild tower.",
        })

    for i, quote in enumerate(GRAND_WIZARD_QUOTES):
        TOWER_CONVERSATIONS.append({
            "id": f"conv_tower_quote_{i}",
            "message": quote,
            "replies": [{"text": "...", "nextPhraseID": "X"}],
        })

create_holiday_horror_tower_assets()

# ============================================================
# POTION SHOP (CASTLE ALCHEMIST)
# ============================================================

for i in range(25):
    POTION_ITEMS.append({
        "id": f"potion_{i+1}",
        "name": f"Castle {random.choice(['Health', 'Mana', 'Stamina', 'Cure', 'Antidote'])} Potion {i+1}",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "hasManualPrice": 1,
        "baseMarketCost": random.randint(25, 800),
        "category": "potion",
        "description": "A potion brewed in the royal castle laboratory.",
        "useEffect": {
            "increaseCurrentHP": {
                "min": 1,
                "max": random.randint(20, 120)
            }
        }
    })

# ============================================================
# STORY NPCS, QUESTS, CONVERSATIONS
# ============================================================

def build_story_content():
  # Actor conditions ---------------------------------------------------------
    ACTORCONDITIONS_QUEST.extend([
        {"id": "sunny_info_complete", "name": "Castle clues gathered", "iconID": ACTORCONDITION_ICON, "isNegative": 0},
        {"id": "lloth_ring_active", "name": "Lloth's ring activated", "iconID": ACTORCONDITION_ICON, "isNegative": 0},
        {"id": "all_moon_quests_done", "name": "Moon realms united", "iconID": ACTORCONDITION_ICON, "isNegative": 0},
        {"id": "sunny_blessed", "name": "Blessed by Sunny", "iconID": ACTORCONDITION_ICON, "isNegative": 0,
         "abilityEffect": {"increaseMaxHP": 50, "increaseAttackChance": 5}},
    ])

    STORY_NPCS.extend([
        friendly_npc("npc_sunny", "Sunny", "conversationlist_sunny", icon="npc_human:5"),
        friendly_npc("npc_ozzy", "Ozzy", "conversationlist_sunny", "questlist_sunny", icon="npc_human:6"),
        friendly_npc("npc_nymph", "Nymph", "conversationlist_sunny", icon="npc_human:7"),
        friendly_npc("npc_jasias_maid", "Jasia's Maid", "conversationlist_sunny", icon="npc_human:8"),
        friendly_npc("npc_castle_guard_tip", "Castle Guard", "conversationlist_sunny", "questlist_sunny", icon="npc_human:9"),
        friendly_npc("npc_swamp_witch", "Swamp Witch", "conversationlist_sunny", "questlist_sunny", icon="npc_human:10"),
        friendly_npc("npc_drow_shaman", "Drow Shaman", "conversationlist_sunny", "questlist_sunny", icon="npc_human:11"),
        friendly_npc("npc_lloth", "Lloth", "conversationlist_sunny", "questlist_sunny", icon="npc_human:12"),
        friendly_npc("npc_ring_guard", "Hybrid Drow Guard", "conversationlist_sunny", icon="npc_human:14"),
        friendly_npc("npc_drow_leader", "Drow Leader", "conversationlist_sunny", "questlist_sunny", icon="npc_human:15"),
    ])

    for color in MOON_COLORS:
        STORY_NPCS.append(friendly_npc(
            f"npc_moon_elder_{color}",
            f"{color.title()} Moon Elder",
            "conversationlist_sunny",
            "questlist_sunny",
            icon="npc_human:16",
        ))

    for i, item_id in enumerate(LLOTH_ITEMS):
        QUEST_ITEMS.append({
            "id": item_id,
            "name": f"Lloth Reagent {i+1}",
            "iconID": ITEM_ICON,
            "displaytype": "quest",
            "category": "misc",
            "description": "A rare component for Lloth's planar spell.",
        })

    QUEST_ITEMS.extend([
        {"id": "lloth_ring", "name": "Lloth's Ring", "iconID": ITEM_ICON, "displaytype": "ordinary",
         "category": "leftring", "description": "Teleports you back from the dragon realm when appeased.",
         "equipEffect": {"increaseArmor": 5}},
        {"id": "sunny_ring", "name": "Sunny's Tent Ring", "iconID": ITEM_ICON, "displaytype": "quest",
         "category": "misc", "description": "A ring Sunny enchanted before she vanished."},
        {"id": "mage_note", "name": "Mage's Note", "iconID": ITEM_ICON, "displaytype": "quest",
         "category": "misc", "description": "Hybrid drow guarding a tent by the dow mountain will let anyone wearing the ring pass."},
    ])

    # Main quest chain ---------------------------------------------------------
    QUESTS.append({
        "id": "quest_search_sunny",
        "name": "Search for Sunny",
        "showInLog": 1,
        "stages": [
            quest_stage(10, "Father Ozzy asked me to find Sunny.", 0, 50),
            quest_stage(50, "I spoke with Mother Nymph in the throne room.", 0, 100),
            quest_stage(100, "I gathered clues from the castle.", 0, 200),
            quest_stage(200, "A guard said Sunny sought the swamp witch.", 0, 150),
            quest_stage(300, "The swamp witch sent me to the drow shaman.", 0, 200),
            quest_stage(400, "Lloth demanded I settle the dragon dispute.", 0, 300),
            quest_stage(500, "Sunny became a demi-god and left a trail to her ring.", 0, 200),
            quest_stage(600, "I recovered Sunny's ring from the psychotic mage.", 0, 250),
            quest_stage(700, "The moon drow united and summoned Sunny.", 0, 400),
            quest_stage(1000, "Sunny has been found.", 1, 1000, 500),
        ],
    })

    for i in range(1, 26):
        qid = f"quest_castle_clue_{i}"
        QUESTS.append({
            "id": qid,
            "name": f"Castle Rumor {i}",
            "showInLog": 1,
            "stages": [quest_stage(100, f"I learned clue {i} about Sunny's disappearance.", 1, 25)],
        })

    QUESTS.append({
        "id": "quest_swamp_witch",
        "name": "Swamp Witch Inquiry",
        "showInLog": 1,
        "stages": [
            quest_stage(25, "The witch knows something (part 1).", 0, 30),
            quest_stage(50, "The witch knows something (part 2).", 0, 30),
            quest_stage(75, "The witch knows something (part 3).", 0, 30),
            quest_stage(100, "The witch pointed me toward the drow shaman.", 1, 100),
        ],
    })

    QUESTS.append({
        "id": "quest_lloth_items",
        "name": "Offerings for Lloth",
        "showInLog": 1,
        "stages": [quest_stage(100, "I gathered nine reagents for Lloth's spell.", 1, 200)],
    })

    for dragon in ["brass", "bronze", "copper", "silver", "gold", "yellow", "white", "black", "blue", "red"]:
        QUESTS.append({
            "id": f"quest_dragon_{dragon}",
            "name": f"Appease the {dragon.title()} Dragon",
            "showInLog": 1,
            "stages": [quest_stage(100, f"I completed the {dragon} dragon's trial.", 1, 150)],
        })

    QUESTS.extend([
        {"id": "quest_dragon_platinum", "name": "Platinum Dragon", "showInLog": 1,
         "stages": [quest_stage(100, "The platinum dragon is satisfied.", 1, 300)]},
        {"id": "quest_dragon_chromatic", "name": "Chromatic Dragon", "showInLog": 1,
         "stages": [quest_stage(100, "The chromatic dragon is satisfied.", 1, 300)]},
        {"id": "quest_dragon_council", "name": "Dragon Council", "showInLog": 1,
         "stages": [quest_stage(100, "The dragons convened and blessed Lloth's ring.", 1, 500)]},
        {"id": "quest_sunny_ring", "name": "Find Sunny's Ring", "showInLog": 1,
         "stages": [quest_stage(100, "I found Sunny's ring.", 1, 400)]},
    ])

    for color in MOON_COLORS:
        QUESTS.append({
            "id": f"quest_moon_{color}",
            "name": f"{color.title()} Moon Pact",
            "showInLog": 1,
            "stages": [quest_stage(100, f"The {color} moon elder acknowledged me.", 1, 100)],
        })

    QUESTS.append({
        "id": "quest_drow_leader",
        "name": "Ring Realm Pact",
        "showInLog": 1,
        "stages": [quest_stage(100, "The drow leader will summon Sunny.", 1, 200)],
    })

    # Conversations ------------------------------------------------------------
    conv("conv_npc_ozzy",
         "Jasia, your sister Sunny has vanished. Will you search for her?",
         [{"text": "I will find Sunny.", "nextPhraseID": "conv_ozzy_start",
           "rewards": [qp_reward("quest_search_sunny", 10)]},
          {"text": "I found Sunny.", "nextPhraseID": "conv_ozzy_complete",
           "requires": [qp_require("quest_search_sunny", 1000)]},
          {"text": "Not now.", "nextPhraseID": "X"}])

    conv("conv_ozzy_start",
         "Speak with your mother Nymph in the throne room. The servants may also know something.",
         [{"text": "I understand.", "nextPhraseID": "X"}])

    conv("conv_npc_nymph",
         "Your father waits with me in the throne room. Ask the castle folk what they saw.",
         [{"text": "I will ask around.", "nextPhraseID": "X",
           "rewards": [qp_reward("quest_search_sunny", 50)]}])

    conv("conv_jasias_maid",
         "My lady, your father wishes to speak with you. He waits in the throne room with your mother.",
         [{"text": "Thank you.", "nextPhraseID": "X"}])

    conv("key_start_block",
         "You should speak with the maid first.",
         [{"text": "...", "nextPhraseID": "X"}])

    for i in range(1, 26):
        conv(f"conv_castle_npc_{i}",
             f"I heard Sunny was studying magic lately. Clue {i}: she seemed troubled.",
             [{"text": "Tell me more.", "nextPhraseID": "X",
               "rewards": [qp_reward(f"quest_castle_clue_{i}", 100),
                          qp_reward("quest_search_sunny", 100)]}])

    for i in range(1, 51):
        hints = [
            "A wood elf girl matching Sunny's description passed through town.",
            "They say Sunny talked of drow magic and distant moons.",
            "Strange lights were seen near the swamp.",
        ]
        if i <= len(HAUNTED_LOCATIONS):
            loc = HAUNTED_LOCATIONS[i - 1]
            hints.append(
                f"A psychotic mage may be hiding near the {loc.replace('_', ' ')}."
            )
        reply = {"text": "Thanks.", "nextPhraseID": "X"}
        if i <= len(HAUNTED_LOCATIONS):
            reply["requires"] = [qp_require("quest_search_sunny", 500)]
        conv(f"conv_town_hint_{i}", random.choice(hints), [reply])

    conv("conv_castle_guard_tip",
         "After the castle interviews, I recall Sunny went to the Witch in the swamp.",
         [{"text": "The swamp witch?", "nextPhraseID": "X",
           "requires": [qp_require("quest_search_sunny", 100)],
           "rewards": [qp_reward("quest_search_sunny", 200)]}])

    for part, prog in [(1, 25), (2, 50), (3, 75), (4, 100)]:
        conv(f"conv_swamp_witch_{part}",
             f"The swamp witch shares vision {part} of four: Sunny sought the drow shaman.",
             [{"text": "Continue", "nextPhraseID": "X",
               "rewards": [qp_reward("quest_swamp_witch", prog),
                          qp_reward("quest_search_sunny", 300 if part == 4 else 0)]}])

    conv("conv_drow_shaman",
         "Sunny wished to speak with Lloth. Bring nine reagents and I will send you to her.",
         [{"text": "I have the reagents.", "nextPhraseID": "conv_lloth_send",
           "requires": [qp_require("quest_swamp_witch", 100)]},
          {"text": "Not yet.", "nextPhraseID": "X"}])

    conv("conv_lloth_send",
         "Go to Lloth.",
         [{"text": "...", "nextPhraseID": "X",
           "rewards": [mapchange_reward("lloth_realm", "south"),
                       qp_reward("quest_search_sunny", 400)]}])

    conv("conv_npc_lloth",
         "You amuse me, wood elf. Settle the dragon dispute and I will tell you of Sunny.",
         [{"text": "I accept.", "nextPhraseID": "X",
           "rewards": [give_item_reward("lloth_ring", 1),
                       qp_reward("quest_lloth_items", 100)]}])

    conv("conv_npc_lloth_after_dragons",
         "Sunny wanted drow form and magic. She cast a tent spell on a ring, lost it, and vanished.",
         [{"text": "Send me back.", "nextPhraseID": "X",
           "requires": [qp_require("quest_dragon_council", 100)],
           "rewards": [mapchange_reward("drow_cave", "north"),
                       qp_reward("quest_search_sunny", 500)]}])

    for dragon in ["brass", "bronze", "copper", "silver", "gold", "yellow", "white", "black", "blue", "red"]:
        conv(f"conv_dragon_{dragon}",
             f"The {dragon} dragon demands a tribute before the council.",
             [{"text": "I will help.", "nextPhraseID": "X",
               "rewards": [qp_reward(f"quest_dragon_{dragon}", 100)]}])

    conv("conv_dragon_platinum", "The platinum dragon watches the council.",
         [{"text": "Report progress.", "nextPhraseID": "X",
           "requires": [qp_require("quest_dragon_gold", 100), qp_require("quest_dragon_red", 100)],
           "rewards": [qp_reward("quest_dragon_platinum", 100)]}])

    conv("conv_dragon_chromatic", "The chromatic dragon judges all colors.",
         [{"text": "Report progress.", "nextPhraseID": "X",
           "requires": [qp_require("quest_dragon_platinum", 100)],
           "rewards": [qp_reward("quest_dragon_chromatic", 100),
                       qp_reward("quest_dragon_council", 100),
                       qp_reward("quest_search_sunny", 450)]}])

    for loc in HAUNTED_LOCATIONS:
        conv(f"conv_haunt_hint_{loc}",
             f"Travelers whisper the psychotic mage hides near the {loc.replace('_', ' ')}.",
             [{"text": "...", "nextPhraseID": "X"}])

    conv("conv_psychotic_mage", "You dare confront me?",
         [{"text": "Fight!", "nextPhraseID": "X"}])

    conv("conv_mage_note", "Hybrid drow guarding a tent by the dow mountain will let anyone wearing the ring pass.",
         [{"text": "...", "nextPhraseID": "X"}])

    conv("conv_ring_guard", "Show the ring if you wish to pass.",
         [{"text": "...", "nextPhraseID": "X",
           "requires": [{"requireType": "inventoryKeep", "requireID": "sunny_ring", "value": 1}]}])

    conv("conv_npc_sunny", "Sister... I became a demi-god and left the mortal realm. Take my blessing.",
         [{"text": "I'm glad you're safe.", "nextPhraseID": "X",
           "requires": [qp_require("quest_drow_leader", 100)],
           "rewards": [{"rewardType": "actorCondition", "rewardID": "sunny_blessed", "value": 1},
                       qp_reward("quest_search_sunny", 1000)]}])

    conv("conv_ozzy_complete", "You found her! The kingdom is in your debt.",
         [{"text": "Father...", "nextPhraseID": "X",
           "requires": [qp_require("quest_search_sunny", 1000)],
           "rewards": [{"rewardType": "giveItem", "rewardID": "gold", "value": 5000},
                       {"rewardType": "questProgress", "rewardID": "quest_search_sunny", "value": 1000}]}])

    for color in MOON_COLORS:
        conv(f"conv_moon_elder_{color}",
             f"The {color} moon elder tests your resolve.",
             [{"text": "Prove myself.", "nextPhraseID": "X",
               "rewards": [qp_reward(f"quest_moon_{color}", 100)]}])

    conv("conv_drow_leader",
         "All moon pacts are sealed. Sunny will meet you at the ring entry.",
         [{"text": "Summon her.", "nextPhraseID": "X",
           "requires": [qp_require(f"quest_moon_{c}", 100) for c in MOON_COLORS],
           "rewards": [activate_group_reward("ring_entry", "Spawn_sunny_summon"),
                       qp_reward("quest_drow_leader", 100),
                       qp_reward("quest_search_sunny", 700)]}])

    conv("conv_sunny_ring_search", "The ring realm hums with old magic.")

    conv("castle_blacksmith_greeting", "Royal steel for the princess's champion.")
    conv("castle_alchemist_greeting", "Potions brewed for the search.")

def build_holiday_content():
    HOLIDAY_QUESTS.append({
        "id": "quest_that_time_of_year",
        "name": "That Time of Year",
        "showInLog": 1,
        "stages": [
            quest_stage(10, "The Timekeeper explained holidays and events.", 0, 25),
            quest_stage(100, "I took part in a holiday or town event.", 1, 100),
        ],
    })

    def add_kind_quests(kind, table):
        for key in table:
            qid = f"quest_{kind}_{key}"
            HOLIDAY_QUESTS.append({
                "id": qid,
                "name": f"{key.replace('_', ' ').title()} ({kind})",
                "showInLog": 1,
                "stages": [
                    quest_stage(50, f"I learned about the {key.replace('_', ' ')} {kind}.", 0, 30),
                    quest_stage(100, f"I completed the {key.replace('_', ' ')} {kind}.", 1, 100),
                ],
            })

    add_kind_quests("holiday", HOLIDAYS)
    add_kind_quests("event", EVENTS)

    for loc in HAUNTED_LOCATIONS:
        HORROR_QUESTS.append({
            "id": f"quest_haunted_{loc}",
            "name": f"Cleanse the {loc.replace('_', ' ').title()}",
            "showInLog": 1,
            "stages": [
                quest_stage(50, f"I explored the {loc.replace('_', ' ')}.", 0, 50),
                quest_stage(100, f"I brought the {loc.replace('_', ' ')} trophy to the Priest.", 1, 200),
            ],
        })

    for guild, variant in (
        [(g, v) for g in ["mage"] for v in MAGE_TOWER_COLORS]
        + [(g, v) for g in ["cleric"] for v in CLERIC_CRYSTAL_TYPES]
        + [(g, v) for g in ["druid"] for v in DRUID_ORE_TYPES]
    ):
        TOWER_QUESTS.append({
            "id": f"quest_tower_{guild}_{variant}",
            "name": f"{variant.title()} {guild.title()} Tower",
            "showInLog": 1,
            "stages": [
                quest_stage(100, f"I defeated the {variant} {guild} tower boss.", 1, 250),
            ],
        })

    TOWER_QUESTS.append({
        "id": "quest_tower_grand",
        "name": "Grand Wizard's Trial",
        "showInLog": 1,
        "stages": [quest_stage(100, "The Grand Wizard acknowledged my mastery.", 1, 500)],
    })

    hconv("conv_timekeeper",
          "Welcome. I am the Timekeeper. That Time of Year has come.",
          [{"text": "Information", "nextPhraseID": "conv_timekeeper_info"},
           {"text": "Holidays", "nextPhraseID": "conv_timekeeper_holidays"},
           {"text": "Events", "nextPhraseID": "conv_timekeeper_events"},
           {"text": "Leave", "nextPhraseID": "X"}])

    hconv("conv_timekeeper_info",
          "I will inform the town when a holiday or special event begins. "
          "Speak with me again to start or end celebrations.",
          [{"text": "Back", "nextPhraseID": "conv_timekeeper"}])

    holiday_replies = []
    for key in HOLIDAYS:
        holiday_replies.append({
            "text": key.replace("_", " ").title(),
            "nextPhraseID": f"conv_{key}_menu",
        })
    hconv("conv_timekeeper_holidays", "Which holiday?", holiday_replies + [
        {"text": "Back", "nextPhraseID": "conv_timekeeper"},
    ])

    event_replies = []
    for key in EVENTS:
        event_replies.append({
            "text": key.replace("_", " ").title(),
            "nextPhraseID": f"conv_{key}_menu",
        })
    hconv("conv_timekeeper_events", "Which event?", event_replies + [
        {"text": "Back", "nextPhraseID": "conv_timekeeper"},
    ])

    def build_kind_menu(kind, key, gifts):
        cond = f"{kind}_active_{key}"
        qid = f"quest_{kind}_{key}"
        host_conv = f"conv_{key}_host"
        hconv(f"conv_{key}_menu",
              f"Manage {key.replace('_', ' ').title()}.",
              [{"text": "Begin celebration", "nextPhraseID": host_conv,
                "rewards": [ac_apply(cond), qp_reward("quest_that_time_of_year", 10),
                            qp_reward(qid, 50),
                            activate_group_reward("home", f"Spawn_host_{key}"),
                            deactivate_group_reward("home", "Spawn_timekeeper")]},
               {"text": "Back", "nextPhraseID": "conv_timekeeper"}])
        gift_replies = []
        for i, gift in enumerate(gifts):
            iid = gift_item_id(kind, key, gift)
            req = [qp_require(qid, 50)]
            if i > 0:
                req.append(qp_require(qid, i))
            gift_replies.append({
                "text": f"Collect: {gift}",
                "nextPhraseID": host_conv,
                "requires": req,
                "rewards": [give_item_reward(iid, 1), qp_reward(qid, i + 1)],
            })
        hconv(host_conv,
              f"I represent the {key.replace('_', ' ')} celebration.",
              [{"text": "Information", "nextPhraseID": "conv_timekeeper_info"},
               {"text": f"End {kind}", "nextPhraseID": "conv_timekeeper",
                "rewards": [ac_remove(cond), qp_reward(qid, 100), qp_reward("quest_that_time_of_year", 100),
                            activate_group_reward("home", "Spawn_timekeeper"),
                            deactivate_group_reward("home", f"Spawn_host_{key}")]},
               {"text": "Quest information", "nextPhraseID": f"conv_{key}_quest"},
               {"text": "Leave", "nextPhraseID": "X"}] + gift_replies)
        hconv(f"conv_{key}_quest",
              f"Complete tasks for the {key.replace('_', ' ')} {kind} and return for gifts.",
              [{"text": "Back", "nextPhraseID": host_conv}])

    for key, gifts in HOLIDAYS.items():
        build_kind_menu("holiday", key, gifts)
    for key, gifts in EVENTS.items():
        build_kind_menu("event", key, gifts)

    HORROR_CONVERSATIONS.append({
        "id": "conv_priest",
        "message": "The haunted places grow restless. Will you cleanse them?",
        "replies": [
            {"text": "Tell me of the haunts", "nextPhraseID": "conv_priest_list"},
            {"text": "I have a trophy", "nextPhraseID": "conv_priest_turnin"},
            {"text": "Leave", "nextPhraseID": "X"},
        ],
    })
    haunt_list = []
    for loc in HAUNTED_LOCATIONS:
        haunt_list.append({
            "text": loc.replace("_", " ").title(),
            "nextPhraseID": f"conv_priest_{loc}",
        })
    HORROR_CONVERSATIONS.append({
        "id": "conv_priest_list",
        "message": "Each haunt is a four-chamber labyrinth. Defeat its lord and bring me proof.",
        "replies": haunt_list + [{"text": "Back", "nextPhraseID": "conv_priest"}],
    })
    for loc in HAUNTED_LOCATIONS:
        HORROR_CONVERSATIONS.append({
            "id": f"conv_priest_{loc}",
            "message": f"Enter the {loc.replace('_', ' ')} from the south-west chamber.",
            "replies": [
                {"text": "Accept quest", "nextPhraseID": "conv_priest",
                 "rewards": [qp_reward(f"quest_haunted_{loc}", 50)]},
                {"text": "Back", "nextPhraseID": "conv_priest_list"},
            ],
        })
        HORROR_CONVERSATIONS.append({
            "id": f"conv_priest_turnin_{loc}",
            "message": f"You bear the trophy of {loc.replace('_', ' ')}.",
            "replies": [
                {"text": "Turn it in", "nextPhraseID": "X",
                 "requires": [
                     {"requireType": "inventoryRemove", "requireID": f"quest_item_{loc}", "value": 1},
                     qp_require(f"quest_haunted_{loc}", 50),
                 ],
                 "rewards": [qp_reward(f"quest_haunted_{loc}", 100)]},
            ],
        })
    HORROR_CONVERSATIONS.append({
        "id": "conv_priest_turnin",
        "message": "Which trophy do you offer?",
        "replies": [
            {"text": loc.replace("_", " ").title(), "nextPhraseID": f"conv_priest_turnin_{loc}"}
            for loc in HAUNTED_LOCATIONS
        ] + [{"text": "Back", "nextPhraseID": "conv_priest"}],
    })

    TOWER_CONVERSATIONS.append({
        "id": "conv_grand_wizard",
        "message": "Twelve elemental towers stand before my own. Conquer them all.",
        "replies": [
            {"text": "Tower quests", "nextPhraseID": "conv_grand_wizard_towers"},
            {"text": "I have all sigils", "nextPhraseID": "conv_grand_wizard_done",
             "requires": [qp_require(f"quest_tower_{g}_{v}", 100)
                          for g, vals in [("mage", MAGE_TOWER_COLORS), ("cleric", CLERIC_CRYSTAL_TYPES), ("druid", DRUID_ORE_TYPES)]
                          for v in vals]},
            {"text": "Leave", "nextPhraseID": "X"},
        ],
    })
    tower_opts = []
    for guild, variant in (
        [("mage", c) for c in MAGE_TOWER_COLORS]
        + [("cleric", c) for c in CLERIC_CRYSTAL_TYPES]
        + [("druid", c) for c in DRUID_ORE_TYPES]
    ):
        tower_opts.append({
            "text": f"{variant.title()} {guild.title()} Tower",
            "nextPhraseID": f"conv_tower_quest_{guild}_{variant}",
        })
    TOWER_CONVERSATIONS.append({
        "id": "conv_grand_wizard_towers",
        "message": "Spiral through each floor; the boss waits on the top level.",
        "replies": tower_opts + [{"text": "Back", "nextPhraseID": "conv_grand_wizard"}],
    })
    for guild, variant in (
        [("mage", c) for c in MAGE_TOWER_COLORS]
        + [("cleric", c) for c in CLERIC_CRYSTAL_TYPES]
        + [("druid", c) for c in DRUID_ORE_TYPES]
    ):
        TOWER_CONVERSATIONS.append({
            "id": f"conv_tower_quest_{guild}_{variant}",
            "message": f"Enter tower_{guild}_{variant}_l1_sw from the city.",
            "replies": [
                {"text": "Understood", "nextPhraseID": "conv_grand_wizard_towers"},
                {"text": "Turn in sigil", "nextPhraseID": "X",
                 "requires": [
                     {"requireType": "inventoryRemove", "requireID": f"quest_item_tower_{guild}_{variant}", "value": 1},
                 ],
                 "rewards": [qp_reward(f"quest_tower_{guild}_{variant}", 100)]},
            ],
        })
    TOWER_CONVERSATIONS.append({
        "id": "conv_grand_wizard_done",
        "message": "You have proven yourself. Take my blessing.",
        "replies": [{"text": "Thank you", "nextPhraseID": "X",
                     "rewards": [qp_reward("quest_tower_grand", 100)]}],
    })

build_story_content()
build_holiday_content()

# ============================================================
# GENERATE ALL MAPS
# ============================================================

def default_castle_spawns(map_id):
    spawns = []
    if map_id == "castle_throne":
        spawns = [
            {"id": "npc_ozzy", "phrase": "conv_npc_ozzy", "pos": (9, 6)},
            {"id": "npc_nymph", "phrase": "conv_npc_nymph", "pos": (11, 6)},
            {"id": "npc_sunny", "phrase": "conv_npc_sunny", "pos": (13, 6),
             "extra": {"active": "false"}},
        ]
    elif map_id == "home":
        spawns = [{"id": "npc_jasias_maid", "phrase": "conv_jasias_maid", "pos": (8, 8)}]
    elif map_id == "castle_entry":
        spawns = [{"id": "npc_castle_guard_tip", "phrase": "conv_castle_guard_tip", "pos": (10, 8),
                   "layer": "custom", "layer_name": "Spawn_castle_guard", "extra": {"active": "false"}}]
    elif map_id.startswith("castle_") and map_id not in ("castle_garden",):
        idx = sum(ord(c) for c in map_id) % 25
        spawns = [{"id": f"castle_npc_{idx + 1}", "phrase": f"conv_castle_npc_{idx + 1}", "pos": (8, 8)}]
    return spawns

def default_drow_spawns(map_id):
    race = DROW_RACES[sum(ord(c) for c in map_id) % len(DROW_RACES)]
    return [{"id": f"{race}_drow_{(sum(ord(c) for c in map_id) % 25) + 1}", "pos": (10, 10)}]

def all_maps_from_grids(*grids):
    ids = set()
    for grid in grids:
        for row in grid:
            for cell in row:
                if cell:
                    ids.add(cell)
    return ids

def spiral_box_links(base, next_base=None, entry_from=None):
    """Four-room spiral: sw->nw->ne->se; optional stairs on se to next_base_nw."""
    nw, ne, sw, se = (f"{base}_{c}" for c in BOX_CORNERS)
    links = {
        nw: {"east": ne},
        ne: {"south": se},
        se: {"west": sw},
        sw: {"north": nw},
    }
    if entry_from:
        links[sw][entry_from] = "city"
    if next_base:
        nxt = f"{next_base}_nw"
        links[se]["south"] = nxt
        links.setdefault(nxt, {})["north"] = se
    return links

def haunted_spawns(map_id):
    spawns = []
    loc = None
    for hloc in HAUNTED_LOCATIONS:
        if map_id.startswith(hloc + "_"):
            loc = hloc
            break
    if not loc:
        return spawns
    if map_id.endswith("_se"):
        spawns.append({"id": f"boss_{loc}", "pos": (12, 12)})
    else:
        idx = sum(ord(c) for c in map_id) % 20 + 1
        spawns.append({"id": f"monster_{loc}_{idx}", "pos": (10, 10)})
    return spawns

def tower_spawns(map_id):
    spawns = []
    if not map_id.startswith("tower_"):
        return spawns
    if map_id.startswith("tower_grand_"):
        rest = map_id[len("tower_grand_"):]
        level_s, corner = rest.split("_", 1)
        level = int(level_s[1:])
        if level == TOWER_BOSS_LEVEL and corner == "se":
            spawns.append({"id": "npc_grand_wizard", "phrase": "conv_grand_wizard", "pos": (12, 10)})
        else:
            qi = (level + sum(ord(c) for c in corner)) % len(GRAND_WIZARD_QUOTES)
            spawns.append({
                "id": f"monster_tower_mage_red_{min(level, 5)}",
                "phrase": f"conv_tower_quote_{qi}",
                "pos": (10, 10),
            })
        return spawns
    parts = map_id.split("_")
    if len(parts) < 5:
        return spawns
    guild, variant, level_part, corner = parts[1], parts[2], parts[3], parts[4]
    if not level_part.startswith("l"):
        return spawns
    level = int(level_part[1:])
    if level == TOWER_BOSS_LEVEL and corner == "se":
        spawns.append({"id": f"boss_tower_{guild}_{variant}", "pos": (12, 12)})
    else:
        spawns.append({"id": f"monster_tower_{guild}_{variant}_{level}", "pos": (10, 10)})
    return spawns

def generate_holiday_maps():
    """Haunted 4-room boxes, guild towers (6 floors), and grand tower."""
    home_links = grid_links(CASTLE_MAIN_GRID).get("home", {})

    for loc in HAUNTED_LOCATIONS:
        base = loc
        links = spiral_box_links(base, entry_from="south")
        for corner in BOX_CORNERS:
            mid = f"{base}_{corner}"
            build_map_tmx(mid, links.get(mid, {}), spawns=haunted_spawns(mid))

    for guild, variant in (
        [("mage", c) for c in MAGE_TOWER_COLORS]
        + [("cleric", c) for c in CLERIC_CRYSTAL_TYPES]
        + [("druid", c) for c in DRUID_ORE_TYPES]
    ):
        for level in range(1, TOWER_BOSS_LEVEL + 1):
            base = f"tower_{guild}_{variant}_l{level}"
            nxt = f"tower_{guild}_{variant}_l{level + 1}" if level < TOWER_BOSS_LEVEL else None
            entry = "south" if level == 1 else None
            links = spiral_box_links(base, next_base=nxt, entry_from=entry)
            for corner in BOX_CORNERS:
                mid = f"{base}_{corner}"
                build_map_tmx(mid, links.get(mid, {}), spawns=tower_spawns(mid))

    for level in range(1, TOWER_BOSS_LEVEL + 1):
        base = f"tower_grand_l{level}"
        nxt = f"tower_grand_l{level + 1}" if level < TOWER_BOSS_LEVEL else None
        entry = "south" if level == 1 else None
        links = spiral_box_links(base, next_base=nxt, entry_from=entry)
        if level == TOWER_BOSS_LEVEL:
            links[f"{base}_se"]["east"] = "city"
        for corner in BOX_CORNERS:
            mid = f"{base}_{corner}"
            build_map_tmx(mid, links.get(mid, {}), spawns=tower_spawns(mid))

    home_spawns = [
        {"id": "npc_timekeeper", "phrase": "conv_timekeeper", "pos": (6, 10)},
        {"id": "npc_priest", "phrase": "conv_priest", "pos": (10, 10)},
    ]
    for key in list(HOLIDAYS.keys()) + list(EVENTS.keys()):
        home_spawns.append({
            "id": f"npc_{key}",
            "phrase": f"conv_{key}_host",
            "pos": (14, 10),
            "layer": "custom",
            "layer_name": f"Spawn_host_{key}",
            "extra": {"active": "false"},
        })
    build_map_tmx("home", home_links, spawns=home_spawns,
                  keys=[{"name": "key_start_block", "phrase": "key_start_block", "pos": (6, 6)}])

def generate_all_maps():
    download_template()
    global template_root
    template_root = ET.parse(TMX_TEMPLATE).getroot()

    main_links = grid_links(CASTLE_MAIN_GRID)
    upper_links = grid_links(CASTLE_UPPER_GRID)
    lower_links = grid_links(CASTLE_LOWER_GRID)

    main_links["castle_center"]["north"] = "castle_top"
    upper_links["castle_top"]["south"] = "castle_center"
    main_links["castle_center"]["south"] = "castle_lower"
    lower_links["castle_lower"]["north"] = "castle_center"
    drow_links = grid_links(DROW_LAIR_GRID)
    drow_links.update(grid_links(DROW_TUNNEL_GRID))
    drow_links["drow_cave"]["east"] = "swamp_witch"
    dragon_links = grid_links(DRAGON_GRID)
    ring_links = grid_links(RING_GRID)
    ring_links["ring_clearing"]["north"] = "swamp_witch"

    all_map_links = {}
    for chunk in (main_links, upper_links, lower_links, drow_links, dragon_links, ring_links):
        for mid, links in chunk.items():
            if mid not in all_map_links:
                all_map_links[mid] = {}
            all_map_links[mid].update(links)

    all_map_links.setdefault("swamp_witch", {})
    all_map_links["swamp_witch"].update({"west": "drow_cave", "south": "ring_clearing"})
    all_map_links["lloth_realm"] = {}
    all_map_links["psychotic_mage"] = {"south": "haunted_crypt_sw"}

    moon_grids = []
    for color in MOON_COLORS:
        grid = [
            [f"moon_{color}_woods", f"moon_{color}_village", f"moon_{color}_lake"],
            [f"moon_{color}_forest", f"moon_{color}_clearing", f"moon_{color}_mountain"],
            [f"moon_{color}_hills", f"moon_{color}_rocket", f"moon_{color}_swamp"],
        ]
        moon_grids.append(grid)
        ml = grid_links(grid)
        if color == "red":
            ml[f"moon_{color}_clearing"]["west"] = "ring_clearing"
        for mid, links in ml.items():
            if mid not in all_map_links:
                all_map_links[mid] = {}
            all_map_links[mid].update(links)

    all_map_ids = all_maps_from_grids(
        CASTLE_MAIN_GRID, CASTLE_UPPER_GRID, CASTLE_LOWER_GRID,
        DROW_LAIR_GRID, DROW_TUNNEL_GRID, DRAGON_GRID, RING_GRID,
        *moon_grids,
    )
    all_map_ids.update(all_map_links.keys())
    all_map_ids.update(["swamp_witch", "lloth_realm", "psychotic_mage", "castle"])

    for map_id in sorted(all_map_ids):
        if any(map_id == loc or map_id.startswith(loc + "_") for loc in HAUNTED_LOCATIONS):
            continue
        if map_id.startswith("tower_"):
            continue
        links = all_map_links.get(map_id, {})
        spawns = []
        keys = []
        if map_id == "home":
            continue
        elif map_id.startswith("castle_"):
            spawns = default_castle_spawns(map_id)
        elif map_id.startswith("drow_"):
            spawns = default_drow_spawns(map_id)
            if map_id == "drow_cave":
                spawns.extend([
                    {"id": "npc_drow_shaman", "phrase": "conv_drow_shaman", "pos": (8, 8)},
                ])
        elif map_id == "swamp_witch":
            spawns = [{"id": "npc_swamp_witch", "phrase": "conv_swamp_witch_1", "pos": (10, 10)}]
        elif map_id == "lloth_realm":
            spawns = [{"id": "npc_lloth", "phrase": "conv_npc_lloth", "pos": (14, 10)}]
            for i in range(6):
                spawns.append({"id": f"castle_npc_{i+1}", "phrase": f"conv_castle_npc_{i+1}", "pos": (4 + i, 12)})
        elif map_id.startswith("dragon_"):
            spawns = [{"id": f"dragon_{(sum(ord(c) for c in map_id) % 60) + 1}", "pos": (12, 10)}]
            if map_id == "dragon_platinum":
                spawns.append({"id": f"dragon_{(sum(ord(c) for c in map_id) % 60) + 1}", "phrase": "conv_dragon_platinum", "pos": (8, 8)})
            elif map_id == "dragon_chromatic":
                spawns.append({"id": f"dragon_{(sum(ord(c) for c in map_id) % 60) + 1}", "phrase": "conv_dragon_chromatic", "pos": (8, 8)})
            elif map_id == "dragon_throne":
                spawns.append({"id": f"dragon_{(sum(ord(c) for c in map_id) % 60) + 1}", "phrase": "conv_dragon_chromatic", "pos": (10, 8)})
        elif map_id == "psychotic_mage":
            spawns = [{"id": "npc_psychotic_mage", "phrase": "conv_psychotic_mage", "pos": (10, 10)}]
        elif map_id == "ring_entry":
            spawns = [
                {"id": "npc_ring_guard", "phrase": "conv_ring_guard", "pos": (8, 8)},
                {"id": "npc_sunny", "phrase": "conv_npc_sunny", "pos": (12, 8),
                 "layer": "custom", "layer_name": "Spawn_sunny_summon", "extra": {"active": "false"}},
            ]
        elif map_id.startswith("moon_"):
            color = map_id.split("_")[1]
            if map_id.endswith("_clearing"):
                spawns = [{"id": f"npc_moon_elder_{color}", "phrase": f"conv_moon_elder_{color}", "pos": (10, 10)}]
        elif map_id == "castle":
            spawns = [{"id": "npc_ozzy", "phrase": "conv_npc_ozzy", "pos": (4, 4)}]

        build_map_tmx(map_id, links, spawns=spawns, keys=keys)

generate_all_maps()
generate_holiday_maps()

# Psychotic mage (combat)
low, high = random_damage()
castle_monsters.append({
    "id": "npc_psychotic_mage",
    "name": "Psychotic Mage",
    "iconID": MONSTER_ICON,
    "maxHP": 900,
    "attackChance": 75,
    "attackDamage": {"min": low + 20, "max": high + 40},
    "moveCost": 5,
    "attackCost": 5,
    "spawnGroup": "npc_psychotic_mage",
    "droplistID": "droplist_psychotic_mage",
    "faction": "neutral",
})

# Merge story NPCs (avoid duplicates with generated castle NPCs)
_story_ids = {m["id"] for m in castle_monsters + town_monsters}
for npc in STORY_NPCS:
    if npc["id"] not in _story_ids:
        castle_monsters.append(npc)
        _story_ids.add(npc["id"])

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
            f"{random.choice(DROW_WEAPON_PREFIXES)} "
            f"{random.choice(DROW_WEAPON_TYPES)}"
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
        slot_id, slot_name = DROW_ARMOR_SLOTS[i % len(DROW_ARMOR_SLOTS)]
        armor_name = (
            f"{race_name} "
            f"{random.choice(DROW_WEAPON_PREFIXES)} "
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
        low, high = random_drow_damage()
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
            "droplistID": drop_id,
            "spawnGroup": f"{race}_drow",
            "faction": "drow_elf"
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
        low, high = random_drow_damage()
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
            "droplistID": drop_id,
            "spawnGroup": f"dragon_{dragon_type.lower()}",
            "faction": "drow_elf"
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

write_json(os.path.join(OUTPUT_RAW, "itemlist_potions.json"), POTION_ITEMS)
write_json(os.path.join(OUTPUT_RAW, "itemlist_quest.json"), QUEST_ITEMS)
write_json(os.path.join(OUTPUT_RAW, "actorconditions_sunny.json"), ACTORCONDITIONS_QUEST)
write_json(os.path.join(OUTPUT_RAW, "conversationlist_castle.json"), CONVERSATIONS)
write_json(os.path.join(OUTPUT_RAW, "conversationlist_town.json"), [
    c for c in CONVERSATIONS if c["id"].startswith("conv_town_") or c["id"].startswith("conv_haunt_")
])
write_json(os.path.join(OUTPUT_RAW, "conversationlist_sunny.json"), CONVERSATIONS)
write_json(os.path.join(OUTPUT_RAW, "questlist_castle.json"), [
    q for q in QUESTS if q["id"].startswith("quest_castle_clue_")
])
write_json(os.path.join(OUTPUT_RAW, "questlist_sunny.json"), QUESTS)

def shop_droplist(did, item_ids):
    return {
        "id": did,
        "items": [{"item": iid, "quantity": {"min": 1, "max": 1}, "chance": "100"} for iid in item_ids],
    }

write_json(os.path.join(OUTPUT_RAW, "droplists_castle_blacksmith.json"), [
    shop_droplist("droplist_castle_blacksmith", [w["id"] for w in weapon_items[:15]]),
])
write_json(os.path.join(OUTPUT_RAW, "droplists_castle_alchemist.json"), [
    shop_droplist("droplist_castle_alchemist", [p["id"] for p in POTION_ITEMS[:15]]),
])
write_json(os.path.join(OUTPUT_RAW, "droplists_psychotic_mage.json"), [{
    "id": "droplist_psychotic_mage",
    "items": [
        {"item": "mage_note", "quantity": {"min": 1, "max": 1}, "chance": "100"},
        {"item": "sunny_ring", "quantity": {"min": 1, "max": 1}, "chance": "100"},
    ],
}])

write_json(os.path.join(OUTPUT_RAW, "itemlist_holiday.json"), holiday_items)
write_json(os.path.join(OUTPUT_RAW, "monsterlist_holiday.json"), holiday_monsters)
write_json(os.path.join(OUTPUT_RAW, "itemlist_horror.json"), horror_items)
write_json(os.path.join(OUTPUT_RAW, "monsterlist_horror.json"), horror_monsters)
write_json(os.path.join(OUTPUT_RAW, "droplists_horror.json"), horror_droplists)
write_json(os.path.join(OUTPUT_RAW, "itemlist_tower.json"), tower_items)
write_json(os.path.join(OUTPUT_RAW, "monsterlist_tower.json"), tower_monsters)
write_json(os.path.join(OUTPUT_RAW, "droplists_tower.json"), tower_droplists)
write_json(os.path.join(OUTPUT_RAW, "actorconditions_holiday.json"), ACTORCONDITIONS_HOLIDAY)
write_json(os.path.join(OUTPUT_RAW, "conversationlist_holiday.json"), HOLIDAY_CONVERSATIONS)
write_json(os.path.join(OUTPUT_RAW, "conversationlist_horror.json"), HORROR_CONVERSATIONS)
write_json(os.path.join(OUTPUT_RAW, "conversationlist_tower.json"), TOWER_CONVERSATIONS)
write_json(os.path.join(OUTPUT_RAW, "questlist_holiday.json"), HOLIDAY_QUESTS)
write_json(os.path.join(OUTPUT_RAW, "questlist_horror.json"), HORROR_QUESTS)
write_json(os.path.join(OUTPUT_RAW, "questlist_tower.json"), TOWER_QUESTS)

if not os.environ.get("jasia_ORCHESTRATE"):
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
print(" Jasia Quest Generator (castle + holiday)")
print("===================================================")
print(f"Castle NPCs: {len(castle_monsters)}")
print(f"Town NPCs: {len(town_monsters)}")
print(f"Weapons: {len(weapon_items)}")
print(f"Armor Items: {len(armor_items)}")
print(f"Shop Items: {len(shop_items)}")
print(f"Potions: {len(POTION_ITEMS)}")
print(f"Quest Items: {len(QUEST_ITEMS)}")
print(f"Conversations: {len(CONVERSATIONS)}")
print(f"Quests: {len(QUESTS)}")
print(f"TMX Maps: {len(list(OUTPUT_XML.glob('*.tmx')))}")
print(f"Holiday Items: {len(holiday_items)}")
print(f"Holiday NPCs: {len(holiday_monsters)}")
print(f"Horror Monsters: {len(horror_monsters)}")
print(f"Tower Monsters: {len(tower_monsters)}")
print(f"Holiday Quests: {len(HOLIDAY_QUESTS)}")
print(f"Horror Quests: {len(HORROR_QUESTS)}")
print(f"Tower Quests: {len(TOWER_QUESTS)}")
print("===================================================")
print("===================================================")
print(" Drow + Dragon Resources Generated")
print("===================================================")
print("Drow Races:", len(DROW_RACES))
print("Dragon Monsters:", len(dragon_monsters))
print("Dragon Spells:", len(dragon_conditions))
print("Dragon Treasure Items:", len(dragon_items))
print("===================================================")
