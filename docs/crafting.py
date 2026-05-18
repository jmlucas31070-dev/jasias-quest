#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
crafting.py

Generates JSON data files and TMX maps for the Andors Trail crafting system.
"""

import json
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET
from copy import deepcopy

from at_format import make_conv, req_actor_condition, req_inv_remove, r_give_item, write_json

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

def create_basic_item(iid, name, cost, category, desc):
    return {
        "id": iid,
        "name": name,
        "iconID": "items_armours:1",
        "displaytype": "ordinary",
        "baseMarketCost": cost,
        "category": category,
        "description": desc
    }

# ============================================================
# AUTO DROPLIST HELPER
# ============================================================

def auto_droplist(animal_name):
    """
    Generate a plausible list of drop item names for the given animal.
    Uses keyword matching on the animal name (case-insensitive).
    Returns a list of item name strings.
    """
    n = animal_name.lower()
    an = animal_name

    RULES = [
        (["snake", "serpent", "viper", "cobra", "asp", "mamba"],
            ["{} Fang", "{} Venom", "{} Skin"]),
        (["wolf", "coyote", "hyena", "jackal"],
            ["{} Fang", "{} Pelt"]),
        (["fox", "lynx", "bobcat", "wildcat", "ocelot", "puma", "cougar", "panther", "leopard", "cheetah", "jaguar"],
            ["{} Fur", "{} Fang"]),
        (["bear"],
            ["{} Claw", "{} Pelt", "{} Fat"]),
        (["eagle", "condor"],
            ["{} Feather", "{} Talon"]),
        (["hawk", "falcon", "osprey"],
            ["{} Feather", "{} Talon"]),
        (["owl", "heron", "crane", "stork", "bittern"],
            ["{} Feather", "{} Claw"]),
        (["crow", "raven"],
            ["{} Feather", "Black Feather"]),
        (["pigeon", "dove", "gull", "pelican", "seagull", "kingfisher", "bittern"],
            ["{} Feather"]),
        (["duck", "goose", "swan", "pheasant", "turkey", "quail", "grouse", "roadrunner"],
            ["{} Feather", "{} Bone"]),
        (["chicken", "hen", "rooster"],
            ["{} Feather", "{} Bone"]),
        (["spider"],
            ["{} Venom", "{} Silk", "{} Egg Sac"]),
        (["scorpion"],
            ["{} Venom", "{} Stinger", "{} Carapace"]),
        (["bat"],
            ["{} Wing", "{} Fang"]),
        (["rat", "mouse"],
            ["{} Tail", "{} Fur"]),
        (["mole", "gopher", "groundhog", "prairie dog"],
            ["{} Claw", "{} Fur"]),
        (["squirrel", "chipmunk", "raccoon"],
            ["{} Tail", "{} Fur"]),
        (["rabbit", "hare", "jackrabbit"],
            ["{} Fur", "{} Foot"]),
        (["deer", "elk", "moose", "reindeer", "stag"],
            ["{} Hide", "{} Antler"]),
        (["antelope", "gazelle", "oryx", "ibex"],
            ["{} Hide", "{} Horn"]),
        (["goat", "ram", "sheep"],
            ["{} Hide", "{} Horn"]),
        (["bison", "ox", "bull", "yak", "cow", "cattle"],
            ["{} Hide", "{} Horn"]),
        (["boar", "pig", "swine", "warthog"],
            ["{} Tusk", "{} Hide"]),
        (["horse", "stallion", "mare", "pony", "mule", "donkey"],
            ["{} Hair", "{} Hide"]),
        (["camel", "llama"],
            ["{} Hide", "{} Hair"]),
        (["lizard", "gecko", "iguana", "monitor"],
            ["{} Scale", "{} Tail"]),
        (["toad", "frog"],
            ["{} Skin", "{} Slime"]),
        (["salamander", "newt"],
            ["{} Skin", "{} Tail"]),
        (["crab", "lobster"],
            ["{} Shell", "{} Claw"]),
        (["clam", "oyster"],
            ["{} Shell"]),
        (["trout", "salmon", "pike", "catfish", "tuna", "marlin", "swordfish", "barracuda"],
            ["{} Scale", "{} Oil"]),
        (["eel", "leech"],
            ["{} Scale", "{} Oil"]),
        (["otter", "beaver"],
            ["{} Fur", "{} Claw"]),
        (["mink", "ferret", "weasel", "stoat", "ermine"],
            ["{} Fur", "{} Claw"]),
        (["badger", "wolverine"],
            ["{} Claw", "{} Hide"]),
        (["shark"],
            ["{} Tooth", "{} Hide"]),
        (["whale", "orca"],
            ["{} Oil", "{} Bone"]),
        (["dolphin", "porpoise"],
            ["{} Oil"]),
        (["seal", "walrus", "sea lion"],
            ["{} Hide", "{} Tusk"]),
        (["penguin"],
            ["{} Feather", "{} Oil"]),
        (["octopus", "squid", "kraken"],
            ["{} Tentacle", "{} Ink"]),
        (["jellyfish"],
            ["{} Venom", "{} Gel"]),
        (["turtle", "tortoise"],
            ["{} Shell", "{} Claw"]),
        (["beetle", "weevil"],
            ["{} Shell", "{} Carapace"]),
        (["ant", "termite"],
            ["{} Carapace"]),
        (["mosquito", "fly", "gnat"],
            ["{} Wing"]),
        (["cricket", "grasshopper", "mantis"],
            ["{} Leg", "{} Carapace"]),
        (["maggot", "grub", "worm"],
            ["{} Slime"]),
        (["meerkat", "mongoose"],
            ["{} Fur", "{} Claw"]),
        (["dog", "hound"],
            ["{} Fang", "{} Fur"]),
        (["imp"],
            ["{} Horn", "{} Claw"]),
        (["demon", "devil"],
            ["{} Horn", "{} Claw", "{} Ichor"]),
        (["drake", "dragon", "wyvern"],
            ["{} Scale", "{} Fang", "{} Claw"]),
        (["mephit"],
            ["{} Shard", "{} Dust"]),
        (["elemental"],
            ["{} Essence", "{} Core"]),
        (["wraith", "specter", "ghost", "phantom"],
            ["{} Essence", "{} Fragment"]),
        (["ghoul", "zombie"],
            ["{} Bone", "{} Flesh"]),
        (["troll"],
            ["{} Fat", "{} Bone"]),
        (["goblin"],
            ["{} Ear", "Crude Dagger"]),
        (["vulture", "buzzard"],
            ["{} Feather", "Bone Dust"]),
        (["manta", "ray", "stingray"],
            ["{} Spine", "{} Hide"]),
        (["fish"],
            ["{} Scale", "{} Oil"]),
        (["cat"],
            ["{} Fur", "{} Claw"]),
    ]

    for keywords, template in RULES:
        if any(k in n for k in keywords):
            return [t.format(an) for t in template]

    # Default
    return [f"{an} Hide", f"{an} Fang"]

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

    "shrubland": {
        "animals": [
            "Jackrabbit", "Fox", "Coyote", "Badger", "Quail",
            "Roadrunner", "Lizard", "Rattlesnake", "Wild Goat", "Hare",
            "Hawk", "Vulture", "Mule Deer", "Scorpion", "Prairie Dog",
            "Bobcat", "Raven", "Desert Tortoise", "Weasel", "Horned Toad",
            "Wild Dog", "Dust Hare", "Brush Wolf", "Scrub Cat", "Antelope"
        ],
        "forage": [
            "Juniper Berry", "Sagebrush", "Wild Thyme", "Prickly Pear", "Dry Moss",
            "Sunroot", "Dust Leaf", "Wild Onion", "Mesquite Bean", "Yucca Root",
            "Brush Berry", "Cactus Fruit", "Desert Mint", "Rock Mushroom", "Acacia Seed",
            "Scrub Herb", "Dry Root", "Bitter Root", "Sun Pepper", "Tumbleweed Seed",
            "Wild Garlic", "Agave", "Dust Blossom", "Stone Root", "Red Berry"
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
    },

    "marsh": {
        "animals": [
            "Heron", "Frog", "Marsh Rat", "Water Snake", "Otter",
            "Mud Crab", "Leech", "Bog Spider", "Toad", "Eel",
            "Snapping Turtle", "Marsh Hawk", "Swamp Deer", "Mud Lizard", "Croaker",
            "Fen Fox", "Reed Hare", "Bittern", "Mire Hound", "Mosquito",
            "Fen Beetle", "Water Beetle", "River Turtle", "Wetland Boar", "Marsh Cat"
        ],
        "forage": [
            "Cattail", "Water Lily", "Bog Moss", "Fen Berry", "Swamp Mint",
            "Reed Stem", "Mud Mushroom", "Duckweed", "River Bulb", "Marsh Herb",
            "Wet Bark", "Frogwort", "Bog Flower", "Fen Grass", "Water Nut",
            "Mire Blossom", "Leech Vine", "Mud Fern", "Swamp Garlic", "Blackroot",
            "Reed Seed", "Wet Herb", "Mud Pepper", "Mire Seed", "Marsh Root"
        ]
    },

    "bog": {
        "animals": [
            "Bog Spider", "Leech", "Toad", "Marsh Rat", "Fen Beetle",
            "Mud Snake", "Croaker", "Bog Hound", "Water Snake", "Swamp Cat",
            "Mud Crab", "Mosquito", "Heron", "Snapping Turtle", "Otter",
            "Fen Fox", "Mire Wolf", "Bog Hare", "Mud Lizard", "Reed Crow",
            "Frog", "Eel", "Bog Deer", "Wetland Boar", "Mire Beetle"
        ],
        "forage": [
            "Bog Moss", "Blackroot", "Mud Mushroom", "Fen Berry", "Wet Bark",
            "Leech Vine", "Bog Flower", "Mire Blossom", "Swamp Mint", "Mud Fern",
            "Rot Fruit", "Fen Grass", "Reed Stem", "Water Nut", "Marsh Herb",
            "Wet Herb", "Mire Seed", "Frogwort", "Bog Root", "Duckweed",
            "Mud Pepper", "River Bulb", "Swamp Garlic", "Dark Moss", "Peat Root"
        ]
    },

    "tundra": {
        "animals": [
            "Snow Hare", "Arctic Fox", "Reindeer", "Musk Ox", "Snow Owl",
            "Polar Wolf", "Ice Bear", "Seal", "White Stoat", "Tundra Elk",
            "Ice Lynx", "Snow Falcon", "Frost Ram", "Walrus", "Penguin",
            "Arctic Hare", "Glacier Goat", "Snow Weasel", "Ice Crow", "Winter Boar",
            "Frost Hound", "Snowy Owl", "Ice Otter", "Frozen Stag", "Cold Drake"
        ],
        "forage": [
            "Snow Moss", "Ice Berry", "Frost Root", "Tundra Herb", "Frozen Mushroom",
            "Arctic Thyme", "White Lichen", "Ice Fern", "Cold Reed", "Snow Mint",
            "Winter Bark", "Glacier Flower", "Frozen Seed", "Ice Bulb", "Frostweed",
            "Coldroot", "Snow Clover", "Ice Petal", "Tundra Grass", "Winter Berry",
            "Frozen Nut", "Frost Blossom", "Arctic Moss", "Snow Onion", "Iceleaf"
        ]
    },

    "hills": {
        "animals": [
            "Goat", "Ram", "Fox", "Badger", "Boar",
            "Hill Wolf", "Falcon", "Hare", "Deer", "Wild Dog",
            "Mole", "Lynx", "Crow", "Weasel", "Ferret",
            "Hill Cat", "Mountain Hare", "Rock Lizard", "Elk", "Hawk",
            "Antelope", "Wild Sheep", "Groundhog", "Otter", "Stone Boar"
        ],
        "forage": [
            "Thyme", "Sage", "Juniper", "Wild Onion", "Acorn",
            "Hazelnut", "Blueberry", "Blackberry", "Hill Moss", "Wild Garlic",
            "Stone Root", "Berry", "Parsley", "Mint", "Lavender",
            "Rosehip", "Hill Flower", "Yarrow", "Sunflower Seed", "Wild Carrot",
            "Grass Seed", "Flax", "Mushroom", "Nettle", "Oak Bark"
        ]
    },

    "mountain": {
        "animals": [
            "Mountain Goat", "Ram", "Eagle", "Snow Leopard", "Wolf",
            "Bear", "Rock Lizard", "Hawk", "Stone Boar", "Elk",
            "Falcon", "Mountain Lion", "Wild Sheep", "Ice Lynx", "Cliff Hare",
            "Stone Drake", "Vulture", "Rock Snake", "Cave Bear", "Condor",
            "Mountain Fox", "Peak Stag", "Iron Boar", "Ridge Wolf", "Frost Eagle"
        ],
        "forage": [
            "Stone Root", "Mountain Herb", "Juniper", "Moss", "Pine Nut",
            "Wild Onion", "Cliff Berry", "Snow Mint", "Frost Mushroom", "Oak Bark",
            "Pine Cone", "Highland Thyme", "Rock Fern", "Coldroot", "Mountain Flower",
            "Ice Berry", "Peak Moss", "Stone Moss", "Wild Garlic", "Frostweed",
            "Alpine Seed", "Cliff Blossom", "Evergreen Needle", "Mountain Sage", "Granite Root"
        ]
    },

    "alpine": {
        "animals": [
            "Snow Hare", "Mountain Goat", "Eagle", "Ice Lynx", "Frost Ram",
            "Cliff Fox", "Peak Wolf", "Falcon", "White Stoat", "Glacier Elk",
            "Condor", "Snow Leopard", "Stone Drake", "Mountain Hare", "Winter Boar",
            "Ice Eagle", "Peak Stag", "Rock Snake", "Cold Hound", "Alpine Crow",
            "Frost Goat", "Cliff Cat", "Ridge Wolf", "Snow Weasel", "Ice Bear"
        ],
        "forage": [
            "Alpine Flower", "Snow Moss", "Frost Root", "Juniper", "Ice Berry",
            "Coldroot", "Glacier Herb", "Rock Fern", "Snow Mint", "Mountain Sage",
            "Frozen Mushroom", "Peak Moss", "Stone Root", "Evergreen Needle", "Cliff Berry",
            "Highland Thyme", "Frostweed", "Ice Petal", "Alpine Seed", "Winter Bark",
            "Pine Nut", "Snow Clover", "Cold Reed", "Glacier Flower", "Mountain Herb"
        ]
    },

    "volcano": {
        "animals": [
            "Fire Lizard", "Ash Snake", "Magma Beetle", "Rock Drake", "Cinder Wolf",
            "Lava Crab", "Ash Rat", "Fire Hawk", "Smoke Serpent", "Burning Scorpion",
            "Obsidian Boar", "Heat Vulture", "Flame Fox", "Coal Spider", "Cinder Cat",
            "Ash Bat", "Inferno Hound", "Molten Toad", "Blister Beetle", "Smoke Bat",
            "Fire Ant", "Lava Serpent", "Charred Ram", "Magma Hound", "Cinder Crow"
        ],
        "forage": [
            "Ash Root", "Fire Moss", "Cinder Flower", "Heat Fern", "Smoke Herb",
            "Lava Bloom", "Obsidian Fungus", "Burnroot", "Sulfur Weed", "Char Moss",
            "Fire Pepper", "Ash Berry", "Volcanic Mint", "Blister Pod", "Coal Mushroom",
            "Ember Seed", "Scorchleaf", "Magma Flower", "Heat Root", "Smoke Blossom",
            "Ash Bark", "Inferno Herb", "Flame Petal", "Cinder Seed", "Lava Root"
        ]
    },

    "river": {
        "animals": [
            "Otter", "Beaver", "Salmon", "Trout", "River Turtle",
            "Water Snake", "Heron", "Frog", "Eel", "Mud Crab",
            "Kingfisher", "River Boar", "Duck", "Leech", "Croaker",
            "River Rat", "Snapping Turtle", "Water Beetle", "Marsh Deer", "Mink",
            "Catfish", "River Hawk", "Swan", "Pike", "Wet Hound"
        ],
        "forage": [
            "River Reed", "Water Lily", "Cattail", "River Bulb", "Wet Moss",
            "Fen Berry", "Swamp Mint", "Mud Mushroom", "Duckweed", "Water Nut",
            "River Herb", "Reed Stem", "Mud Fern", "Wet Bark", "Frogwort",
            "River Grass", "Water Root", "Marsh Herb", "Bog Flower", "Wet Seed",
            "Blue Reed", "River Mint", "Mire Blossom", "Shore Berry", "Water Fern"
        ]
    },

    "lake": {
        "animals": [
            "Trout", "Pike", "Otter", "Duck", "Swan",
            "Heron", "Eel", "River Turtle", "Water Snake", "Mud Crab",
            "Frog", "Beaver", "Catfish", "Leech", "Mink",
            "Croaker", "Lake Boar", "Snapping Turtle", "Kingfisher", "Water Beetle",
            "Marsh Deer", "Lake Hawk", "Goose", "River Rat", "Wet Hound"
        ],
        "forage": [
            "Water Lily", "Cattail", "River Reed", "Duckweed", "Water Nut",
            "Wet Moss", "Lake Herb", "Mud Mushroom", "River Bulb", "Swamp Mint",
            "Fen Berry", "Reed Stem", "Water Fern", "Wet Bark", "Bog Flower",
            "Mud Fern", "Lake Root", "Water Root", "Marsh Herb", "Blue Reed",
            "Shore Berry", "Wet Seed", "River Grass", "Mire Blossom", "Water Mint"
        ]
    },

    "sea": {
        "animals": [
            "Shark", "Seal", "Dolphin", "Sea Turtle", "Crab",
            "Lobster", "Eel", "Swordfish", "Seagull", "Octopus",
            "Manta Ray", "Sea Snake", "Whale", "Barracuda", "Sea Lion",
            "Jellyfish", "Coral Crab", "Reef Shark", "Tuna", "Pelican",
            "Sea Otter", "Kraken Spawn", "Clam", "Marlin", "Reef Eel"
        ],
        "forage": [
            "Seaweed", "Kelp", "Salt Grass", "Coral Moss", "Pearl Algae",
            "Driftwood", "Sea Berry", "Tide Root", "Ocean Herb", "Shell Fungus",
            "Reef Bloom", "Salt Crystal", "Sea Mint", "Water Pod", "Blue Coral",
            "Brine Weed", "Sea Fern", "Tide Flower", "Kelp Seed", "Coral Root",
            "Salt Mushroom", "Ocean Moss", "Wave Reed", "Shell Root", "Pearl Moss"
        ]
    },

    "ocean": {
        "animals": [
            "Whale", "Shark", "Kraken Spawn", "Sea Serpent", "Dolphin",
            "Tuna", "Marlin", "Swordfish", "Manta Ray", "Octopus",
            "Sea Turtle", "Reef Shark", "Barracuda", "Jellyfish", "Sea Lion",
            "Seal", "Coral Crab", "Deep Eel", "Leviathan Fry", "Sea Snake",
            "Pelican", "Flying Fish", "Ocean Drake", "Storm Gull", "Reef Eel"
        ],
        "forage": [
            "Kelp", "Seaweed", "Pearl Algae", "Brine Weed", "Coral Moss",
            "Ocean Herb", "Tide Root", "Sea Fern", "Blue Coral", "Salt Grass",
            "Wave Reed", "Shell Fungus", "Ocean Moss", "Tide Flower", "Coral Root",
            "Sea Mint", "Salt Crystal", "Pearl Moss", "Water Pod", "Deep Kelp",
            "Storm Algae", "Reef Bloom", "Sea Berry", "Shell Root", "Driftwood"
        ]
    },

    "small_cave": {
        "animals": [
            "Bat", "Rat", "Cave Spider", "Lizard", "Snake",
            "Mole", "Cave Cricket", "Weasel", "Ferret", "Rock Toad",
            "Cave Beetle", "Blind Fish", "Stone Rat", "Dark Bat", "Tunnel Snake",
            "Cave Fox", "Burrow Hare", "Dust Spider", "Rock Lizard", "Mushroom Beetle",
            "Tunnel Rat", "Shadow Cat", "Stone Snake", "Deep Mole", "Cave Crow"
        ],
        "forage": [
            "Cave Moss", "Glow Mushroom", "Stone Root", "Bat Guano Fungus", "Dark Fern",
            "Tunnel Herb", "Rock Moss", "Blind Mushroom", "Dust Root", "Cave Berry",
            "Glow Moss", "Stone Fungus", "Root Vine", "Wet Moss", "Shadow Herb",
            "Cave Mint", "Mushroom Cap", "Tunnel Root", "Rock Fern", "Darkroot",
            "Crystal Moss", "Earth Fungus", "Deep Mushroom", "Stone Flower", "Glow Fern"
        ]
    },

    "large_cave": {
        "animals": [
            "Bat", "Cave Bear", "Cave Spider", "Rock Snake", "Blind Fish",
            "Stone Boar", "Dark Wolf", "Tunnel Rat", "Cave Lizard", "Shadow Cat",
            "Deep Mole", "Rock Toad", "Mushroom Beetle", "Dust Spider", "Stone Drake",
            "Cave Hawk", "Burrow Hare", "Crystal Beetle", "Tunnel Snake", "Dark Bat",
            "Cave Crab", "Stone Rat", "Underground Eel", "Shadow Hound", "Rock Scorpion"
        ],
        "forage": [
            "Glow Mushroom", "Cave Moss", "Stone Fungus", "Crystal Moss", "Dark Fern",
            "Tunnel Root", "Bat Guano Fungus", "Shadow Herb", "Glow Fern", "Earth Fungus",
            "Stone Root", "Rock Moss", "Blind Mushroom", "Deep Mushroom", "Darkroot",
            "Crystal Flower", "Wet Moss", "Tunnel Herb", "Dust Root", "Glow Berry",
            "Root Vine", "Stone Flower", "Mushroom Cap", "Cave Mint", "Shadow Moss"
        ]
    },

    "dark_cave": {
        "animals": [
            "Dark Bat", "Shadow Spider", "Blind Fish", "Tunnel Snake", "Cave Scorpion",
            "Deep Rat", "Stone Drake", "Shadow Cat", "Rock Toad", "Cave Beetle",
            "Underground Eel", "Dark Wolf", "Crystal Beetle", "Dust Spider", "Mole",
            "Burrow Snake", "Night Bat", "Shadow Hound", "Deep Mole", "Rock Lizard",
            "Stone Rat", "Mushroom Beetle", "Cave Crab", "Dark Crow", "Blind Serpent"
        ],
        "forage": [
            "Glow Mushroom", "Shadow Moss", "Darkroot", "Crystal Moss", "Blind Mushroom",
            "Cave Moss", "Stone Fungus", "Night Fern", "Glow Fern", "Tunnel Root",
            "Bat Guano Fungus", "Deep Mushroom", "Shadow Herb", "Earth Fungus", "Dust Root",
            "Crystal Flower", "Dark Moss", "Wet Moss", "Stone Root", "Glow Berry",
            "Root Vine", "Cave Mint", "Shadow Flower", "Black Fungus", "Dark Fern"
        ]
    },

    "damp_cave": {
        "animals": [
            "Frog", "Salamander", "Bat", "Mud Crab", "Cave Spider",
            "Leech", "Blind Fish", "Water Snake", "Rock Toad", "Mushroom Beetle",
            "Tunnel Rat", "Wet Lizard", "Cave Eel", "Dark Bat", "Mud Beetle",
            "Swamp Cat", "River Crab", "Stone Snake", "Cave Frog", "Wet Hound",
            "Otter", "Mud Spider", "Shadow Toad", "Bog Rat", "Water Beetle"
        ],
        "forage": [
            "Wet Moss", "Glow Mushroom", "Mud Fern", "Cave Moss", "Water Root",
            "Shadow Herb", "River Bulb", "Duckweed", "Darkroot", "Tunnel Root",
            "Bog Flower", "Mire Blossom", "Glow Fern", "Stone Fungus", "Wet Bark",
            "Frogwort", "Mud Mushroom", "Leech Vine", "Crystal Moss", "Water Fern",
            "Cave Mint", "Swamp Mint", "Earth Fungus", "Mud Root", "Shadow Moss"
        ]
    },

    "deep_cave": {
        "animals": [
            "Deep Bat", "Blind Serpent", "Stone Drake", "Cave Bear", "Shadow Spider",
            "Crystal Beetle", "Dark Wolf", "Underground Eel", "Rock Scorpion", "Tunnel Snake",
            "Deep Mole", "Shadow Hound", "Cave Crab", "Mushroom Beetle", "Blind Fish",
            "Night Bat", "Stone Rat", "Burrow Snake", "Dark Cat", "Cave Lizard",
            "Crystal Spider", "Rock Toad", "Shadow Crow", "Deep Scorpion", "Earth Drake"
        ],
        "forage": [
            "Glow Mushroom", "Crystal Moss", "Deep Mushroom", "Darkroot", "Shadow Moss",
            "Earth Fungus", "Stone Fungus", "Glow Fern", "Black Fungus", "Crystal Flower",
            "Tunnel Root", "Cave Moss", "Night Fern", "Shadow Herb", "Dark Moss",
            "Stone Root", "Glow Berry", "Root Vine", "Blind Mushroom", "Dust Root",
            "Earth Root", "Crystal Fern", "Deep Moss", "Shadow Flower", "Cave Mint"
        ]
    },

    "hell": {
        "animals": [
            "Hell Hound", "Fire Imp", "Ash Serpent", "Demon Boar", "Flame Bat",
            "Inferno Spider", "Lava Drake", "Cinder Wolf", "Bone Vulture", "Soul Rat",
            "Magma Toad", "Burning Scorpion", "Smoke Wyrm", "Ash Crow", "Blister Beetle",
            "Char Hound", "Pit Serpent", "Ember Fox", "Infernal Goat", "Coal Spider",
            "Blood Hawk", "Fire Beetle", "Doom Rat", "Cinder Cat", "Flame Snake"
        ],
        "forage": [
            "Ash Root", "Fire Moss", "Cinder Flower", "Burnroot", "Sulfur Weed",
            "Blister Pod", "Coal Mushroom", "Ember Seed", "Scorchleaf", "Lava Bloom",
            "Inferno Herb", "Heat Root", "Smoke Blossom", "Ash Berry", "Char Moss",
            "Flame Petal", "Bloodroot", "Magma Flower", "Cinder Seed", "Fire Pepper",
            "Smoke Herb", "Hell Fern", "Soul Mushroom", "Obsidian Fungus", "Ash Bark"
        ]
    },

    "city": {
        "animals": [
            "Rat", "Pigeon", "Stray Dog", "Cat", "Crow",
            "Horse", "Mule", "Goat", "Chicken", "Pig",
            "Guard Hound", "Stable Mouse", "Street Fox", "Raven", "Ferret",
            "Messenger Hawk", "Dock Rat", "Alley Cat", "Pack Mule", "Watch Dog",
            "Sewer Rat", "Market Goat", "Stable Cat", "Street Crow", "Courier Pigeon"
        ],
        "forage": [
            "Apple", "Onion", "Garlic", "Turnip", "Cabbage",
            "Barley", "Wheat", "Herbs", "Mint", "Parsley",
            "Leek", "Carrot", "Potato", "Berry", "Mushroom",
            "Bread Crust", "Ale Hops", "Street Herbs", "Dry Beans", "Walnut",
            "Hazelnut", "Market Spice", "Sunflower Seed", "Dried Fruit", "Cheese Herb"
        ]
    },

    "farm": {
        "animals": [
            "Cow", "Chicken", "Pig", "Horse", "Goat",
            "Sheep", "Dog", "Cat", "Duck", "Goose",
            "Ox", "Donkey", "Mule", "Barn Rat", "Rooster",
            "Turkey", "Farm Hound", "Stable Cat", "Field Mouse", "Rabbit",
            "Pony", "Ram", "Milk Cow", "Work Horse", "Barn Owl"
        ],
        "forage": [
            "Wheat", "Barley", "Corn", "Carrot", "Potato",
            "Turnip", "Cabbage", "Apple", "Berry", "Herbs",
            "Mint", "Parsley", "Onion", "Garlic", "Leek",
            "Hay", "Sunflower Seed", "Dry Beans", "Oats", "Pumpkin",
            "Squash", "Wild Carrot", "Walnut", "Hazelnut", "Mushroom"
        ]
    }
}

# ============================================================
# REGION (specific animals with curated droplists + special forage)
# ============================================================

REGION = {
    "grassland": {
        "animal": ["Rabbit", "Fox", "Snake", "Crow", "Wolf"],
        "droplists": [
            ["Rabbit Fur", "Rabbit Foot"],
            ["Fox Fur", "Sharp Fang"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Crow Feather", "Black Feather"],
            ["Wolf Fang", "Wolf Pelt"]
        ],
        "forage": [
            "Storm Herb", "Mana Herb", "Moonroot", "Sunroot", "Wildroot",
            "Golden Herb", "Morning Dew", "Silver Leaf", "Thornvine", "Bitterroot"
        ]
    },

    "shrubland": {
        "animal": ["Snake", "Crow", "Scorpion", "Fox", "Spider"],
        "droplists": [
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Crow Feather", "Black Feather"],
            ["Giant Scorpion Venom", "Scorpion Stinger"],
            ["Fox Fur", "Sharp Fang"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"]
        ],
        "forage": [
            "Nightshade", "Storm Herb", "Moonleaf", "Wilted Herb", "Thornvine Sap",
            "Shadow Vine", "Wildroot", "Toxic Petal", "Moonroot", "Blight Petal"
        ]
    },

    "swamp": {
        "animal": ["Plague Rat", "Spider", "Toad", "Snake", "Carrion Beetle"],
        "droplists": [
            ["Plague Rat Liver", "Diseased Rat Tail", "Rat King Tail"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Paralytic Toad Skin", "Toad Slime"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Carrion Beetle Shell", "Rot Beetle Shell"]
        ],
        "forage": [
            "Bog Moss", "Swamp Mold", "Murkweed", "Darkwater Slime", "Rot Fungus",
            "Rot Mushroom", "Bog Water", "Swamp Gas Vial", "Murkwater Essence", "Carrion Worm Ichor"
        ]
    },

    "marsh": {
        "animal": ["Toad", "Snake", "Crow", "Spider", "Rat"],
        "droplists": [
            ["Paralytic Toad Skin", "Toad Slime"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Crow Feather", "Black Feather"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Diseased Rat Tail", "Rat Tail"]
        ],
        "forage": [
            "Bog Moss", "Hollow Reed", "Murkweed", "Rotwater", "Swamp Mold",
            "Nightshade", "Tainted Water", "Pale Moss", "Moldy Bark", "Decay Fungus"
        ]
    },

    "bog": {
        "animal": ["Plague Rat", "Toad", "Spider", "Snake", "Carrion Maggot"],
        "droplists": [
            ["Plague Rat Liver", "Diseased Rat Tail", "Rat King Tail"],
            ["Paralytic Toad Skin", "Toad Slime"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Carrion Maggot", "Carrion Worm Ichor"]
        ],
        "forage": [
            "Bog Moss", "Bog Water", "Rot Fungus", "Swamp Gas Vial", "Rot Mushroom",
            "Darkwater Slime", "Murkweed", "Fungal Paste", "Blight Petal", "Toxic Sap"
        ]
    },

    "desert": {
        "animal": ["Giant Scorpion", "Snake", "Vulture", "Lizard", "Coyote"],
        "droplists": [
            ["Giant Scorpion Venom", "Scorpion Stinger"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Carrion Feather", "Bone Dust"],
            ["Lizard Tail", "Scaled Hide"],
            ["Coyote Fang", "Wild Fur"]
        ],
        "forage": [
            "Sulfur Ash", "Fire Salts", "Rock Salt", "Dragon Pepper", "Emberleaf",
            "Charcoal Root", "Prismatic Salt", "Chaos Ember", "Sun Ember", "Time Sand"
        ]
    },

    "tundra": {
        "animal": ["Snow Wolf", "Winter Wolf", "Ice Mephit", "Polar Hare", "Owl"],
        "droplists": [
            ["Snow Wolf Fur", "Winter Wolf Fang"],
            ["Winter Wolf Fang", "Frozen Pelt"],
            ["Ice Mephit Shard", "Ice Mephit Dust"],
            ["White Fur", "Frozen Meat"],
            ["Owl Feather", "Night Eye"]
        ],
        "forage": [
            "Wintermint", "Snow Lotus", "Frozen Sap", "Ice Crystal", "Frost Crystal",
            "Frozen Thorn", "Frost Needle", "Snow Moss", "Frozen Water Essence", "Chilled Water Essence"
        ]
    },

    "hills": {
        "animal": ["Goat", "Fox", "Wolf", "Crow", "Eagle"],
        "droplists": [
            ["Goat Horn", "Tough Hide"],
            ["Fox Fur", "Sharp Fang"],
            ["Wolf Fang", "Wolf Pelt"],
            ["Crow Feather", "Black Feather"],
            ["Eagle Feather", "Sky Talon"]
        ],
        "forage": [
            "Stone Dust", "Earth Crystal", "Wildroot", "Granite Dust", "Moonleaf",
            "Oak Sap", "Storm Herb", "Root Resin", "Iron Bark", "Silver Thorn"
        ]
    },

    "mountain": {
        "animal": ["Eagle", "Mountain Goat", "Wyvern", "Wolf", "Bat"],
        "droplists": [
            ["Eagle Feather", "Sky Talon"],
            ["Mountain Horn", "Thick Hide"],
            ["Wyvern Venom", "Wyvern Scale", "Dragon Coal"],
            ["Wolf Fang", "Wolf Pelt"],
            ["Bat Wing", "Echo Fang"]
        ],
        "forage": [
            "Granite Shard", "Obsidian Shard", "Storm Crystal", "Earth Crystal", "Iron Oak Bark",
            "Thunderstone", "Meteor Fragment", "Dragon Coal", "Rock Salt", "Sky Feather"
        ]
    },

    "alpine": {
        "animal": ["Snow Wolf", "Mountain Goat", "Eagle", "Ice Mephit", "Hawk"],
        "droplists": [
            ["Snow Wolf Fur", "Winter Wolf Fang"],
            ["Mountain Horn", "Thick Hide"],
            ["Eagle Feather", "Sky Talon"],
            ["Ice Mephit Shard", "Ice Mephit Dust"],
            ["Sky Feather", "Sharp Talon"]
        ],
        "forage": [
            "Snow Lotus", "Wintermint", "Frost Crystal", "Moonleaf", "Sky Feather",
            "Ice Bark", "Storm Crystal", "Celestial Water", "Silver Thorn", "Moonwater"
        ]
    },

    "volcano": {
        "animal": ["Fire Elemental", "Ash Drake", "Magma Serpent", "Bat", "Hell Hound"],
        "droplists": [
            ["Fire Elemental Ember", "Fire Elemental Ash"],
            ["Ash Scale", "Volcanic Fang"],
            ["Lava Core", "Molten Scale"],
            ["Bat Wing", "Echo Fang"],
            ["Hellfire Ember", "Burning Fang"]
        ],
        "forage": [
            "Sulfur Ash", "Lava Salt", "Fire Elemental Ember", "Volatile Ember", "Wildfire Ember",
            "Obsidian Dust", "Ash Resin", "Flame Oil", "Fire Bloom", "Chaos Ember"
        ]
    },

    "river": {
        "animal": ["Fish", "Frog", "Otter", "Snake", "Heron"],
        "droplists": [
            ["Fish Oil", "Fish Scale"],
            ["Frog Leg", "Wet Skin"],
            ["Otter Fur", "River Claw"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Heron Feather", "Wet Plume"]
        ],
        "forage": [
            "Charged Water", "Rainwater", "Pure Spring Water", "Moonwater", "Hollow Reed",
            "River Moss", "Celestial Water", "Morning Dew", "Storm Water", "Ethereal Water"
        ]
    },

    "lake": {
        "animal": ["Fish", "Frog", "Water Snake", "Heron", "Otter"],
        "droplists": [
            ["Fish Oil", "Fish Scale"],
            ["Frog Leg", "Wet Skin"],
            ["Snake Venom", "River Fang"],
            ["Heron Feather", "Wet Plume"],
            ["Otter Fur", "River Claw"]
        ],
        "forage": [
            "Moonwater", "Charged Water", "Pure Spring Water", "Lake Moss", "Hollow Reed",
            "Morning Dew", "Celestial Water", "Spirit Water", "Pale Moss", "Starwater"
        ]
    },

    "sea": {
        "animal": ["Shark", "Crab", "Sea Serpent", "Gull", "Jellyfish"],
        "droplists": [
            ["Shark Tooth", "Sea Hide"],
            ["Crab Shell", "Sea Claw"],
            ["Sea Serpent Scale", "Abyssal Fang"],
            ["Sea Feather", "Salted Wing"],
            ["Jelly Venom", "Glow Gel"]
        ],
        "forage": [
            "Black Pearl Dust", "Sea Moss", "Salt Crystal", "Storm Water", "Charged Water",
            "Abyssal Shard", "Celestial Water", "Void Essence", "Prismatic Salt", "Spirit Water"
        ]
    },

    "ocean": {
        "animal": ["Kraken", "Shark", "Sea Serpent", "Whale", "Jellyfish"],
        "droplists": [
            ["Kraken Tentacle", "Abyssal Ink"],
            ["Shark Tooth", "Sea Hide"],
            ["Sea Serpent Scale", "Abyssal Fang"],
            ["Whale Oil", "Massive Bone"],
            ["Jelly Venom", "Glow Gel"]
        ],
        "forage": [
            "Black Pearl Dust", "Abyssal Shard", "Void Essence", "Storm Water", "Sea Moss",
            "Charged Water", "Celestial Water", "Prismatic Salt", "Starwater", "Ghost Salt"
        ]
    },

    "small_cave": {
        "animal": ["Bat", "Spider", "Rat", "Snake", "Goblin"],
        "droplists": [
            ["Bat Wing", "Echo Fang"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Diseased Rat Tail", "Rat Tail"],
            ["Snake Fang", "Snake Venom", "Shed Snake Skin"],
            ["Goblin Ear", "Crude Dagger"]
        ],
        "forage": [
            "Cave Moss", "Glow Fungus", "Stone Dust", "Bat Wing", "Spider Silk",
            "Fungus Spores", "Grave Fungus", "Acid Slime", "Shadow Moss", "Crystal Shard"
        ]
    },

    "large_cave": {
        "animal": ["Bat", "Spider", "Troll", "Displacer Beast", "Ghoul"],
        "droplists": [
            ["Bat Wing", "Echo Fang"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Troll Fat", "Troll Bone"],
            ["Displacer Beast Eye", "Shadow Hide"],
            ["Ghoul Fingernail", "Necrotic Flesh"]
        ],
        "forage": [
            "Crystal Shard", "Glow Fungus", "Necrotic Ash", "Void Dust", "Shadow Moss",
            "Grave Fungus", "Acid Crystal", "Dark Ash", "Obsidian Dust", "Cave Moss"
        ]
    },

    "dark_cave": {
        "animal": ["Wraith", "Ghast", "Spider", "Bat", "Mind Flayer"],
        "droplists": [
            ["Wraith Essence", "Wraith Bone Fragment"],
            ["Ghast Saliva", "Rotten Tongue"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Bat Wing", "Echo Fang"],
            ["Mind Flayer Tentacle", "Mind Flayer Residue", "Psychic Brain Tissue"]
        ],
        "forage": [
            "Shadow Moss", "Dream Fungus", "Void Dust", "Necrotic Ash", "Ghost Orchid",
            "Dark Essence", "Nightshade", "Brain Fungus", "Shadow Crystal", "Nether Moss"
        ]
    },

    "damp_cave": {
        "animal": ["Toad", "Spider", "Bat", "Slime", "Rat"],
        "droplists": [
            ["Paralytic Toad Skin", "Toad Slime"],
            ["Spider Venom", "Spider Silk", "Spider Egg Sac"],
            ["Bat Wing", "Echo Fang"],
            ["Acid Slime", "Rot Slime", "Distorted Slime"],
            ["Diseased Rat Tail", "Rat Tail"]
        ],
        "forage": [
            "Glow Fungus", "Pale Moss", "Acid Slime", "Darkwater Slime", "Rot Fungus",
            "Moldy Bark", "Fungal Paste", "Spider Egg Sac", "Cave Moss", "Murkwater Essence"
        ]
    },

    "deep_cave": {
        "animal": ["Mind Flayer", "Wraith", "Ghoul", "Displacer Beast", "Shadow Spider"],
        "droplists": [
            ["Mind Flayer Tentacle", "Mind Flayer Residue", "Psychic Brain Tissue"],
            ["Wraith Essence", "Wraith Bone Fragment"],
            ["Ghoul Fingernail", "Necrotic Flesh"],
            ["Displacer Beast Eye", "Shadow Hide"],
            ["Shadow Silk", "Shadow Venom"]
        ],
        "forage": [
            "Void Crystal", "Nether Moss", "Psychic Residue", "Dream Fungus", "Shadow Ember",
            "Ghost Orchid", "Abyssal Shard", "Necrotic Dust", "Dark Essence", "Chaos Crystal"
        ]
    },

    "hell": {
        "animal": ["Demon", "Hell Hound", "Fire Elemental", "Imp", "Shadow Beast"],
        "droplists": [
            ["Demon Blood Drop", "Demon Ichor"],
            ["Hellfire Ember", "Burning Fang"],
            ["Fire Elemental Ember", "Fire Elemental Ash"],
            ["Imp Horn", "Sulfur Ash"],
            ["Shadow Essence", "Shadow Claw"]
        ],
        "forage": [
            "Demon Blood Drop", "Demon Ichor", "Hellfire Ember", "Shadow Flame Residue", "Void Crystal",
            "Chaos Ember", "Lava Core", "Sulfur Crystal", "Dark Ash", "Nether Oil"
        ]
    },

    "city": {
        "animal": ["Rat", "Crow", "Cat", "Dog", "Pigeon"],
        "droplists": [
            ["Diseased Rat Tail", "Rat Tail"],
            ["Crow Feather", "Black Feather"],
            ["Cat Fur", "Sharp Claw"],
            ["Dog Fang", "Dog Fur"],
            ["Gray Feather", "Small Bone"]
        ],
        "forage": [
            "Copper Powder", "Silver Dust", "Iron Shavings", "Black Ink", "Enchanted Ink",
            "Glass Shard", "Mirror Shard", "Arcane Powder", "Black Candle Wax", "Smog Essence"
        ]
    },

    "farm": {
        "animal": ["Cow", "Pig", "Chicken", "Horse", "Goat"],
        "droplists": [
            ["Leather Hide", "Cow Horn"],
            ["Pig Fat", "Boar Tusk"],
            ["Chicken Feather", "Chicken Bone"],
            ["Horse Hair", "Strong Hide"],
            ["Goat Horn", "Tough Hide"]
        ],
        "forage": [
            "Healing Herb", "Oak Bark", "Golden Nectar", "Moon Herb", "Blessed Herb",
            "Faith Herb", "Wildroot", "Root Vine", "Bitterroot", "Growth Seed"
        ]
    }
}

# ============================================================
# ENSURE ALL REGION NAMES EXIST IN REGIONS
# ============================================================

DEFAULT_REGION_DATA = REGIONS["grassland"]

ALL_REGION_NAMES = [
    "grassland", "shrubland", "swamp", "marsh", "bog",
    "desert", "tundra", "hills", "mountain", "alpine",
    "volcano", "river", "lake", "sea", "ocean",
    "small_cave", "large_cave", "dark_cave", "damp_cave", "deep_cave",
    "hell", "city", "farm"
]

for _rname in ALL_REGION_NAMES:
    if _rname not in REGIONS:
        REGIONS[_rname] = deepcopy(DEFAULT_REGION_DATA)

# ============================================================
# MERGE REGION DROPLISTS INTO REGIONS
# Each animal in REGIONS gets a droplist:
#   - From REGION if a specific droplist exists for that animal
#   - Auto-generated via auto_droplist() otherwise
# Also stores special_forage from REGION for use in forage droplists.
# ============================================================

for _rname, _data in REGIONS.items():
    _spec = REGION.get(_rname, {})
    _spec_map = dict(zip(_spec.get("animal", []), _spec.get("droplists", [])))
    _data["droplists"] = [
        _spec_map[a] if a in _spec_map else auto_droplist(a)
        for a in _data["animals"]
    ]
    _data["special_forage"] = _spec.get("forage", [])

# ============================================================
# UNUSED INGREDIENT SOURCES
# ============================================================

UNUSED_INGREDIENT_SOURCES = {
    "Arcane Cloth": "Mage Shopkeeper",
    "Arcane Oil": "Enchanter Shopkeeper",
    "Arcane Prism": "Ancient Ruins Chest",
    "Arcane Resin": "Mage Tower Loot",
    "Astral Crystal": "Astral Boss Drop",
    "Astral Shard": "Planar Creature Drop",
    "Barrier Crystal": "Guardian Construct Drop",
    "Blessed Iron": "Temple Blacksmith",
    "Blink Dog Fur": "Blink Dog Monster Drop",
    "Bloom Petal": "Druid Shopkeeper",
    "Celestial Bloom": "Celestial Creature Drop",
    "Celestial Crystal": "Angel Boss Drop",
    "Chaos Salt": "Chaos Rift Loot",
    "Chrono Moss": "Time Dungeon Forage",
    "Crystal Bloom": "Crystal Cave Forage",
    "Crystal Core": "Crystal Golem Drop",
    "Cyclone Seed": "Storm Elemental Drop",
    "Diamond Dust": "Jeweler Shopkeeper",
    "Divine Ink": "Temple Scribe Vendor",
    "Dream Eater Venom": "Dream Eater Monster Drop",
    "Earth Core": "Earth Elemental Boss Drop",
    "Elder Crystal": "Ancient Dragon Hoard",
    "Enchanted Leather": "Magic Leatherworker",
    "Ether Bloom": "Ethereal Plane Forage",
    "Ether Crystal": "Void Entity Drop",
    "Ether Oil": "Alchemist Shopkeeper",
    "Fear Essence": "Nightmare Creature Drop",
    "Fey Essence": "Fey Creature Drop",
    "Fey Mushroom": "Fairy Grove Forage",
    "Force Essence": "Arcane Construct Drop",
    "Ghost Salt": "Crypt Loot",
    "Glass Shard": "City Forage",
    "Grace Flower": "Temple Garden Forage",
    "Guardian Gem": "Guardian Boss Drop",
    "Guardian Stone": "Ancient Sentinel Drop",
    "Hailstone Core": "Ice Elemental Drop",
    "Healing Bloom": "Healer Shopkeeper",
    "Holy Ember": "Phoenix Creature Drop",
    "Hourglass Dust": "Ancient Tomb Loot",
    "Illusion Dust": "Illusionist Vendor",
    "Justice Root": "Paladin Order Vendor",
    "Light Essence": "Holy Shrine Reward",
    "Living Vine": "Living Plant Monster Drop",
    "Mana Bloom": "Arcane Forest Forage",
    "Mana Crystal": "Mage Guild Vendor",
    "Mana Oil": "Alchemist Vendor",
    "Meteor Fragment": "Meteor Crash Event",
    "Mirror Image Dust": "Illusion Boss Drop",
    "Moon Cloth": "Moon Priest Vendor",
    "Mystic Moss": "Enchanted Cave Forage",
    "Necrotic Dust": "Lich Monster Drop",
    "Nightmare Oil": "Night Hag Drop",
    "Painroot": "Torture Dungeon Forage",
    "Phase Crystal": "Phase Beast Drop",
    "Phantom Essence": "Phantom Monster Drop",
    "Phoenix Ash": "Phoenix Boss Drop",
    "Phoenix Feather": "Phoenix Boss Drop",
    "Planar Shard": "Planar Rift Loot",
    "Prayer Beads": "Temple Vendor",
    "Prism Crystal": "Rainbow Cavern Loot",
    "Pure Mana Crystal": "Archmage Boss Drop",
    "Radiant Crystal": "Holy Temple Reward",
    "Radiant Dust": "Cleric Vendor",
    "Rainbow Petal": "Fey Garden Forage",
    "Reflective Dust": "Mirror Wraith Drop",
    "Renewal Seed": "World Tree Forage",
    "Rift Dust": "Void Rift Event",
    "Runic Dust": "Runesmith Vendor",
    "Sacred Flame Oil": "High Priest Vendor",
    "Sanctified Oil": "Temple Vendor",
    "Sanctuary Bloom": "Sacred Grove Forage",
    "Shield Moss": "Fortress Ruin Forage",
    "Sphere Crystal": "Arcane Sphere Construct Drop",
    "Spirit Flame": "Spirit Boss Drop",
    "Star Dust": "Falling Star Event",
    "Storm Orb": "Storm Titan Drop",
    "Sunstone": "Desert Temple Loot",
    "Sunstone Fragment": "Solar Elemental Drop",
    "Tear of Mercy": "Angel NPC Reward",
    "Thunder Feather": "Thunderbird Monster Drop",
    "Thunder Herb": "Storm Plains Forage",
    "Thunder Crystal": "Storm Elemental Boss Drop",
    "Time Sand": "Ancient Hourglass Dungeon Loot",
    "Tremor Stone": "Earth Titan Drop",
    "Veil Moss": "Shadow Forest Forage",
    "Void Stone": "Void Creature Drop",
    "Wardstone": "Mage Fortress Loot",
    "Wild Magic Residue": "Wild Mage Enemy Drop",
    "Wind Essence": "Air Elemental Drop"
}

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
    "shield": {"suffix": "Shield", "inventorySlot": "shield"},
    "head":   {"suffix": "Helmet", "inventorySlot": "head"},
    "neck":   {"suffix": "Necklace", "inventorySlot": "neck"},
    "body":   {"suffix": "Armor", "inventorySlot": "body"},
    "hand":   {"suffix": "Gloves", "inventorySlot": "hand"},
    "feet":   {"suffix": "Boots", "inventorySlot": "feet"}
}

# ============================================================
# WEAPON TYPES
# ============================================================

WEAPON_TYPES = [
    "Sword", "Shortsword", "Battleaxe", "Handaxe", "Club",
    "Staff", "Wand", "Mace", "Dagger", "Trident",
    "Whip", "Spear"
]

# ============================================================
# CATEGORY HELPERS
# ============================================================

def create_weapon_category(guild):
    return {
        "id": f"crafted_weapon_{guild}",
        "name": f"Crafted {guild.title()} Weapons",
        "actionType": "equip",
        "size": "large",
        "inventorySlot": "weapon"
    }

def create_scroll_category(guild):
    return {
        "id": f"crafted_scroll_{guild}",
        "name": f"Crafted {guild.title()} Scroll",
        "actionType": "use"
    }

def create_potion_category(guild):
    return {
        "id": f"crafted_potion_{guild}",
        "name": f"Crafted {guild.title()} Potion",
        "actionType": "use"
    }

def create_armor_category(guild, slot):
    slot_info = ARMOR_SLOT_DATA[slot]
    return {
        "id": f"crafted_{slot}_{guild}",
        "name": f"Crafted {guild.title()} {slot_info['suffix']}",
        "actionType": "equip",
        "size": "large",
        "inventorySlot": slot_info["inventorySlot"]
    }

# ============================================================
# BASE ITEM CATEGORIES
# ============================================================

ITEMCATEGORIES["animal"] = [{"id": "animal_parts", "name": "Animal Parts"}]
ITEMCATEGORIES["forage"] = [{"id": "forage_ingredients", "name": "Forage Ingredients"}]
ITEMCATEGORIES["mining"] = [
    {"id": "mining_ingredients", "name": "Mining Ingredients"},
    {"id": "mining_tools", "name": "Mining Tools", "actionType": "equip", "inventorySlot": "weapon"}
]
ITEMCATEGORIES["gardening"] = [
    {"id": "garden_ingredients", "name": "Garden Ingredients"},
    {"id": "garden_fresh", "name": "Fresh Garden Food", "actionType": "use"},
    {"id": "garden_tools", "name": "Garden Tools", "actionType": "equip", "inventorySlot": "weapon"}
]
ITEMCATEGORIES["spell_materials"] = [
    {"id": "spell_materials", "name": "Spell Materials"}
]
ITEMCATEGORIES["crafting_materials"] = [
    {"id": "crafting_materials", "name": "Crafting Materials"}
]

# ============================================================
# SPELL GUILDS
# ============================================================

SPELL_GUILDS = ["mage", "cleric", "druid"]

for guild in SPELL_GUILDS:
    ITEMCATEGORIES[guild] = []
    ITEMCATEGORIES[guild].append(create_weapon_category(guild))
    ITEMCATEGORIES[guild].append(create_scroll_category(guild))
    ITEMCATEGORIES[guild].append(create_potion_category(guild))
    for slot in ARMOR_SLOT_DATA.keys():
        ITEMCATEGORIES[guild].append(create_armor_category(guild, slot))

# ============================================================
# AILMENTS
# ============================================================

AILMENTS = [
    "Blight Fever", "Rotting Curse", "Plague Touch", "Venom Shock", "Frostbite",
    "Hellfire Burn", "Mind Rot", "Soul Drain", "Blood Curse", "Weakening Hex",
    "Shadow Plague", "Dark Paralysis", "Poison Blood", "Spirit Sickness", "Bone Decay",
    "Disease Cloud", "Chaos Fever", "Lung Rot", "Pestilence", "Curse of Agony",
    "Death Mark", "Nightmare Toxin", "Decay Touch", "Rotting Venom", "Chaotic Doom"
]

# FIXED: was [ (list), must be { (dict)
AILMENT_INGREDIENTS = {
    "Blight Fever":    ["Diseased Rat Tail", "Rot Mushroom", "Bog Water", "Grave Dust", "Black Salt"],
    "Rotting Curse":   ["Ghoul Fingernail", "Corpse Flower Petal", "Necrotic Ash", "Bat Wing", "Tainted Blood"],
    "Plague Touch":    ["Plague Rat Liver", "Swamp Mold", "Spider Venom", "Bone Dust", "Murkwater Essence"],
    "Venom Shock":     ["Giant Scorpion Venom", "Shock Beetle Carapace", "Copper Powder", "Snake Fang", "Storm Herb"],
    "Frostbite":       ["Ice Mephit Shard", "Wintermint", "Frost Crystal", "Snow Lotus", "Chilled Water Essence"],
    "Hellfire Burn":   ["Fire Elemental Ember", "Sulfur Ash", "Demon Blood Drop", "Charcoal Root", "Lava Salt"],
    "Mind Rot":        ["Mind Flayer Tentacle", "Dream Fungus", "Shadow Moss", "Nightshade", "Psychic Residue"],
    "Soul Drain":      ["Specter Essence", "Grave Lily", "Black Pearl Dust", "Wraith Bone Fragment", "Hollow Ash"],
    "Blood Curse":     ["Vampire Fang", "Blood Rose", "Crimson Moss", "Iron Shavings", "Cursed Ink"],
    "Weakening Hex":   ["Hag Hair", "Wilted Herb", "Dust of Decay", "Crow Feather", "Moonroot"],
    "Shadow Plague":   ["Shadow Essence", "Rot Fungus", "Obsidian Dust", "Darkwater Slime", "Raven Eye"],
    "Dark Paralysis":  ["Ghast Saliva", "Nightshade Oil", "Spider Silk", "Shadow Root", "Paralytic Toad Skin"],
    "Poison Blood":    ["Wyvern Venom", "Hemlock Leaf", "Diseased Tick", "Bitterroot", "Rotten Heartseed"],
    "Spirit Sickness": ["Ghost Orchid", "Spirit Dust", "Hollow Reed", "Ethereal Water", "Pale Moss"],
    "Bone Decay":      ["Crushed Skeleton Bone", "Acid Slime", "Grave Fungus", "Carrion Worm Ichor", "Bone Meal"],
    "Disease Cloud":   ["Plague Spore Pod", "Swamp Gas Vial", "Moldy Bark", "Rot Beetle Shell", "Murkweed"],
    "Chaos Fever":     ["Wild Magic Residue", "Fey Mushroom", "Chaos Crystal", "Emberleaf", "Distorted Slime"],
    "Lung Rot":        ["Ashen Mold", "Smog Essence", "Diseased Lung Tissue", "Blackroot", "Fungus Spores"],
    "Pestilence":      ["Rat King Tail", "Carrion Maggot", "Tainted Water", "Grave Soil", "Blight Petal"],
    "Curse of Agony":  ["Tortured Soul Essence", "Thornvine Sap", "Black Candle Wax", "Painroot", "Crimson Thorn"],
    "Death Mark":      ["Assassin Vine Sap", "Black Ink", "Raven Feather", "Shadow Crystal", "Grave Dust"],
    "Nightmare Toxin": ["Dream Eater Venom", "Nightshade Berry", "Shadow Orchid", "Fear Essence", "Moon Ash"],
    "Decay Touch":     ["Rot Slime", "Carrion Beetle Shell", "Blighted Root", "Necrotic Dust", "Fungal Paste"],
    "Rotting Venom":   ["Snake Venom", "Decayed Mushroom", "Spider Egg Sac", "Rotwater", "Bog Moss"],
    "Chaotic Doom":    ["Chaos Ember", "Demon Ichor", "Void Crystal", "Shadow Flame Residue", "Wild Magic Ash"]
}

ACTORCONDITIONS["ailment"] = []
ITEMLISTS["ailment"] = []

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
    ITEMLISTS["ailment"].append({
        "id": "potion_" + sid(ailment),
        "name": "Potion to cure " + ailment,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 100,
        "category": "pot",
        "description": "A potion to cure illness."
    })

# ============================================================
# ANIMALS — uses merged REGIONS droplists
# Creates actual drop items (not just hides), builds real droplists.
# ============================================================

ITEMLISTS["animal"] = []
MONSTERLISTS["animal"] = []
DROPLISTS["animal"] = []

_SEEN_DROP_IDS = set()

for region, data in REGIONS.items():
    for i, animal in enumerate(data["animals"]):
        animal_id = sid(animal)
        dl_id = f"dl_{region}_{animal_id}"

        droplist_entries = []
        for j, drop_name in enumerate(data["droplists"][i]):
            drop_id = sid(drop_name)
            if drop_id not in _SEEN_DROP_IDS:
                _SEEN_DROP_IDS.add(drop_id)
                ITEMLISTS["animal"].append({
                    "id": drop_id,
                    "name": drop_name,
                    "iconID": ITEM_ICON,
                    "displaytype": "ordinary",
                    "baseMarketCost": 15,
                    "category": "animal_parts",
                    "description": f"A crafting drop from a {animal.lower()}."
                })
            droplist_entries.append({
                "itemID": drop_id,
                "chance": "100" if j == 0 else "50",
                "quantity": {"min": 1, "max": 1 if j == 0 else 2}
            })

        DROPLISTS["animal"].append({
            "id": dl_id,
            "items": droplist_entries
        })

        conditions = []
        for ailment in AILMENTS:
            conditions.append({
                "condition": sid(ailment),
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
            "attackDamage": {"min": 5, "max": 10},
            "moveCost": 5,
            "attackCost": 4,
            "droplist": dl_id,
            "spawnGroup": f"animal_{region.lower()}",
            "faction": "animal",
            "hitEffect": {"conditionsSource": conditions}
        })

# ============================================================
# FORAGE — mundane forage items per region
# ============================================================

ITEMLISTS["forage"] = []

_SEEN_FORAGE_IDS = set()
for region, data in REGIONS.items():
    for forage in data["forage"]:
        iid = f"{region}_{sid(forage)}"
        if iid not in _SEEN_FORAGE_IDS:
            _SEEN_FORAGE_IDS.add(iid)
            ITEMLISTS["forage"].append({
                "id": iid,
                "name": forage,
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "baseMarketCost": 10,
                "category": "forage_ingredients",
                "description": f"A forage ingredient called {forage}."
            })

# ============================================================
# SPECIAL FORAGE — magical/rare forage from REGION
# Also creates the dl_forage_{region} droplists referenced by TMX maps.
# ============================================================

ITEMLISTS["special_forage"] = []
DROPLISTS["special_forage"] = []

_SEEN_SPECIAL_FORAGE_IDS = set()

for region_name, data in REGIONS.items():
    dl_items = []
    for forage_name in data.get("special_forage", []):
        forage_id = sid(forage_name)
        if forage_id not in _SEEN_SPECIAL_FORAGE_IDS:
            _SEEN_SPECIAL_FORAGE_IDS.add(forage_id)
            ITEMLISTS["special_forage"].append({
                "id": forage_id,
                "name": forage_name,
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "baseMarketCost": 30,
                "category": "forage_ingredients",
                "description": f"A rare ingredient found while foraging: {forage_name}."
            })
        dl_items.append({
            "itemID": forage_id,
            "chance": "25",
            "quantity": {"min": 1, "max": 1}
        })
    if dl_items:
        DROPLISTS["special_forage"].append({
            "id": f"dl_forage_{region_name}",
            "items": dl_items
        })

# ============================================================
# MINING
# ============================================================

MINING = [
    "Copper Ore", "Tin Ore", "Iron Ore", "Silver Ore", "Gold Ore",
    "Nickel Ore", "Cobalt Ore", "Lead Ore", "Zinc Ore", "Platinum Ore",
    "Quartz", "Ruby", "Sapphire", "Emerald", "Obsidian",
    "Adamantite", "Adamantine Shard", "Moonstone", "Sunstone", "Opal",
    "Coal", "Sulfur", "Crystal Shard", "Granite", "Marble",
    "Jade", "Bloodstone", "Onyx", "Aquamarine", "Garnet",
    "Pyrite", "Salt Crystal", "Basalt", "Slate", "Flint",
    "Topaz", "Amethyst", "Diamond", "Emerald", "Ruby",
    "Meteorite", "Mithril", "Dragonstone", "Star Metal"
]

ITEMLISTS["mining"] = []
_SEEN_MINING_IDS = set()
for ore in MINING:
    ore_id = sid(ore)
    if ore_id not in _SEEN_MINING_IDS:
        _SEEN_MINING_IDS.add(ore_id)
        ITEMLISTS["mining"].append({
            "id": ore_id,
            "name": ore,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "baseMarketCost": 25,
            "category": "mining_ingredients",
            "description": f"A mining resource called {ore}."
        })

ITEMLISTS["mining"].append({
    "id": "iron_pick_axe",
    "name": "Iron Pick Axe",
    "iconID": ITEM_ICON,
    "displaytype": "ordinary",
    "baseMarketCost": 100,
    "category": "mining_tools",
    "description": "A heavy mining tool.",
    "equipEffect": {"increaseAttackDamage": {"min": 2, "max": 5}}
})
ITEMLISTS["mining"].append({
    "id": "iron_shovel",
    "name": "Iron Shovel",
    "iconID": ITEM_ICON,
    "displaytype": "ordinary",
    "baseMarketCost": 75,
    "category": "mining_tools",
    "description": "A mining tool to dig soil.",
    "equipEffect": {"increaseAttackDamage": {"min": 1, "max": 3}}
})
ITEMLISTS["mining"].append({
    "id": "mining_pan",
    "name": "Mining Pan",
    "iconID": ITEM_ICON,
    "displaytype": "ordinary",
    "baseMarketCost": 50,
    "category": "mining_tools",
    "description": "A pan to mine gold from soil.",
    "equipEffect": {"increaseAttackDamage": {"min": 0, "max": 1}}
})

# ============================================================
# GARDENING
# ============================================================

GARDENING = [
    "Tomato", "Potato", "Corn", "Onion", "Carrot",
    "Radish", "Turnip", "Beet", "Celery", "Leek",
    "Rosemary", "Lavender", "Mint", "Basil", "Pepper",
    "Parsley", "Thyme", "Sage", "Oregano", "Chive",
    "Cabbage", "Pumpkin", "Bean", "Pea", "Apple",
    "Lettuce", "Spinach", "Broccoli", "Cauliflower", "Cucumber",
    "Zucchini", "Squash", "Melon", "Strawberry", "Blueberry",
    "Pear", "Plum", "Berry", "Mushroom", "Garlic"
]

ITEMLISTS["gardening"] = []

for crop in GARDENING:
    crop_id = "garden_" + sid(crop)
    ITEMLISTS["gardening"].append({
        "id": crop_id,
        "name": crop,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 10,
        "category": "garden_fresh",
        "description": f"Fresh {crop.lower()} ready to eat.",
        "useEffect": {"increaseCurrentHP": {"min": 5, "max": 5}}
    })
    ITEMLISTS["gardening"].append({
        "id": f"{crop_id}_seed",
        "name": f"{crop} Seed",
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 3,
        "category": "garden_ingredients",
        "description": f"Seeds used to grow {crop.lower()}."
    })

ITEMLISTS["gardening"].append({
    "id": "iron_hoe",
    "name": "Iron Hoe",
    "iconID": ITEM_ICON,
    "displaytype": "ordinary",
    "baseMarketCost": 75,
    "category": "garden_tools",
    "description": "A gardening hoe weapon.",
    "equipEffect": {"increaseAttackDamage": {"min": 1, "max": 4}}
})

# ============================================================
# SPELL DATA
# ============================================================

SPELL_DATA = {
    "mage": {
        "offensive": [
            "Fireball", "Lightning Bolt", "Magic Missile", "Cone of Cold", "Meteor Swarm",
            "Chain Lightning", "Ice Storm", "Disintegrate", "Finger of Death", "Delayed Blast Fireball",
            "Arcane Burst", "Flame Strike", "Thunder Wave", "Blizzard", "Chaos Bolt",
            "Soul Burn", "Nether Blast", "Shadow Flame", "Astral Spear", "Void Nova",
            "Crystal Lance", "Inferno", "Storm Sphere", "Mind Rupture", "Frost Lance"
        ],
        "defensive": [
            "Mage Armor", "Shield", "Arcane Barrier", "Mirror Image", "Stoneskin",
            "Prismatic Wall", "Mana Shield", "Mystic Ward", "Frost Armor", "Aegis",
            "Temporal Guard", "Crystal Shield", "Arcane Veil", "Energy Barrier", "Soul Ward",
            "Void Shield", "Astral Armor", "Guardian Sphere", "Blink Shield", "Phantom Guard",
            "Ward of Ages", "Mystic Cloak", "Planar Barrier", "Arcane Sanctuary", "Spell Reflection"
        ]
    },
    "cleric": {
        "offensive": [
            "Holy Smite", "Divine Wrath", "Sacred Flame", "Sun Strike", "Judgement",
            "Radiant Burst", "Hammer of Faith", "Exorcism", "Holy Nova", "Celestial Spear",
            "Purge Evil", "Wrath of Dawn", "Consecration", "Divine Lance", "Light Hammer",
            "Blessed Fire", "Faith Bolt", "Holy Storm", "Sunfire", "Sacred Judgement",
            "Heavens Fury", "Radiant Spear", "Divine Flame", "Smite Undead", "Sacred Storm"
        ],
        "defensive": [
            "Divine Shield", "Blessing", "Sanctuary", "Holy Barrier", "Guardian Angel",
            "Sacred Ward", "Healing Aura", "Prayer Shield", "Faith Armor", "Protection",
            "Holy Grace", "Shield of Light", "Blessed Armor", "Celestial Guard", "Redemption",
            "Aegis of Faith", "Divine Protection", "Sacred Veil", "Holy Resistance", "Spirit Ward",
            "Purity", "Shield of Faith", "Light Ward", "Grace of Dawn", "Guardian Prayer"
        ]
    },
    "druid": {
        "offensive": [
            "Thorn Strike", "Poison Bloom", "Natures Wrath", "Vine Lash", "Earthquake",
            "Hurricane", "Wildfire", "Storm Call", "Venom Roots", "Moonfire",
            "Sunstrike", "Entangle", "Nature Bolt", "Oak Smash", "Tornado",
            "Spirit Thorn", "Feral Rage", "Earth Spear", "Bloom Rot", "Nature Shock",
            "Wild Growth", "Forest Fury", "Plague Seeds", "Stone Rain", "Wrath of Beasts"
        ],
        "defensive": [
            "Barkskin", "Nature Shield", "Regrowth", "Spirit Guard", "Earth Ward",
            "Stone Skin", "Healing Roots", "Wild Protection", "Moon Ward", "Forest Veil",
            "Natural Armor", "Oak Shield", "Nature Blessing", "Renewal", "Lifebloom",
            "Ancient Ward", "Storm Barrier", "Wild Grace", "Spirit Bark", "Earth Guard",
            "Feral Shield", "Bloom Shield", "Root Barrier", "Nature Sanctuary", "Beast Ward"
        ]
    }
}

SPELL_INGREDIENTS = {
    "mage": {
        "offensive": {
            "Fireball": ["Fire Elemental Ember", "Sulfur Powder", "Ruby Dust", "Ashwood Bark"],
            "Lightning Bolt": ["Storm Crystal", "Copper Wire", "Thunder Feather", "Spark Moss"],
            "Magic Missile": ["Arcane Crystal", "Pixie Dust", "Silver Thread", "Mana Herb"],
            "Cone of Cold": ["Frost Crystal", "Ice Lotus", "Snow Wolf Fur", "Wintermint"],
            "Meteor Swarm": ["Meteor Fragment", "Dragon Coal", "Obsidian Shard", "Fire Salts"],
            "Chain Lightning": ["Charged Crystal", "Copper Filament", "Storm Essence", "Eagle Feather"],
            "Ice Storm": ["Hailstone Core", "Frost Sap", "Frozen Thorn", "Ice Mephit Dust"],
            "Disintegrate": ["Displacer Beast Eye", "Void Dust", "Acid Crystal", "Necrotic Ash"],
            "Finger of Death": ["Grave Dust", "Wraith Essence", "Black Candle Wax", "Bone Powder"],
            "Delayed Blast Fireball": ["Volatile Ember", "Sulfur Crystal", "Dragon Pepper", "Flame Oil"],
            "Arcane Burst": ["Arcane Powder", "Mana Crystal", "Crystal Bloom", "Silver Dust"],
            "Flame Strike": ["Holy Ember", "Fire Opal", "Ash Resin", "Sunroot"],
            "Thunder Wave": ["Thunderstone", "Bat Wing", "Echo Crystal", "Storm Herb"],
            "Blizzard": ["Ice Crystal", "Snow Lotus", "Frozen Water Essence", "Winter Wolf Fang"],
            "Chaos Bolt": ["Chaos Shard", "Wild Magic Dust", "Fey Essence", "Prismatic Salt"],
            "Soul Burn": ["Soul Ash", "Spirit Flame", "Ghost Orchid", "Shadow Ember"],
            "Nether Blast": ["Void Crystal", "Nether Moss", "Dark Ash", "Obsidian Powder"],
            "Shadow Flame": ["Shadow Ember", "Nightshade Oil", "Black Flame Residue", "Raven Feather"],
            "Astral Spear": ["Astral Crystal", "Moonstone Dust", "Celestial Water", "Silver Thorn"],
            "Void Nova": ["Void Essence", "Black Pearl Dust", "Abyssal Shard", "Chaos Salt"],
            "Crystal Lance": ["Crystal Shard", "Diamond Dust", "Ice Vine", "Arcane Oil"],
            "Inferno": ["Lava Core", "Fire Elemental Ash", "Sulfur Resin", "Charred Bark"],
            "Storm Sphere": ["Storm Orb", "Thunder Crystal", "Charged Water", "Wind Essence"],
            "Mind Rupture": ["Psychic Crystal", "Brain Fungus", "Mind Flayer Residue", "Nightmare Oil"],
            "Frost Lance": ["Frost Needle", "Ice Crystal", "Snow Moss", "Frozen Sap"]
        },
        "defensive": {
            "Mage Armor": ["Arcane Cloth", "Mana Crystal", "Silver Dust", "Enchanted Leather"],
            "Shield": ["Iron Bark", "Arcane Powder", "Guardian Stone", "Shield Moss"],
            "Arcane Barrier": ["Barrier Crystal", "Mana Resin", "Runic Dust", "Spirit Water"],
            "Mirror Image": ["Glass Shard", "Illusion Dust", "Moonwater", "Silver Leaf"],
            "Stoneskin": ["Granite Powder", "Earth Essence", "Troll Fat", "Stone Root"],
            "Prismatic Wall": ["Prism Crystal", "Rainbow Petal", "Mana Oil", "Light Essence"],
            "Mana Shield": ["Pure Mana Crystal", "Arcane Sap", "Mystic Moss", "Ether Bloom"],
            "Mystic Ward": ["Enchanted Ink", "Wardstone", "Arcane Resin", "Silver Thread"],
            "Frost Armor": ["Frost Crystal", "Ice Bark", "Snow Wolf Fur", "Winter Oil"],
            "Aegis": ["Guardian Gem", "Blessed Iron", "Shield Bark", "Holy Water"],
            "Temporal Guard": ["Time Sand", "Hourglass Dust", "Arcane Crystal", "Chrono Moss"],
            "Crystal Shield": ["Crystal Core", "Diamond Dust", "Arcane Resin", "Hardened Sap"],
            "Arcane Veil": ["Veil Moss", "Mana Bloom", "Shadow Silk", "Silver Dust"],
            "Energy Barrier": ["Charged Crystal", "Storm Water", "Arcane Powder", "Force Essence"],
            "Soul Ward": ["Soul Crystal", "Spirit Herb", "Blessed Ash", "Ghost Orchid"],
            "Void Shield": ["Void Stone", "Obsidian Dust", "Dark Essence", "Nether Oil"],
            "Astral Armor": ["Astral Shard", "Moonstone", "Celestial Thread", "Starwater"],
            "Guardian Sphere": ["Sphere Crystal", "Earth Core", "Shield Herb", "Spirit Dust"],
            "Blink Shield": ["Blink Dog Fur", "Arcane Dust", "Phase Crystal", "Ether Oil"],
            "Phantom Guard": ["Phantom Essence", "Ghost Silk", "Moon Ash", "Shadow Crystal"],
            "Ward of Ages": ["Ancient Bark", "Time Sand", "Elder Crystal", "Mystic Water"],
            "Mystic Cloak": ["Shadow Silk", "Mana Thread", "Moon Petal", "Arcane Oil"],
            "Planar Barrier": ["Planar Shard", "Rift Dust", "Ether Crystal", "Void Sap"],
            "Arcane Sanctuary": ["Sanctuary Bloom", "Holy Water", "Mana Crystal", "Spirit Moss"],
            "Spell Reflection": ["Mirror Shard", "Reflective Dust", "Arcane Prism", "Silver Oil"]
        }
    },
    "cleric": {
        "offensive": {
            "Holy Smite": ["Holy Water", "Sunroot", "Radiant Crystal", "Silver Dust"],
            "Divine Wrath": ["Blessed Ash", "Angel Feather", "Celestial Bloom", "Holy Oil"],
            "Sacred Flame": ["Sacred Flame Oil", "Sunroot", "Blessed Wax", "Fire Petal"],
            "Sun Strike": ["Sunstone Fragment", "Golden Herb", "Light Essence", "Radiant Dust"],
            "Judgement": ["Divine Ink", "Holy Water", "Silver Leaf", "Justice Root"],
            "Radiant Burst": ["Radiant Crystal", "Celestial Bloom", "Light Essence", "Blessed Ash"],
            "Hammer of Faith": ["Ironwood Bark", "Holy Water", "Faith Herb", "Silver Dust"],
            "Exorcism": ["Ghost Salt", "Holy Water", "Angel Feather", "Blessed Ash"],
            "Holy Nova": ["Sunstone Fragment", "Radiant Crystal", "Sacred Flame Oil", "Light Essence"],
            "Celestial Spear": ["Celestial Crystal", "Silver Thorn", "Holy Water", "Star Dust"],
            "Purge Evil": ["Purity Herb", "Blessed Ash", "Holy Water", "Silver Dust"],
            "Wrath of Dawn": ["Sunroot", "Radiant Crystal", "Morning Dew", "Light Essence"],
            "Consecration": ["Holy Water", "Blessed Herb", "Sanctified Oil", "Silver Leaf"],
            "Divine Lance": ["Radiant Crystal", "Golden Thorn", "Holy Water", "Blessed Ash"],
            "Light Hammer": ["Sunstone", "Ironwood Bark", "Light Essence", "Silver Dust"],
            "Blessed Fire": ["Sacred Flame Oil", "Phoenix Ash", "Holy Water", "Sunroot"],
            "Faith Bolt": ["Faith Herb", "Radiant Dust", "Silver Thread", "Holy Water"],
            "Holy Storm": ["Storm Crystal", "Holy Water", "Angel Feather", "Light Essence"],
            "Sunfire": ["Sun Ember", "Golden Herb", "Radiant Crystal", "Blessed Oil"],
            "Sacred Judgement": ["Judgement Ink", "Holy Water", "Radiant Dust", "Celestial Bloom"],
            "Heavens Fury": ["Angel Feather", "Storm Crystal", "Sacred Flame Oil", "Light Essence"],
            "Radiant Spear": ["Radiant Crystal", "Silver Thorn", "Holy Water", "Sunroot"],
            "Divine Flame": ["Sacred Flame Oil", "Phoenix Ash", "Light Essence", "Holy Water"],
            "Smite Undead": ["Gravebane Herb", "Holy Water", "Silver Dust", "Radiant Crystal"],
            "Sacred Storm": ["Storm Crystal", "Holy Water", "Angel Feather", "Blessed Ash"]
        },
        "defensive": {
            "Divine Shield": ["Holy Water", "Guardian Bark", "Radiant Crystal", "Blessed Ash"],
            "Blessing": ["Blessed Herb", "Holy Water", "Silver Leaf", "Light Essence"],
            "Sanctuary": ["Sanctuary Moss", "Holy Water", "Radiant Dust", "Celestial Bloom"],
            "Holy Barrier": ["Radiant Crystal", "Blessed Bark", "Holy Water", "Light Essence"],
            "Guardian Angel": ["Phoenix Feather", "Holy Water", "Angel Feather", "Radiant Dust"],
            "Sacred Ward": ["Sacred Herb", "Silver Dust", "Holy Water", "Light Essence"],
            "Healing Aura": ["Healing Bloom", "Holy Water", "Blessed Herb", "Golden Nectar"],
            "Prayer Shield": ["Prayer Beads", "Radiant Crystal", "Holy Water", "Silver Leaf"],
            "Faith Armor": ["Guardian Bark", "Faith Herb", "Holy Water", "Blessed Ash"],
            "Protection": ["Silver Dust", "Holy Water", "Blessed Herb", "Radiant Crystal"],
            "Holy Grace": ["Grace Flower", "Holy Water", "Angel Feather", "Light Essence"],
            "Shield of Light": ["Radiant Crystal", "Sunroot", "Holy Water", "Silver Dust"],
            "Blessed Armor": ["Blessed Iron", "Holy Water", "Guardian Bark", "Radiant Dust"],
            "Celestial Guard": ["Celestial Crystal", "Angel Feather", "Holy Water", "Light Essence"],
            "Redemption": ["Tear of Mercy", "Holy Water", "Blessed Herb", "Silver Leaf"],
            "Aegis of Faith": ["Faith Herb", "Radiant Crystal", "Holy Water", "Guardian Bark"],
            "Divine Protection": ["Blessed Ash", "Holy Water", "Silver Dust", "Light Essence"],
            "Sacred Veil": ["Moon Cloth", "Holy Water", "Radiant Dust", "Blessed Herb"],
            "Holy Resistance": ["Guardian Bark", "Holy Water", "Silver Dust", "Radiant Crystal"],
            "Spirit Ward": ["Spirit Dust", "Holy Water", "Ghost Orchid", "Blessed Ash"],
            "Purity": ["Pure Spring Water", "Silver Leaf", "Blessed Herb", "Light Essence"],
            "Shield of Faith": ["Faith Herb", "Guardian Bark", "Holy Water", "Radiant Crystal"],
            "Light Ward": ["Light Essence", "Holy Water", "Silver Dust", "Blessed Ash"],
            "Grace of Dawn": ["Morning Dew", "Sunroot", "Holy Water", "Radiant Dust"],
            "Guardian Prayer": ["Prayer Beads", "Guardian Bark", "Holy Water", "Angel Feather"]
        }
    },
    "druid": {
        "offensive": {
            "Thorn Strike": ["Thornvine", "Oak Sap", "Wildroot", "Stone Dust"],
            "Poison Bloom": ["Toxic Petal", "Venom Sap", "Nightshade", "Bog Moss"],
            "Natures Wrath": ["Ancient Bark", "Storm Herb", "Earth Crystal", "Wildfire Ember"],
            "Vine Lash": ["Whip Vine", "Oak Sap", "Moonleaf", "Wildroot"],
            "Earthquake": ["Tremor Stone", "Earth Crystal", "Granite Dust", "Root Resin"],
            "Hurricane": ["Wind Essence", "Storm Herb", "Sky Feather", "Rainwater"],
            "Wildfire": ["Wildfire Ember", "Ash Bark", "Sulfur Moss", "Fire Bloom"],
            "Storm Call": ["Storm Crystal", "Charged Water", "Thunder Herb", "Wind Essence"],
            "Venom Roots": ["Venom Sap", "Root Vine", "Spider Venom", "Bog Moss"],
            "Moonfire": ["Moonleaf", "Silver Dust", "Celestial Water", "Spirit Bloom"],
            "Sunstrike": ["Sunroot", "Golden Nectar", "Radiant Petal", "Fire Bloom"],
            "Entangle": ["Living Vine", "Root Resin", "Forest Moss", "Oak Sap"],
            "Nature Bolt": ["Storm Herb", "Wildroot", "Earth Crystal", "Moonleaf"],
            "Oak Smash": ["Iron Oak Bark", "Stone Dust", "Wildroot", "Earth Sap"],
            "Tornado": ["Cyclone Seed", "Wind Essence", "Storm Crystal", "Sky Feather"],
            "Spirit Thorn": ["Ghost Thorn", "Spirit Bloom", "Moonwater", "Silver Vine"],
            "Feral Rage": ["Beast Fang", "Blood Moss", "Wildroot", "Moon Herb"],
            "Earth Spear": ["Earth Crystal", "Stone Dust", "Root Resin", "Granite Shard"],
            "Bloom Rot": ["Rot Seed", "Toxic Petal", "Bog Moss", "Decay Fungus"],
            "Nature Shock": ["Storm Herb", "Charged Sap", "Wildroot", "Earth Crystal"],
            "Wild Growth": ["Growth Seed", "Moonwater", "Ancient Moss", "Earth Sap"],
            "Forest Fury": ["Oak Bark", "Storm Herb", "Beast Fang", "Wildfire Ember"],
            "Plague Seeds": ["Rot Seed", "Blight Petal", "Toxic Sap", "Bog Moss"],
            "Stone Rain": ["Granite Dust", "Earth Crystal", "Storm Water", "Rock Salt"],
            "Wrath of Beasts": ["Alpha Fang", "Blood Moss", "Wildroot", "Moonleaf"]
        },
        "defensive": {
            "Barkskin": ["Barkskin Resin", "Oak Bark", "Stone Dust", "Earth Sap"],
            "Nature Shield": ["Wildroot", "Earth Crystal", "Spirit Bloom", "Ancient Moss"],
            "Regrowth": ["Lifebloom Petal", "Healing Herb", "Moonwater", "Golden Nectar"],
            "Spirit Guard": ["Spirit Bloom", "Ghost Orchid", "Moonwater", "Ancient Moss"],
            "Earth Ward": ["Earth Crystal", "Stone Dust", "Oak Sap", "Wildroot"],
            "Stone Skin": ["Granite Dust", "Earth Sap", "Root Resin", "Stone Moss"],
            "Healing Roots": ["Healing Herb", "Root Vine", "Golden Nectar", "Moonwater"],
            "Wild Protection": ["Wildroot", "Ancient Bark", "Spirit Bloom", "Earth Sap"],
            "Moon Ward": ["Moonleaf", "Silver Dust", "Moonwater", "Spirit Bloom"],
            "Forest Veil": ["Forest Moss", "Shadow Vine", "Moonwater", "Wildroot"],
            "Natural Armor": ["Oak Bark", "Stone Dust", "Root Resin", "Earth Crystal"],
            "Oak Shield": ["Iron Oak Bark", "Earth Sap", "Stone Moss", "Wildroot"],
            "Nature Blessing": ["Healing Herb", "Moonwater", "Spirit Bloom", "Golden Nectar"],
            "Renewal": ["Renewal Seed", "Healing Herb", "Moonwater", "Ancient Moss"],
            "Lifebloom": ["Golden Nectar", "Lifebloom Petal", "Moonwater", "Healing Herb"],
            "Ancient Ward": ["Ancient Bark", "Earth Crystal", "Spirit Bloom", "Stone Dust"],
            "Storm Barrier": ["Charged Bark", "Storm Crystal", "Wind Essence", "Earth Sap"],
            "Wild Grace": ["Moonleaf", "Healing Herb", "Spirit Bloom", "Wildroot"],
            "Spirit Bark": ["Spirit Bloom", "Oak Bark", "Moonwater", "Ancient Moss"],
            "Earth Guard": ["Earth Crystal", "Stone Dust", "Oak Sap", "Wildroot"],
            "Feral Shield": ["Alpha Fang", "Wildroot", "Earth Sap", "Moonleaf"],
            "Bloom Shield": ["Bloom Petal", "Healing Herb", "Spirit Bloom", "Golden Nectar"],
            "Root Barrier": ["Root Vine", "Oak Sap", "Stone Dust", "Earth Crystal"],
            "Nature Sanctuary": ["Sacred Grove Leaf", "Moonwater", "Spirit Bloom", "Ancient Moss"],
            "Beast Ward": ["Alpha Fang", "Wildroot", "Moonleaf", "Earth Sap"]
        }
    }
}

# ============================================================
# SPELL MATERIAL ITEMS
# Create item entries for every unique ingredient in
# AILMENT_INGREDIENTS and SPELL_INGREDIENTS that is not already
# in the animal, forage, mining, or gardening lists.
# ============================================================

ITEMLISTS["spell_materials"] = []
_SEEN_SPELL_MAT_IDS = set()

def _add_spell_material(name):
    iid = sid(name)
    if iid in _SEEN_SPELL_MAT_IDS:
        return
    if iid in _SEEN_DROP_IDS:
        return
    if iid in _SEEN_SPECIAL_FORAGE_IDS:
        return
    # Skip if already a mining item
    if iid in _SEEN_MINING_IDS:
        return
    _SEEN_SPELL_MAT_IDS.add(iid)
    ITEMLISTS["spell_materials"].append({
        "id": iid,
        "name": name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 50,
        "category": "spell_materials",
        "description": f"A rare crafting ingredient: {name}."
    })

# Collect from AILMENT_INGREDIENTS
for _ing_list in AILMENT_INGREDIENTS.values():
    for _ing in _ing_list:
        _add_spell_material(_ing)

# Collect from SPELL_INGREDIENTS
for _guild_spells in SPELL_INGREDIENTS.values():
    for _spell_type_dict in _guild_spells.values():
        for _ing_list in _spell_type_dict.values():
            for _ing in _ing_list:
                _add_spell_material(_ing)

# Collect from UNUSED_INGREDIENT_SOURCES keys
for _ing_name in UNUSED_INGREDIENT_SOURCES.keys():
    _add_spell_material(_ing_name)

# ============================================================
# BASE CRAFT ITEMS
# ============================================================

ITEMCATEGORIES["craft"] = [
    {"id": "craft_base_weapon", "name": "Base Weapons",
     "actionType": "equip", "inventorySlot": "weapon", "size": "large"},
    {"id": "craft_base_armor", "name": "Base Armors",
     "actionType": "equip", "size": "large"}
]

ITEMLISTS["craft"] = []

BASE_WEAPONS = [
    "Iron Sword", "Steel Sword", "Bronze Dagger", "War Axe", "Battle Hammer",
    "Hunter Spear", "Oak Staff", "Crystal Wand", "Knight Mace", "Bone Club",
    "Silver Shortsword", "Obsidian Blade"
]

BASE_ARMORS = [
    ("Leather Helmet", "head"),
    ("Iron Helmet", "head"),
    ("Traveler Hood", "head"),
    ("Chain Necklace", "neck"),
    ("Bone Necklace", "neck"),
    ("Iron Chestplate", "body"),
    ("Steel Armor", "body"),
    ("Leather Vest", "body"),
    ("Iron Gloves", "hand"),
    ("Leather Gloves", "hand"),
    ("Steel Boots", "feet"),
    ("Traveler Boots", "feet")
]

for weapon in BASE_WEAPONS:
    ITEMLISTS["craft"].append({
        "id": sid(weapon),
        "name": weapon,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 100,
        "category": "craft_base_weapon",
        "description": "A base weapon ready for magical crafting.",
        "equipEffect": {"increaseAttackDamage": {"min": 3, "max": 8}}
    })

for armor_name, slot in BASE_ARMORS:
    ITEMLISTS["craft"].append({
        "id": sid(armor_name),
        "name": armor_name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 120,
        "category": "craft_base_armor",
        "inventorySlot": slot,
        "description": "A base armor piece ready for magical crafting.",
        "equipEffect": {"increaseDefense": 4, "increaseMaxHP": 10}
    })

# ============================================================
# CLOTHING
# ============================================================

ITEMCATEGORIES["clothing"] = [
    {"id": "clothing_items", "name": "Clothing",
     "actionType": "equip", "size": "large"}
]

ITEMLISTS["clothing"] = []

CLOTHING_ITEMS = [
    ("Wool Cap", "head"), ("Silk Hood", "head"), ("Traveler Hat", "head"),
    ("Feather Cap", "head"), ("Fur Hood", "head"),
    ("Cloth Scarf", "neck"), ("Silk Scarf", "neck"), ("Traveler Cloak", "neck"),
    ("Wool Vest", "body"), ("Silk Robe", "body"), ("Traveler Coat", "body"),
    ("Leather Coat", "body"), ("Fur Coat", "body"),
    ("Leather Mitts", "hand"), ("Silk Gloves", "hand"), ("Wool Gloves", "hand"),
    ("Traveler Wraps", "hand"), ("Work Gloves", "hand"),
    ("Leather Sandals", "feet"), ("Traveler Boots", "feet"), ("Fur Boots", "feet"),
    ("Cloth Shoes", "feet"), ("Silk Slippers", "feet")
]

for item_name, slot in CLOTHING_ITEMS:
    ITEMLISTS["clothing"].append({
        "id": sid(item_name),
        "name": item_name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 35,
        "category": "clothing_items",
        "inventorySlot": slot,
        "description": f"Comfortable clothing worn on the {slot} slot.",
        "equipEffect": {"increaseDefense": 1, "increaseMaxHP": 2}
    })

# ============================================================
# JEWELRY
# ============================================================

ITEMCATEGORIES["jewelry"] = [
    {"id": "jewelry_items", "name": "Jewelry",
     "actionType": "equip", "size": "large"}
]

ITEMLISTS["jewelry"] = []

JEWELRY_ITEMS = [
    ("Copper Ring", "leftring"), ("Silver Ring", "leftring"), ("Golden Ring", "leftring"),
    ("Ruby Ring", "leftring"), ("Emerald Ring", "leftring"), ("Sapphire Ring", "leftring"),
    ("Moonstone Ring", "leftring"), ("Dragon Ring", "leftring"),
    ("Copper Bracelet", "hand"), ("Silver Bracelet", "hand"), ("Golden Bracelet", "hand"),
    ("Obsidian Bracelet", "hand"), ("Crystal Bracelet", "hand"),
    ("Copper Necklace", "neck"), ("Silver Necklace", "neck"), ("Golden Necklace", "neck"),
    ("Ruby Necklace", "neck"), ("Emerald Necklace", "neck"), ("Sapphire Necklace", "neck"),
    ("Moon Pendant", "neck"), ("Sun Pendant", "neck"), ("Crystal Charm", "neck"),
    ("Bone Charm", "neck"), ("Ancient Talisman", "neck"), ("Wizard Charm", "neck")
]

for item_name, slot in JEWELRY_ITEMS:
    ITEMLISTS["jewelry"].append({
        "id": sid(item_name),
        "name": item_name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 90,
        "category": "jewelry_items",
        "inventorySlot": slot,
        "description": f"Jewelry worn in the {slot} slot.",
        "equipEffect": {"increaseMaxHP": 5, "increaseAttackChance": 2}
    })

# ============================================================
# MEALS
# ============================================================

ITEMCATEGORIES["meals"] = [
    {"id": "meal_items", "name": "Meals", "actionType": "use"}
]

ITEMLISTS["meals"] = []

MEALS = [
    "Rabbit Stew", "Beef Roast", "Herb Soup", "Fish Chowder", "Apple Pie",
    "Berry Tart", "Vegetable Stew", "Spiced Wolf Meat", "Roasted Boar",
    "Mushroom Soup", "Honey Bread", "Cheese Platter", "Grilled Salmon",
    "Baked Potato", "Garlic Chicken", "Fried Catfish", "Pepper Steak",
    "Mint Salad", "Pumpkin Soup", "Roasted Duck", "Traveler Rations",
    "Sweet Roll", "Berry Porridge", "Seafood Platter", "Golden Omelet"
]

for meal in MEALS:
    ITEMLISTS["meals"].append({
        "id": sid(meal),
        "name": meal,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 25,
        "category": "meal_items",
        "description": f"A prepared meal called {meal}.",
        "useEffect": {
            "increaseCurrentHP": {"min": 20, "max": 35},
            "increaseCurrentAP": {"min": 5, "max": 10}
        }
    })

# ============================================================
# FIGHTER GUILD WEAPONS
# ============================================================

ITEMCATEGORIES["fighter"] = [
    {"id": "fighter_forge_weapons", "name": "Fighter Forge Weapons",
     "actionType": "equip", "inventorySlot": "weapon", "size": "large"}
]

ITEMLISTS["fighter"] = []

FIGHTER_WEAPONS = [
    "Iron Longsword", "Steel Claymore", "Bronze War Axe", "Knight Halberd",
    "Spiked Mace", "Heavy Maul", "Battle Spear", "Forged Pike",
    "Executioner Axe", "Iron Flail", "Tower Hammer", "Steel Bastard Sword",
    "Mercenary Blade", "Legionnaire Spear", "War Pick", "Reinforced Club",
    "Tempered Falchion", "Barbed Trident", "Crusader Hammer", "Forged Scimitar",
    "Warlord Axe", "Steel Greatsword", "Arena Mace", "Veteran Sword", "Champion Halberd"
]

for i, weapon in enumerate(FIGHTER_WEAPONS):
    ITEMLISTS["fighter"].append({
        "id": sid(weapon),
        "name": weapon,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 180 + (i * 5),
        "category": "fighter_forge_weapons",
        "description": "A forged weapon crafted by fighter guild blacksmiths.",
        "equipEffect": {
            "increaseAttackDamage": {"min": 5 + (i % 4), "max": 10 + (i % 6)},
            "increaseAttackChance": 2 + (i % 3)
        }
    })

# ============================================================
# THIEF GUILD ARMORS
# ============================================================

ITEMCATEGORIES["thief"] = [
    {"id": "thief_shadow_armor", "name": "Thief Guild Armor",
     "actionType": "equip", "size": "large"}
]

ITEMLISTS["thief"] = []

THIEF_ARMORS = [
    ("Shadow Hood", "head"), ("Silent Hood", "head"), ("Night Mask", "head"),
    ("Cutpurse Cap", "head"), ("Black Veil", "head"),
    ("Smoke Cloak", "neck"), ("Whisper Scarf", "neck"), ("Night Stalker Cloak", "neck"),
    ("Bandit Wrap", "neck"), ("Shadow Pendant", "neck"),
    ("Leather Jerkin", "body"), ("Silent Vest", "body"), ("Nightweave Armor", "body"),
    ("Dark Leather Coat", "body"), ("Rogue Tunic", "body"),
    ("Silent Gloves", "hand"), ("Pickpocket Grips", "hand"), ("Shadow Wraps", "hand"),
    ("Night Gloves", "hand"), ("Locksmith Mitts", "hand"),
    ("Silent Boots", "feet"), ("Shadow Boots", "feet"), ("Softstep Shoes", "feet"),
    ("Nightwalker Boots", "feet"), ("Bandit Sandals", "feet")
]

for i, (armor_name, slot) in enumerate(THIEF_ARMORS):
    ITEMLISTS["thief"].append({
        "id": sid(armor_name),
        "name": armor_name,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 140 + (i * 4),
        "category": "thief_shadow_armor",
        "inventorySlot": slot,
        "description": "Light armor crafted for thief guild operatives.",
        "equipEffect": {
            "increaseDefense": 3 + (i % 3),
            "increaseAttackChance": 2,
            "increaseMoveCost": -1
        }
    })

# ============================================================
# SPELL CONTENT GENERATION
# ============================================================

for guild, spells in SPELL_DATA.items():

    ACTORCONDITIONS[guild] = []
    ITEMLISTS[f"weapon_{guild}"] = []
    ITEMLISTS[f"scroll_{guild}"] = []
    ITEMLISTS[f"potion_{guild}"] = []
    ITEMLISTS[f"armor_{guild}"] = []

    # ---- OFFENSIVE SPELLS ----
    for i, spell in enumerate(spells["offensive"]):
        spell_id = sid(spell)
        weapon_type = WEAPON_TYPES[i % len(WEAPON_TYPES)]
        weapon_name = f"{spell} {weapon_type}"

        ACTORCONDITIONS[guild].append({
            "id": spell_id,
            "name": spell,
            "iconID": ACTORCONDITION_ICON,
            "isNegative": 1,
            "abilityEffect": {
                "increaseAttackChance": 15,
                "increaseAttackDamage": {"min": 10, "max": 25}
            }
        })

        base_weapon = BASE_WEAPONS[i % len(BASE_WEAPONS)]

        ITEMLISTS[f"weapon_{guild}"].append({
            "id": f"{spell_id}_{sid(weapon_type)}",
            "name": weapon_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "baseMarketCost": 250,
            "category": f"crafted_weapon_{guild}",
            "description": (
                f"A magical {weapon_type.lower()} crafted from "
                f"{base_weapon} and infused with {spell}."
            ),
            "hitEffect": {
                "conditionsSource": [{
                    "condition": spell_id,
                    "magnitude": 1,
                    "duration": 20,
                    "chance": 100
                }]
            },
            "equipEffect": {
                "increaseAttackDamage": {"min": 10, "max": 20},
                "increaseAttackChance": 10
            }
        })

        ITEMLISTS[f"scroll_{guild}"].append({
            "id": f"{spell_id}_scroll",
            "name": f"Scroll of {spell}",
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "baseMarketCost": 100,
            "category": f"crafted_scroll_{guild}",
            "description": f"A magical scroll containing {spell}.",
            "useEffect": {
                "conditionsSource": [{
                    "condition": spell_id,
                    "magnitude": 1,
                    "duration": 20,
                    "chance": 100
                }]
            }
        })

        ITEMLISTS[f"potion_{guild}"].append({
            "id": f"{spell_id}_potion",
            "name": f"{spell} Potion",
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "baseMarketCost": 120,
            "category": f"crafted_potion_{guild}",
            "description": f"A magical potion infused with {spell}.",
            "useEffect": {
                "conditionsSource": [{
                    "condition": spell_id,
                    "magnitude": 2,
                    "duration": 10,
                    "chance": 100
                }]
            }
        })

    # ---- DEFENSIVE SPELLS ----
    slot_keys = list(ARMOR_SLOT_DATA.keys())
    for i, spell in enumerate(spells["defensive"]):
        spell_id = sid(spell)
        slot = slot_keys[i % len(slot_keys)]
        slot_info = ARMOR_SLOT_DATA[slot]
        armor_name = f"{spell} {slot_info['suffix']}"

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

        base_armor_name, _ = BASE_ARMORS[i % len(BASE_ARMORS)]

        ITEMLISTS[f"armor_{guild}"].append({
            "id": f"{spell_id}_{slot}",
            "name": armor_name,
            "iconID": ITEM_ICON,
            "displaytype": "ordinary",
            "baseMarketCost": 200,
            "category": f"crafted_{slot}_{guild}",
            "description": (
                f"Protective gear crafted from {base_armor_name} "
                f"and blessed with {spell}."
            ),
            "equipEffect": {
                "increaseDefense": 15,
                "increaseMaxHP": 25
            }
        })

# ============================================================
# GUILD NPCs / QUESTS / SCHOLARS
# ============================================================

GUILDS = ["adventurer", "fighter", "thief", "mage", "cleric", "druid"]

SCHOLAR_SKILLS = [
    "foraging", "mining", "jewelry_making", "sewing", "cooking",
    "gardening", "weaponsmithing", "armorsmithing"
]

NPCS = {}
CONVERSATIONS = {}
QUESTS = {}

# ============================================================
# GLOBAL SKILL ACTOR CONDITIONS
# ============================================================

ACTORCONDITIONS["skills"] = []

for skill in SCHOLAR_SKILLS:
    skill_condition = f"skill_{skill}"
    ACTORCONDITIONS["skills"].append({
        "id": skill_condition,
        "name": skill.replace("_", " ").title(),
        "iconID": ACTORCONDITION_ICON,
        "isNegative": 0,
        "abilityEffect": {"increaseAttackChance": 1}
    })

if "adventurer" not in ACTORCONDITIONS:
    ACTORCONDITIONS["adventurer"] = []

for guild in GUILDS:
    NPCS[guild] = []
    CONVERSATIONS[guild] = []
    QUESTS[guild] = []

    # ---- GRANDMASTER ----
    grandmaster_id = f"grandmaster_{guild}"
    random_lines = [
        f"The {guild} guild watches every road.",
        f"A true {guild} studies patience before strength.",
        f"Many adventurers fail because they ignore preparation.",
        f"The old ruins still hide forgotten treasures.",
        f"Mastery belongs to those who endure failure.",
        f"Dangerous creatures roam beyond the northern hills.",
        f"Rare crafting materials can be found deep underground.",
        f"Guild loyalty is earned through action.",
        f"Knowledge is worth more than gold.",
        f"Power without discipline leads to ruin.",
        f"Travelers speak of ancient magic beneath the mountains.",
        f"The wilderness rewards careful explorers.",
        f"Every guild member must prove their worth.",
        f"Experience is the greatest teacher.",
        f"Heroes are forged through hardship."
    ]
    conversation_entries = [
        {"id": f"{guild}_grandmaster_random_{i}", "text": line}
        for i, line in enumerate(random_lines)
    ]
    CONVERSATIONS[guild].extend(conversation_entries)
    NPCS[guild].append({
        "id": grandmaster_id,
        "name": f"{guild.title()} Grandmaster",
        "iconID": "npc_human:1",
        "conversation": f"conversationlist_{guild}",
        "randomConversationIDs": [c["id"] for c in conversation_entries]
    })

    # ---- LEADER + QUEST CHAIN ----
    leader_id = f"leader_{guild}"
    CONVERSATIONS[guild].append({
        "id": f"leader_{guild}_intro",
        "text": (
            f"Welcome to the {guild.title()} Guild. "
            f"Complete our trials and rise through the ranks."
        )
    })
    NPCS[guild].append({
        "id": leader_id,
        "name": f"{guild.title()} Guild Leader",
        "iconID": "npc_human:2",
        "conversation": f"conversationlist_{guild}",
        "questlist": f"questlist_{guild}"
    })

    for level in range(1, 13):
        quest_id = f"quest_{guild}_{level}"
        actor_condition = f"{guild}_level_{level}"

        if guild not in ACTORCONDITIONS:
            ACTORCONDITIONS[guild] = []

        ACTORCONDITIONS[guild].append({
            "id": actor_condition,
            "name": f"{guild.title()} Guild Rank {level}",
            "iconID": ACTORCONDITION_ICON,
            "isNegative": 0,
            "abilityEffect": {
                "increaseAttackChance": level,
                "increaseDefense": level,
                "increaseMaxHP": level * 2
            }
        })

        QUESTS[guild].append({
            "id": quest_id,
            "name": f"{guild.title()} Trial {level}",
            "description": (
                f"Complete the level {level} trial for the {guild.title()} guild."
            ),
            "showReward": 1,
            "rewards": {
                "actorConditions": [{
                    "condition": actor_condition,
                    "magnitude": 1,
                    "chance": 100,
                    "duration": -1
                }],
                "experience": level * 250,
                "gold": level * 100
            },
            "requirements": {"actorConditions": []}
        })

        if level > 1:
            QUESTS[guild][-1]["requirements"]["actorConditions"].append({
                "condition": f"{guild}_level_{level - 1}",
                "magnitude": 1
            })

        CONVERSATIONS[guild].append({
            "id": f"{guild}_leader_level_{level}",
            "text": (
                f"You are now prepared for level {level} "
                f"of the {guild.title()} guild trials."
            ),
            "actorConditions": [{"condition": actor_condition, "negate": 1}]
        })

    # ---- SCHOLAR ----
    scholar_id = f"scholar_{guild}"
    scholar_conversations = []
    for skill in SCHOLAR_SKILLS:
        skill_condition = f"skill_{skill}"
        scholar_conversations.append({
            "id": f"teach_{guild}_{skill}",
            "text": f"I can teach you the art of {skill.replace('_', ' ')}.",
            "rewards": {
                "actorConditions": [{
                    "condition": skill_condition,
                    "magnitude": 1,
                    "chance": 100,
                    "duration": -1
                }]
            }
        })
    CONVERSATIONS[guild].extend(scholar_conversations)
    NPCS[guild].append({
        "id": scholar_id,
        "name": f"{guild.title()} Scholar",
        "iconID": "npc_human:3",
        "conversation": f"conversationlist_{guild}"
    })

# ============================================================
# GUILD SHOPKEEPERS
# ============================================================

SHOPKEEPERS = {
    "adventurer": [
        {"id": "shop_jeweler_adventurer",   "name": "Guild Jeweler",    "items": "itemlist_jewelry",    "type": "jeweler"},
        {"id": "shop_seamstress_adventurer","name": "Guild Seamstress", "items": "itemlist_clothing",   "type": "seamstress"},
        {"id": "shop_grocer_adventurer",    "name": "Guild Grocer",     "items": "itemlist_meals",      "type": "grocer"},
        {"id": "shop_farmer_adventurer",    "name": "Guild Farmer",     "items": "itemlist_gardening",  "type": "farmer"},
        {"id": "shop_weaponer_adventurer",  "name": "Guild Weaponer",   "items": "itemlist_fighter",    "type": "weaponer"},
        {"id": "shop_armorer_adventurer",   "name": "Guild Armorer",    "items": "itemlist_thief",      "type": "armorer"}
    ],
    "fighter": [
        {"id": "shop_weaponer_fighter", "name": "Fighter Weaponer", "items": "itemlist_fighter", "type": "weaponer"}
    ],
    "thief": [
        {"id": "shop_armorer_thief",     "name": "Thief Armorer",      "items": "itemlist_thief",       "type": "armorer"},
        {"id": "shop_blackmarket_thief", "name": "Black Market Dealer", "items": "itemlist_thief_tools", "type": "blackmarket"}
    ],
    "mage": [
        {"id": "shop_scribe_mage",    "name": "Arcane Scribe",  "items": "itemlist_scroll_mage",  "type": "scribe"},
        {"id": "shop_alchemist_mage", "name": "Mage Alchemist", "items": "itemlist_potion_mage",  "type": "alchemist"},
        {"id": "shop_crafter_mage",   "name": "Wand Crafter",   "items": "itemlist_weapon_mage",  "type": "crafter"}
    ],
    "cleric": [
        {"id": "shop_scribe_cleric",    "name": "Holy Scribe",      "items": "itemlist_scroll_cleric",  "type": "scribe"},
        {"id": "shop_alchemist_cleric", "name": "Temple Alchemist", "items": "itemlist_potion_cleric",  "type": "alchemist"},
        {"id": "shop_crafter_cleric",   "name": "Relic Crafter",    "items": "itemlist_weapon_cleric",  "type": "crafter"}
    ],
    "druid": [
        {"id": "shop_scribe_druid",    "name": "Nature Scribe",  "items": "itemlist_scroll_druid",  "type": "scribe"},
        {"id": "shop_alchemist_druid", "name": "Wild Alchemist", "items": "itemlist_potion_druid",  "type": "alchemist"},
        {"id": "shop_crafter_druid",   "name": "Totem Crafter",  "items": "itemlist_weapon_druid",  "type": "crafter"}
    ]
}

# ============================================================
# THIEF TOOLS
# ============================================================

ITEMCATEGORIES["thief_tools"] = [{"id": "thief_tools", "name": "Thief Tools"}]
ITEMLISTS["thief_tools"] = []

THIEF_TOOLS = [
    "Lockpick", "Fine Lockpick", "Shadow Cloak", "Disguise Kit", "Smoke Bomb",
    "Poison Needle", "Silent Boots", "Forgery Papers", "Hidden Blade", "Dark Hood"
]

for i, item in enumerate(THIEF_TOOLS):
    ITEMLISTS["thief_tools"].append({
        "id": sid(item),
        "name": item,
        "iconID": ITEM_ICON,
        "displaytype": "ordinary",
        "baseMarketCost": 50 + (i * 10),
        "category": "thief_tools",
        "description": f"A thief utility item called {item}."
    })

# ============================================================
# CRAFTING MATERIALS (extra items needed for crafting recipes)
# ============================================================

ITEMLISTS["crafting_materials"] = []
_SEEN_CRAFT_MAT_IDS = set()

def _add_craft_mat(iid, name, cost, category, desc):
    if iid in _SEEN_CRAFT_MAT_IDS:
        return
    if iid in _SEEN_DROP_IDS or iid in _SEEN_MINING_IDS:
        return
    _SEEN_CRAFT_MAT_IDS.add(iid)
    ITEMLISTS["crafting_materials"].append(
        create_basic_item(iid, name, cost, category, desc)
    )

_add_craft_mat("binding_wire",    "Binding Wire",    5,  "crafting_materials", "Wire used in jewelry making.")
_add_craft_mat("bone",            "Bone",            8,  "crafting_materials", "A bone used in crafting.")
_add_craft_mat("thread",          "Thread",          3,  "crafting_materials", "Thread used for sewing.")
_add_craft_mat("wool_cloth",      "Wool Cloth",      8,  "crafting_materials", "Rough wool cloth.")
_add_craft_mat("feather_material","Feather Material",6,  "crafting_materials", "Bound feathers for crafting.")
_add_craft_mat("fur_pelt",        "Fur Pelt",        12, "crafting_materials", "A pelt of animal fur.")
_add_craft_mat("leather_hide",    "Leather Hide",    15, "crafting_materials", "Tanned animal hide.")
_add_craft_mat("holy_water",      "Holy Water",      20, "crafting_materials", "Blessed water sanctified by a cleric.")
_add_craft_mat("angel_feather",   "Angel Feather",   60, "crafting_materials", "A feather from a celestial being.")
_add_craft_mat("ironwood_bark",   "Ironwood Bark",   25, "crafting_materials", "Bark from an ironwood tree.")
_add_craft_mat("gravebane_herb",  "Gravebane Herb",  30, "crafting_materials", "Herb that repels undead.")
_add_craft_mat("judgement_ink",   "Judgement Ink",   40, "crafting_materials", "Sacred ink for divine rites.")
_add_craft_mat("sun_ember",       "Sun Ember",       35, "crafting_materials", "A glowing ember of solar energy.")
_add_craft_mat("golden_herb",     "Golden Herb",     25, "crafting_materials", "An herb with a golden hue.")
_add_craft_mat("blessed_wax",     "Blessed Wax",     15, "crafting_materials", "Candle wax blessed by a cleric.")
_add_craft_mat("fire_petal",      "Fire Petal",      20, "crafting_materials", "A petal that burns to the touch.")
_add_craft_mat("blessed_herb",    "Blessed Herb",    20, "crafting_materials", "An herb blessed by a priest.")
_add_craft_mat("blessed_ash",     "Blessed Ash",     15, "crafting_materials", "Sacred ash from a holy fire.")
_add_craft_mat("blessed_oil",     "Blessed Oil",     25, "crafting_materials", "Oil blessed by a cleric.")
_add_craft_mat("silver_leaf",     "Silver Leaf",     18, "crafting_materials", "A silvery magical leaf.")
_add_craft_mat("guardian_bark",   "Guardian Bark",   22, "crafting_materials", "Bark imbued with protective energy.")
_add_craft_mat("sanctuary_moss",  "Sanctuary Moss",  20, "crafting_materials", "Moss from a holy sanctuary.")
_add_craft_mat("blessed_bark",    "Blessed Bark",    18, "crafting_materials", "Bark blessed by a cleric.")
_add_craft_mat("sacred_herb",     "Sacred Herb",     22, "crafting_materials", "An herb from a sacred grove.")
_add_craft_mat("purity_herb",     "Purity Herb",     20, "crafting_materials", "An herb of cleansing purity.")
_add_craft_mat("golden_thorn",    "Golden Thorn",    15, "crafting_materials", "A sharp golden thorn.")
_add_craft_mat("golden_nectar",   "Golden Nectar",   20, "crafting_materials", "Sweet golden nectar.")
_add_craft_mat("spirit_dust",     "Spirit Dust",     25, "crafting_materials", "Dust from a spirit entity.")
_add_craft_mat("spirit_herb",     "Spirit Herb",     22, "crafting_materials", "An herb aligned with spirit energy.")
_add_craft_mat("blessed_iron",    "Blessed Iron",    30, "crafting_materials", "Iron metal blessed by a temple.")

# Druid materials
_add_craft_mat("thornvine",       "Thornvine",       12, "crafting_materials", "A thorny vine.")
_add_craft_mat("oak_sap",         "Oak Sap",         10, "crafting_materials", "Sap from an oak tree.")
_add_craft_mat("wildroot",        "Wildroot",         8, "crafting_materials", "A wild root from the forest.")
_add_craft_mat("stone_dust",      "Stone Dust",       5, "crafting_materials", "Powdered stone.")
_add_craft_mat("toxic_petal",     "Toxic Petal",     18, "crafting_materials", "A petal that secretes toxins.")
_add_craft_mat("venom_sap",       "Venom Sap",       20, "crafting_materials", "Venomous tree sap.")
_add_craft_mat("ancient_bark",    "Ancient Bark",    22, "crafting_materials", "Bark from an ancient tree.")
_add_craft_mat("earth_crystal",   "Earth Crystal",   28, "crafting_materials", "A crystal of earth energy.")
_add_craft_mat("wildfire_ember",  "Wildfire Ember",  25, "crafting_materials", "An ember from a wildfire.")
_add_craft_mat("whip_vine",       "Whip Vine",       12, "crafting_materials", "A flexible vine used as a whip.")
_add_craft_mat("moonleaf",        "Moonleaf",        18, "crafting_materials", "A leaf bathed in moonlight.")
_add_craft_mat("root_resin",      "Root Resin",      10, "crafting_materials", "Resin from tree roots.")
_add_craft_mat("wind_essence",    "Wind Essence",    30, "crafting_materials", "Essence of the wind.")
_add_craft_mat("storm_herb",      "Storm Herb",      20, "crafting_materials", "An herb that grows in storm regions.")
_add_craft_mat("sky_feather",     "Sky Feather",     25, "crafting_materials", "A feather from a sky creature.")
_add_craft_mat("rainwater",       "Rainwater",        5, "crafting_materials", "Fresh rainwater.")
_add_craft_mat("ash_bark",        "Ash Bark",         8, "crafting_materials", "Bark from an ash tree.")
_add_craft_mat("sulfur_moss",     "Sulfur Moss",     15, "crafting_materials", "Moss with a sulfurous smell.")
_add_craft_mat("fire_bloom",      "Fire Bloom",      20, "crafting_materials", "A flame-colored flower bloom.")
_add_craft_mat("charged_water",   "Charged Water",   15, "crafting_materials", "Water charged with energy.")
_add_craft_mat("thunder_herb",    "Thunder Herb",    22, "crafting_materials", "An herb that crackles with energy.")
_add_craft_mat("root_vine",       "Root Vine",       10, "crafting_materials", "A vine that grows along roots.")
_add_craft_mat("forest_moss",     "Forest Moss",      8, "crafting_materials", "Soft moss from the forest floor.")
_add_craft_mat("iron_oak_bark",   "Iron Oak Bark",   22, "crafting_materials", "Extremely hard bark from iron oak.")
_add_craft_mat("living_vine",     "Living Vine",     20, "crafting_materials", "A vine still pulsing with life.")
_add_craft_mat("earth_sap",       "Earth Sap",       12, "crafting_materials", "Sap infused with earth energy.")
_add_craft_mat("ghost_thorn",     "Ghost Thorn",     25, "crafting_materials", "A thorn from a ghost plant.")
_add_craft_mat("spirit_bloom",    "Spirit Bloom",    22, "crafting_materials", "A bloom aligned with spirit energy.")
_add_craft_mat("silver_vine",     "Silver Vine",     20, "crafting_materials", "A vine with silvery leaves.")
_add_craft_mat("beast_fang",      "Beast Fang",      18, "crafting_materials", "A fang from a wild beast.")
_add_craft_mat("blood_moss",      "Blood Moss",      15, "crafting_materials", "Reddish moss found near battlefields.")
_add_craft_mat("moon_herb",       "Moon Herb",       18, "crafting_materials", "An herb that blooms under moonlight.")
_add_craft_mat("charged_sap",     "Charged Sap",     15, "crafting_materials", "Electrically charged tree sap.")
_add_craft_mat("growth_seed",     "Growth Seed",      8, "crafting_materials", "A seed brimming with growth energy.")
_add_craft_mat("moonwater",       "Moonwater",       20, "crafting_materials", "Water bathed under moonlight.")
_add_craft_mat("ancient_moss",    "Ancient Moss",    15, "crafting_materials", "Moss that has grown for centuries.")
_add_craft_mat("rot_seed",        "Rot Seed",        12, "crafting_materials", "A seed that spreads rot.")
_add_craft_mat("blight_petal",    "Blight Petal",    15, "crafting_materials", "A petal infected with blight.")
_add_craft_mat("toxic_sap",       "Toxic Sap",       18, "crafting_materials", "Highly toxic tree sap.")
_add_craft_mat("granite_dust",    "Granite Dust",     5, "crafting_materials", "Fine powder from ground granite.")
_add_craft_mat("rock_salt",       "Rock Salt",        5, "crafting_materials", "Salt in its raw rock form.")
_add_craft_mat("alpha_fang",      "Alpha Fang",      25, "crafting_materials", "A fang from an alpha predator.")
_add_craft_mat("barkskin_resin",  "Barkskin Resin",  18, "crafting_materials", "Resin that hardens the skin.")
_add_craft_mat("oak_bark",        "Oak Bark",         8, "crafting_materials", "Bark stripped from an oak tree.")
_add_craft_mat("lifebloom_petal", "Lifebloom Petal", 22, "crafting_materials", "A petal that radiates healing energy.")
_add_craft_mat("healing_herb",    "Healing Herb",    15, "crafting_materials", "An herb with healing properties.")
_add_craft_mat("stone_moss",      "Stone Moss",       8, "crafting_materials", "Moss growing on stone surfaces.")
_add_craft_mat("shadow_vine",     "Shadow Vine",     18, "crafting_materials", "A vine that grows in shadows.")
_add_craft_mat("charged_bark",    "Charged Bark",    20, "crafting_materials", "Bark charged with storm energy.")
_add_craft_mat("storm_crystal",   "Storm Crystal",   30, "crafting_materials", "A crystal of storm energy.")
_add_craft_mat("bloom_petal",     "Bloom Petal",     15, "crafting_materials", "A colorful bloom petal.")
_add_craft_mat("renewal_seed",    "Renewal Seed",    20, "crafting_materials", "A seed of renewal and regrowth.")
_add_craft_mat("sacred_grove_leaf","Sacred Grove Leaf",22,"crafting_materials","A leaf from a sacred grove.")
_add_craft_mat("sacred_flame_oil","Sacred Flame Oil",30, "crafting_materials", "Blessed oil that burns holy flame.")
_add_craft_mat("celestial_water", "Celestial Water", 25, "crafting_materials", "Water from a celestial source.")
_add_craft_mat("silver_thread",   "Silver Thread",   15, "crafting_materials", "Thread spun from silver fibers.")
_add_craft_mat("mana_resin",      "Mana Resin",      20, "crafting_materials", "Resin saturated with mana.")
_add_craft_mat("runic_dust",      "Runic Dust",      22, "crafting_materials", "Dust inscribed with runes.")
_add_craft_mat("spirit_water",    "Spirit Water",    20, "crafting_materials", "Water imbued with spirit energy.")
_add_craft_mat("arcane_powder",   "Arcane Powder",   18, "crafting_materials", "Powder radiating arcane energy.")
_add_craft_mat("arcane_sap",      "Arcane Sap",      20, "crafting_materials", "Sap imbued with arcane energy.")
_add_craft_mat("mystic_moss",     "Mystic Moss",     18, "crafting_materials", "Moss with mystical properties.")
_add_craft_mat("ice_bark",        "Ice Bark",        15, "crafting_materials", "Bark from a tree in icy regions.")
_add_craft_mat("winter_oil",      "Winter Oil",      18, "crafting_materials", "Oil made in cold climates.")
_add_craft_mat("shield_bark",     "Shield Bark",     20, "crafting_materials", "Bark used in protective crafting.")
_add_craft_mat("granite_powder",  "Granite Powder",   5, "crafting_materials", "Very fine granite powder.")
_add_craft_mat("earth_essence",   "Earth Essence",   25, "crafting_materials", "Pure essence of earth magic.")
_add_craft_mat("soul_crystal",    "Soul Crystal",    40, "crafting_materials", "A crystal containing soul energy.")
_add_craft_mat("shadow_silk",     "Shadow Silk",     25, "crafting_materials", "Silk woven in darkness.")
_add_craft_mat("mana_thread",     "Mana Thread",     18, "crafting_materials", "Thread infused with mana.")
_add_craft_mat("moon_petal",      "Moon Petal",      18, "crafting_materials", "A petal that glows in moonlight.")
_add_craft_mat("ghost_silk",      "Ghost Silk",      28, "crafting_materials", "Silk spun by ghost spiders.")
_add_craft_mat("moon_ash",        "Moon Ash",        20, "crafting_materials", "Ash produced under moonlight.")
_add_craft_mat("arcane_crystal",  "Arcane Crystal",  35, "crafting_materials", "A crystal pulsing with arcane power.")
_add_craft_mat("celestial_thread","Celestial Thread",30, "crafting_materials", "Thread woven from celestial light.")
_add_craft_mat("starwater",       "Starwater",       25, "crafting_materials", "Water that has absorbed starlight.")
_add_craft_mat("shield_herb",     "Shield Herb",     18, "crafting_materials", "An herb used in protective rites.")
_add_craft_mat("arcane_dust",     "Arcane Dust",     15, "crafting_materials", "Dust imbued with arcane magic.")
_add_craft_mat("arcane_oil",      "Arcane Oil",      22, "crafting_materials", "Oil saturated with arcane energy.")
_add_craft_mat("silver_oil",      "Silver Oil",      20, "crafting_materials", "Oil refined from silver compounds.")
_add_craft_mat("copper_wire",     "Copper Wire",      8, "crafting_materials", "Wire spun from copper.")
_add_craft_mat("spark_moss",      "Spark Moss",      15, "crafting_materials", "Moss that produces sparks.")
_add_craft_mat("pixie_dust",      "Pixie Dust",      25, "crafting_materials", "Magical dust from pixies.")
_add_craft_mat("ice_lotus",       "Ice Lotus",       25, "crafting_materials", "A lotus flower that blooms in ice.")
_add_craft_mat("copper_filament", "Copper Filament",  8, "crafting_materials", "Thin copper filament.")
_add_craft_mat("storm_essence",   "Storm Essence",   28, "crafting_materials", "Pure essence of a storm.")
_add_craft_mat("frost_sap",       "Frost Sap",       15, "crafting_materials", "Sap that has crystallized in frost.")
_add_craft_mat("void_dust",       "Void Dust",       20, "crafting_materials", "Dust from the void.")
_add_craft_mat("acid_crystal",    "Acid Crystal",    22, "crafting_materials", "A crystal of acidic energy.")
_add_craft_mat("bone_powder",     "Bone Powder",      8, "crafting_materials", "Finely ground bone.")
_add_craft_mat("volatile_ember",  "Volatile Ember",  25, "crafting_materials", "An extremely volatile ember.")
_add_craft_mat("sulfur_crystal",  "Sulfur Crystal",  18, "crafting_materials", "A crystal of pure sulfur.")
_add_craft_mat("dragon_pepper",   "Dragon Pepper",   20, "crafting_materials", "Scorching hot pepper.")
_add_craft_mat("flame_oil",       "Flame Oil",       22, "crafting_materials", "Oil that ignites easily.")
_add_craft_mat("crystal_bloom",   "Crystal Bloom",   25, "crafting_materials", "A flower made of crystal.")
_add_craft_mat("silver_dust",     "Silver Dust",     15, "crafting_materials", "Finely ground silver.")
_add_craft_mat("fire_opal",       "Fire Opal",       35, "crafting_materials", "An opal with a fiery core.")
_add_craft_mat("ash_resin",       "Ash Resin",       12, "crafting_materials", "Resin mixed with ash.")
_add_craft_mat("sunroot",         "Sunroot",         18, "crafting_materials", "A root that loves sunlight.")
_add_craft_mat("thunderstone",    "Thunderstone",    25, "crafting_materials", "A stone that resonates with thunder.")
_add_craft_mat("echo_crystal",    "Echo Crystal",    20, "crafting_materials", "A crystal that echoes sound.")
_add_craft_mat("chaos_shard",     "Chaos Shard",     28, "crafting_materials", "A shard of chaotic energy.")
_add_craft_mat("wild_magic_dust", "Wild Magic Dust", 22, "crafting_materials", "Dust infused with wild magic.")
_add_craft_mat("prismatic_salt",  "Prismatic Salt",  18, "crafting_materials", "Salt refracting light into prisms.")
_add_craft_mat("soul_ash",        "Soul Ash",        25, "crafting_materials", "Ash remaining from souls.")
_add_craft_mat("shadow_ember",    "Shadow Ember",    22, "crafting_materials", "An ember of shadow energy.")
_add_craft_mat("nightshade_oil",  "Nightshade Oil",  20, "crafting_materials", "Oil extracted from nightshade.")
_add_craft_mat("black_flame_residue","Black Flame Residue",22,"crafting_materials","Residue of black flames.")
_add_craft_mat("moonstone_dust",  "Moonstone Dust",  18, "crafting_materials", "Finely ground moonstone.")
_add_craft_mat("nether_moss",     "Nether Moss",     20, "crafting_materials", "Moss from the nether realm.")
_add_craft_mat("dark_ash",        "Dark Ash",        12, "crafting_materials", "Ash with dark properties.")
_add_craft_mat("obsidian_powder", "Obsidian Powder",  8, "crafting_materials", "Finely ground obsidian.")
_add_craft_mat("ice_vine",        "Ice Vine",        18, "crafting_materials", "A vine that grows in ice.")
_add_craft_mat("charred_bark",    "Charred Bark",     8, "crafting_materials", "Bark that has been charred by fire.")
_add_craft_mat("psychic_crystal", "Psychic Crystal", 35, "crafting_materials", "A crystal resonating with psychic energy.")
_add_craft_mat("brain_fungus",    "Brain Fungus",    20, "crafting_materials", "A fungus shaped like a brain.")
_add_craft_mat("sulfur_powder",   "Sulfur Powder",   10, "crafting_materials", "Powdered sulfur.")
_add_craft_mat("ruby_dust",       "Ruby Dust",       25, "crafting_materials", "Finely ground ruby.")
_add_craft_mat("ashwood_bark",    "Ashwood Bark",    10, "crafting_materials", "Bark from an ashwood tree.")
_add_craft_mat("iron_bark",       "Iron Bark",       15, "crafting_materials", "Bark as hard as iron.")
_add_craft_mat("void_sap",        "Void Sap",        20, "crafting_materials", "Sap from a void-touched tree.")
_add_craft_mat("nether_oil",      "Nether Oil",      22, "crafting_materials", "Oil extracted from nether plants.")
_add_craft_mat("hardened_sap",    "Hardened Sap",    12, "crafting_materials", "Sap that has hardened solid.")
_add_craft_mat("mana_bloom",      "Mana Bloom",      22, "crafting_materials", "A bloom that radiates mana.")
_add_craft_mat("spirit_moss",     "Spirit Moss",     18, "crafting_materials", "Moss that resonates with spirit energy.")
_add_craft_mat("mystic_water",    "Mystic Water",    20, "crafting_materials", "Water with mystical properties.")
_add_craft_mat("ancient_bark",    "Ancient Bark",    22, "crafting_materials", "Bark from an ancient tree.")

# Also add some common ailment ingredients not from animal/forage drops
_add_craft_mat("grave_dust",      "Grave Dust",      15, "crafting_materials", "Dust collected from graves.")
_add_craft_mat("black_salt",      "Black Salt",      10, "crafting_materials", "Salt that has turned black.")
_add_craft_mat("corpse_flower_petal","Corpse Flower Petal",18,"crafting_materials","A petal from the corpse flower.")
_add_craft_mat("tainted_blood",   "Tainted Blood",   20, "crafting_materials", "Blood corrupted by disease.")
_add_craft_mat("bone_dust",       "Bone Dust",        8, "crafting_materials", "Finely ground bone dust.")
_add_craft_mat("shock_beetle_carapace","Shock Beetle Carapace",20,"crafting_materials","Carapace of a shock beetle.")
_add_craft_mat("copper_powder",   "Copper Powder",    8, "crafting_materials", "Finely ground copper.")
_add_craft_mat("specter_essence", "Specter Essence", 30, "crafting_materials", "Essence of a specter.")
_add_craft_mat("grave_lily",      "Grave Lily",      15, "crafting_materials", "A lily that grows in graveyards.")
_add_craft_mat("hollow_ash",      "Hollow Ash",      12, "crafting_materials", "Ash from burned hollow wood.")
_add_craft_mat("vampire_fang",    "Vampire Fang",    35, "crafting_materials", "A fang from a vampire.")
_add_craft_mat("blood_rose",      "Blood Rose",      22, "crafting_materials", "A rose that feeds on blood.")
_add_craft_mat("crimson_moss",    "Crimson Moss",    15, "crafting_materials", "Deep red moss.")
_add_craft_mat("iron_shavings",   "Iron Shavings",    8, "crafting_materials", "Shavings from iron metal.")
_add_craft_mat("cursed_ink",      "Cursed Ink",      25, "crafting_materials", "Ink infused with a curse.")
_add_craft_mat("hag_hair",        "Hag Hair",        20, "crafting_materials", "Hair from a hag creature.")
_add_craft_mat("wilted_herb",     "Wilted Herb",      5, "crafting_materials", "A dried and wilted herb.")
_add_craft_mat("dust_of_decay",   "Dust of Decay",   15, "crafting_materials", "Dust infused with decay.")
_add_craft_mat("raven_eye",       "Raven Eye",       20, "crafting_materials", "The preserved eye of a raven.")
_add_craft_mat("shadow_root",     "Shadow Root",     18, "crafting_materials", "A root from a shadow plant.")
_add_craft_mat("wyvern_venom",    "Wyvern Venom",    35, "crafting_materials", "Deadly venom from a wyvern.")
_add_craft_mat("hemlock_leaf",    "Hemlock Leaf",    15, "crafting_materials", "A poisonous hemlock leaf.")
_add_craft_mat("diseased_tick",   "Diseased Tick",   12, "crafting_materials", "A tick carrying disease.")
_add_craft_mat("bitterroot",      "Bitterroot",       8, "crafting_materials", "A bitter-tasting root.")
_add_craft_mat("rotten_heartseed","Rotten Heartseed",15, "crafting_materials", "A seed from a rotten plant.")
_add_craft_mat("spirit_dust",     "Spirit Dust",     22, "crafting_materials", "Dust from a spirit.")
_add_craft_mat("hollow_reed",     "Hollow Reed",      5, "crafting_materials", "A hollow reed stalk.")
_add_craft_mat("ethereal_water",  "Ethereal Water",  25, "crafting_materials", "Water from the ethereal plane.")
_add_craft_mat("pale_moss",       "Pale Moss",       10, "crafting_materials", "Pale, colorless moss.")
_add_craft_mat("bone_meal",       "Bone Meal",        8, "crafting_materials", "Ground bone used as fertilizer.")
_add_craft_mat("plague_spore_pod","Plague Spore Pod",20, "crafting_materials", "A pod filled with plague spores.")
_add_craft_mat("moldy_bark",      "Moldy Bark",       8, "crafting_materials", "Bark covered in mold.")
_add_craft_mat("murkweed",        "Murkweed",        10, "crafting_materials", "A weed from murky waters.")
_add_craft_mat("ashen_mold",      "Ashen Mold",      12, "crafting_materials", "Mold with an ashen appearance.")
_add_craft_mat("smog_essence",    "Smog Essence",    15, "crafting_materials", "Captured smog essence.")
_add_craft_mat("diseased_lung_tissue","Diseased Lung Tissue",20,"crafting_materials","Tissue from a diseased lung.")
_add_craft_mat("blackroot",       "Blackroot",       12, "crafting_materials", "A dark-colored root.")
_add_craft_mat("fungus_spores",   "Fungus Spores",   10, "crafting_materials", "Spores released by fungus.")
_add_craft_mat("tainted_water",   "Tainted Water",    8, "crafting_materials", "Water contaminated with disease.")
_add_craft_mat("grave_soil",      "Grave Soil",      10, "crafting_materials", "Soil dug from a grave.")
_add_craft_mat("tortured_soul_essence","Tortured Soul Essence",30,"crafting_materials","Essence of a tortured soul.")
_add_craft_mat("thornvine_sap",   "Thornvine Sap",   12, "crafting_materials", "Sap from a thornvine plant.")
_add_craft_mat("crimson_thorn",   "Crimson Thorn",   15, "crafting_materials", "A bright red thorn.")
_add_craft_mat("assassin_vine_sap","Assassin Vine Sap",20,"crafting_materials","Sap from the deadly assassin vine.")
_add_craft_mat("black_ink",       "Black Ink",        8, "crafting_materials", "Deep black ink.")
_add_craft_mat("raven_feather",   "Raven Feather",   12, "crafting_materials", "A feather from a raven.")
_add_craft_mat("nightshade_berry","Nightshade Berry",18, "crafting_materials", "A poisonous nightshade berry.")
_add_craft_mat("shadow_orchid",   "Shadow Orchid",   22, "crafting_materials", "An orchid that grows in shadows.")
_add_craft_mat("blighted_root",   "Blighted Root",   15, "crafting_materials", "A root infected with blight.")
_add_craft_mat("decayed_mushroom","Decayed Mushroom", 10, "crafting_materials","A mushroom in an advanced state of decay.")
_add_craft_mat("rotwater",        "Rotwater",         8, "crafting_materials", "Foul water from rotting matter.")
_add_craft_mat("shadow_flame_residue","Shadow Flame Residue",22,"crafting_materials","Residue of shadow flames.")
_add_craft_mat("wild_magic_ash",  "Wild Magic Ash",  20, "crafting_materials", "Ash infused with wild magic.")
_add_craft_mat("charcoal_root",   "Charcoal Root",   10, "crafting_materials", "A root that resembles charcoal.")
_add_craft_mat("lava_salt",       "Lava Salt",       15, "crafting_materials", "Salt crystallized from lava.")

# ============================================================
# SHOPKEEPER CONTENT
# ============================================================

SHOPKEEPER_CONVERSATIONS = {}
SHOPKEEPER_ITEMS = {}
SHOPKEEPER_DROPLISTS = {}

# ---- Adventurer shops ----
SHOPKEEPER_ITEMS["jeweler"] = [
    create_basic_item("silver_ring_blank","Silver Ring Blank",40,"jewelry_items","A blank ring for jewelry crafting."),
    create_basic_item("gold_ring_blank","Gold Ring Blank",80,"jewelry_items","A gold ring base for jewelers."),
    create_basic_item("gem_setting_tool","Gem Setting Tool",120,"jewelry_items","A tool used for setting gems.")
]

SHOPKEEPER_ITEMS["seamstress"] = [
    create_basic_item("linen_cloth","Linen Cloth",10,"clothing_items","Soft cloth used for sewing."),
    create_basic_item("silk_cloth","Silk Cloth",30,"clothing_items","Fine silk used for sewing."),
    create_basic_item("sewing_kit","Sewing Kit",60,"clothing_items","Tools for tailoring clothing.")
]

SHOPKEEPER_ITEMS["grocer"] = [
    create_basic_item("cooking_spice","Cooking Spice",8,"meal_items","Spices used in cooking."),
    create_basic_item("salt_sack","Salt Sack",5,"meal_items","A sack filled with salt."),
    create_basic_item("cooking_pot","Cooking Pot",25,"meal_items","A heavy iron cooking pot.")
]

SHOPKEEPER_ITEMS["farmer"] = [
    create_basic_item("fertile_soil","Fertile Soil",12,"garden_ingredients","Rich soil for gardening."),
    create_basic_item("watering_can","Watering Can",20,"garden_tools","Used to water crops."),
    create_basic_item("garden_rake","Garden Rake",15,"garden_tools","Used to prepare farmland.")
]

SHOPKEEPER_ITEMS["weaponer"] = [
    create_basic_item("weapon_hilt","Weapon Hilt",25,"craft_base_weapon","A hilt for forged weapons."),
    create_basic_item("iron_blade","Iron Blade",40,"craft_base_weapon","A forged iron blade."),
    create_basic_item("forge_hammer","Forge Hammer",60,"craft_base_weapon","A hammer used in weaponsmithing.")
]

SHOPKEEPER_ITEMS["armorer"] = [
    create_basic_item("armor_plate","Armor Plate",35,"craft_base_armor","A forged armor plate."),
    create_basic_item("leather_straps","Leather Straps",15,"craft_base_armor","Used in armor crafting."),
    create_basic_item("armor_rivets","Armor Rivets",10,"craft_base_armor","Metal rivets for armor.")
]

# ---- Spell guild shops ----
SHOPKEEPER_ITEMS["scribe"] = [
    create_basic_item("blank_scroll","Blank Scroll",20,"crafted_scroll_mage","A blank magical scroll."),
    create_basic_item("enchanted_ink","Enchanted Ink",45,"crafted_scroll_mage","Ink infused with magical energy."),
    create_basic_item("scribe_quill","Scribe Quill",15,"crafted_scroll_mage","A quill used for magical writing.")
]

SHOPKEEPER_ITEMS["alchemist"] = [
    create_basic_item("glass_vial","Glass Vial",8,"crafted_potion_mage","A vial used for potions."),
    create_basic_item("alchemy_flask","Alchemy Flask",20,"crafted_potion_mage","Used for brewing potions."),
    create_basic_item("mana_herb","Mana Herb",25,"crafted_potion_mage","An herb filled with magical power.")
]

SHOPKEEPER_ITEMS["crafter"] = [
    create_basic_item("wand_core","Wand Core",50,"crafted_weapon_mage","A magical wand core."),
    create_basic_item("staff_shaft","Staff Shaft",40,"crafted_weapon_mage","A shaft used for magical staffs."),
    create_basic_item("arcane_crystal","Arcane Crystal",100,"crafted_weapon_mage","A crystal radiating magical energy.")
]

# ---- Thief shop ----
SHOPKEEPER_ITEMS["blackmarket"] = [
    create_basic_item("fine_lockpick","Fine Lockpick",50,"thief_tools","A precision lockpick."),
    create_basic_item("disguise_kit","Disguise Kit",75,"thief_tools","Tools used for disguises."),
    create_basic_item("smoke_bomb","Smoke Bomb",45,"thief_tools","Creates a cloud of smoke.")
]

for shop_type in SHOPKEEPER_ITEMS.keys():
    SHOPKEEPER_CONVERSATIONS[shop_type] = [{
        "id": f"{shop_type}_greeting",
        "text": f"Welcome. I sell {shop_type} supplies."
    }]
    SHOPKEEPER_DROPLISTS[shop_type] = []
    for item in SHOPKEEPER_ITEMS[shop_type]:
        SHOPKEEPER_DROPLISTS[shop_type].append({
            "itemID": item["id"],
            "chance": "100",
            "quantity": {"min": 1, "max": 3}
        })

# ============================================================
# CREATE SHOPKEEPER NPCS
# ============================================================

for guild, shops in SHOPKEEPERS.items():
    for shop in shops:
        NPCS[guild].append({
            "id": shop["id"],
            "name": shop["name"],
            "iconID": "npc_human:4",
            "shop": f"itemlist_shop_{shop['type']}",
            "conversation": f"conversationlist_shop_{shop['type']}",
            "droplist": f"droplist_shop_{shop['type']}"
        })

# ============================================================
# UNUSED INGREDIENT SOURCES — Game Entities
# Categorise each source and create: shopkeeper NPCs,
# monster entries with droplists, forage droplists, chest droplists.
# ============================================================

_UNUSED_SHOPKEEPERS = {}  # src_id -> {name, items:[]}
_UNUSED_MONSTERS    = {}  # monster_id -> {name, drops:[]}
_UNUSED_FORAGES     = {}  # forage_id -> {name, items:[]}
_UNUSED_CHESTS      = {}  # chest_id -> {name, items:[]}

_SHOPKEEPER_KEYWORDS = [
    "shopkeeper", "vendor", "scribe", "blacksmith", "leatherworker",
    "healer", "jeweler", "alchemist", "merchant", "trader", "guild vendor"
]
_MONSTER_KEYWORDS = [
    "drop", "monster drop", "boss drop", "creature drop", "enemy drop",
    "hoard", "spawn"
]
_FORAGE_KEYWORDS = [
    "forage", "grove", "arcane forest", "storm plains", "shadow forest",
    "enchanted cave", "world tree", "ethereal plane", "fairy grove",
    "fey garden", "sacred grove", "crystal cave", "time dungeon", "fortress ruin"
]
_CHEST_KEYWORDS = [
    "loot", "chest", "dungeon loot", "ancient ruins", "mage tower",
    "chaos rift", "ancient tomb", "crypt", "mage fortress", "desert temple",
    "planar rift", "rainbow cavern", "ancient hourglass dungeon"
]
_EVENT_KEYWORDS = ["event", "reward", "holy shrine", "angel npc"]

for ing_name, src_desc in UNUSED_INGREDIENT_SOURCES.items():
    src_lower = src_desc.lower()
    ing_id = sid(ing_name)

    if any(k in src_lower for k in _SHOPKEEPER_KEYWORDS):
        src_id = sid(src_desc)
        if src_id not in _UNUSED_SHOPKEEPERS:
            _UNUSED_SHOPKEEPERS[src_id] = {"name": src_desc, "id": f"npc_{src_id}", "items": []}
        _UNUSED_SHOPKEEPERS[src_id]["items"].append(ing_name)

    elif any(k in src_lower for k in _MONSTER_KEYWORDS):
        monster_name = (src_desc.replace(" Monster Drop", "").replace(" Boss Drop", "")
                                .replace(" Creature Drop", "").replace(" Enemy Drop", "")
                                .replace(" Drop", "").replace(" Hoard", ""))
        monster_id = sid(monster_name)
        if monster_id not in _UNUSED_MONSTERS:
            _UNUSED_MONSTERS[monster_id] = {"name": monster_name, "drops": []}
        _UNUSED_MONSTERS[monster_id]["drops"].append(ing_name)

    elif any(k in src_lower for k in _FORAGE_KEYWORDS):
        forage_name = (src_desc.replace(" Forage", "").replace(" Reward", ""))
        forage_id = sid(forage_name)
        if forage_id not in _UNUSED_FORAGES:
            _UNUSED_FORAGES[forage_id] = {"name": forage_name, "items": []}
        _UNUSED_FORAGES[forage_id]["items"].append(ing_name)

    elif any(k in src_lower for k in _CHEST_KEYWORDS):
        chest_name = (src_desc.replace(" Loot", "").replace(" Chest", ""))
        chest_id = sid(chest_name)
        if chest_id not in _UNUSED_CHESTS:
            _UNUSED_CHESTS[chest_id] = {"name": chest_name, "items": []}
        _UNUSED_CHESTS[chest_id]["items"].append(ing_name)

    else:  # events + rewards → treat as chests/droplists
        event_name = (src_desc.replace(" Event", "").replace(" Reward", ""))
        event_id = sid(event_name)
        if event_id not in _UNUSED_CHESTS:
            _UNUSED_CHESTS[event_id] = {"name": src_desc, "items": []}
        _UNUSED_CHESTS[event_id]["items"].append(ing_name)

# Build entity lists
UNUSED_NPC_LIST   = []
UNUSED_NPC_CONVS  = []
UNUSED_NPC_DROPS  = []
UNUSED_MONSTER_LIST   = []
UNUSED_MONSTER_DROPS  = []
UNUSED_FORAGE_DROPS   = []
UNUSED_CHEST_DROPS    = []

for src_id, shop_data in _UNUSED_SHOPKEEPERS.items():
    npc_id  = f"npc_{src_id}"
    conv_id = f"conv_{src_id}_greeting"
    dl_id   = f"dl_{src_id}"
    shop_items = [{"itemID": sid(i), "chance": "100", "quantity": {"min": 1, "max": 2}}
                  for i in shop_data["items"]]
    UNUSED_NPC_LIST.append({
        "id": npc_id,
        "name": shop_data["name"],
        "iconID": "npc_human:4",
        "conversation": f"conv_{src_id}",
        "droplist": dl_id
    })
    UNUSED_NPC_CONVS.append({
        "id": conv_id,
        "text": f"I sell rare ingredients and materials from {shop_data['name']}."
    })
    UNUSED_NPC_DROPS.append({"id": dl_id, "items": shop_items})

for mid, mdata in _UNUSED_MONSTERS.items():
    dl_id = f"dl_{mid}"
    dl_items = [{"itemID": sid(drop), "chance": "50", "quantity": {"min": 1, "max": 1}}
                for drop in mdata["drops"]]
    if dl_items:
        dl_items[0]["chance"] = "100"
    UNUSED_MONSTER_DROPS.append({"id": dl_id, "items": dl_items})
    UNUSED_MONSTER_LIST.append({
        "id": mid,
        "name": mdata["name"],
        "iconID": MONSTER_ICON,
        "maxHP": 250,
        "attackChance": 75,
        "attackDamage": {"min": 15, "max": 30},
        "moveCost": 4,
        "attackCost": 3,
        "droplist": dl_id,
        "faction": "monster"
    })

for fid, fdata in _UNUSED_FORAGES.items():
    dl_items = [{"itemID": sid(i), "chance": "30", "quantity": {"min": 1, "max": 1}}
                for i in fdata["items"]]
    UNUSED_FORAGE_DROPS.append({
        "id": f"dl_forage_{fid}",
        "items": dl_items
    })

for cid, cdata in _UNUSED_CHESTS.items():
    dl_items = [{"itemID": sid(i), "chance": "25", "quantity": {"min": 1, "max": 1}}
                for i in cdata["items"]]
    UNUSED_CHEST_DROPS.append({
        "id": f"dl_chest_{cid}",
        "items": dl_items
    })

# ============================================================
# CRAFTING TABLE CONVERSATION LISTS
# ============================================================

def _craft_entry(conv_id, text, skill_or_guild_cond, input_items, output_item_id, qty=1):
    """
    Build a conversation entry for a crafting interaction.
    input_items: list of (itemID_str, quantity_int)
    """
    requires = [req_inv_remove(iid, q) for iid, q in input_items]
    if skill_or_guild_cond:
        requires.append(req_actor_condition(skill_or_guild_cond))
    reply = {
        "text": "Craft",
        "nextPhraseID": "X",
        "rewards": [r_give_item(output_item_id, qty)],
    }
    if requires:
        reply["requires"] = requires
    return make_conv(conv_id, text, [reply])

def _ing_list_to_input(ingredients):
    return [(sid(ing), 1) for ing in ingredients]

def _ing_desc(ingredients):
    return ", ".join(ingredients)

# ============================================================
# AILMENT POTION CAULDRON (open — no guild rank required)
# Anyone can brew cure potions if they have ingredients.
# ============================================================

CONVERSATIONS["ailment_cauldron"] = []
for ailment, ingredients in AILMENT_INGREDIENTS.items():
    out_id = "potion_" + sid(ailment)
    CONVERSATIONS["ailment_cauldron"].append(_craft_entry(
        f"brew_cure_{sid(ailment)}",
        f"Brew Cure Potion: {ailment} [{_ing_desc(ingredients)}]",
        None,
        _ing_list_to_input(ingredients),
        out_id
    ))

# ============================================================
# GUILD SPELL CAULDRON — brew spell potions (guild level 5)
# ============================================================

for guild in SPELL_GUILDS:
    conv_key = f"cauldron_{guild}"
    CONVERSATIONS[conv_key] = []
    for spell, ingredients in SPELL_INGREDIENTS[guild]["offensive"].items():
        out_id = f"{sid(spell)}_potion"
        CONVERSATIONS[conv_key].append(_craft_entry(
            f"brew_{sid(spell)}_potion_{guild}",
            f"Brew {spell} Potion [{_ing_desc(ingredients)}]",
            f"{guild}_level_5",
            _ing_list_to_input(ingredients),
            out_id
        ))

# ============================================================
# SCROLL WRITING TABLE — write scrolls (guild level 3)
# Uses first 2 spell ingredients + blank scroll + enchanted ink.
# ============================================================

for guild in SPELL_GUILDS:
    conv_key = f"scroll_table_{guild}"
    CONVERSATIONS[conv_key] = []
    all_spells = {**SPELL_INGREDIENTS[guild]["offensive"], **SPELL_INGREDIENTS[guild]["defensive"]}
    for spell, ingredients in all_spells.items():
        out_id = f"{sid(spell)}_scroll"
        partial_ing = ingredients[:2]
        input_items = _ing_list_to_input(partial_ing) + [("blank_scroll", 1), ("enchanted_ink", 1)]
        CONVERSATIONS[conv_key].append(_craft_entry(
            f"write_{sid(spell)}_scroll_{guild}",
            f"Write Scroll of {spell} [{_ing_desc(partial_ing)}, Blank Scroll, Enchanted Ink]",
            f"{guild}_level_3",
            input_items,
            out_id
        ))

# ============================================================
# SPELL CRAFT TABLE — enchanted weapons & armors (guild level 7)
# ============================================================

for guild in SPELL_GUILDS:
    # Weapons (offensive spells, skip Wand/Staff weapon types)
    conv_key_w = f"craft_weapon_{guild}"
    CONVERSATIONS[conv_key_w] = []
    for i, spell in enumerate(SPELL_DATA[guild]["offensive"]):
        spell_id_s = sid(spell)
        weapon_type = WEAPON_TYPES[i % len(WEAPON_TYPES)]
        if weapon_type in ("Wand", "Staff"):
            continue
        out_id = f"{spell_id_s}_{sid(weapon_type)}"
        ingredients = SPELL_INGREDIENTS[guild]["offensive"][spell]
        base_weapon = BASE_WEAPONS[i % len(BASE_WEAPONS)]
        input_items = [(sid(base_weapon), 1)] + _ing_list_to_input(ingredients)
        CONVERSATIONS[conv_key_w].append(_craft_entry(
            f"craft_{spell_id_s}_{sid(weapon_type)}_{guild}",
            f"Craft {spell} {weapon_type} [{base_weapon}, {_ing_desc(ingredients)}]",
            f"{guild}_level_7",
            input_items,
            out_id
        ))

    # Armors (defensive spells)
    conv_key_a = f"craft_armor_{guild}"
    CONVERSATIONS[conv_key_a] = []
    slot_keys = list(ARMOR_SLOT_DATA.keys())
    for i, spell in enumerate(SPELL_DATA[guild]["defensive"]):
        spell_id_s = sid(spell)
        slot = slot_keys[i % len(slot_keys)]
        out_id = f"{spell_id_s}_{slot}"
        ingredients = SPELL_INGREDIENTS[guild]["defensive"][spell]
        base_armor_name, _ = BASE_ARMORS[i % len(BASE_ARMORS)]
        input_items = [(sid(base_armor_name), 1)] + _ing_list_to_input(ingredients)
        CONVERSATIONS[conv_key_a].append(_craft_entry(
            f"craft_{spell_id_s}_{slot}_{guild}",
            f"Craft {spell} {ARMOR_SLOT_DATA[slot]['suffix']} [{base_armor_name}, {_ing_desc(ingredients)}]",
            f"{guild}_level_7",
            input_items,
            out_id
        ))

# ============================================================
# SPELL CRAFT TABLE — wands & staffs (guild level 9)
# ============================================================

for guild in SPELL_GUILDS:
    conv_key = f"craft_wand_{guild}"
    CONVERSATIONS[conv_key] = []
    for i, spell in enumerate(SPELL_DATA[guild]["offensive"]):
        spell_id_s = sid(spell)
        weapon_type = WEAPON_TYPES[i % len(WEAPON_TYPES)]
        if weapon_type not in ("Wand", "Staff"):
            continue
        out_id = f"{spell_id_s}_{sid(weapon_type)}"
        ingredients = SPELL_INGREDIENTS[guild]["offensive"][spell]
        base_mat = "wand_core" if weapon_type == "Wand" else "staff_shaft"
        base_label = "Wand Core" if weapon_type == "Wand" else "Staff Shaft"
        input_items = [(base_mat, 1)] + _ing_list_to_input(ingredients)
        CONVERSATIONS[conv_key].append(_craft_entry(
            f"craft_{spell_id_s}_{sid(weapon_type)}_{guild}",
            f"Craft {spell} {weapon_type} [{base_label}, {_ing_desc(ingredients)}]",
            f"{guild}_level_9",
            input_items,
            out_id
        ))

# ============================================================
# JEWELRY MAKING TABLE (skill_jewelry_making)
# ============================================================

JEWELRY_RECIPES = {
    "Copper Ring":     [("copper_ore", 2), ("binding_wire", 1)],
    "Silver Ring":     [("silver_ore", 2), ("binding_wire", 1)],
    "Golden Ring":     [("gold_ore", 2), ("binding_wire", 1)],
    "Ruby Ring":       [("gold_ore", 1), ("ruby", 1), ("gem_setting_tool", 1)],
    "Emerald Ring":    [("gold_ore", 1), ("emerald", 1), ("gem_setting_tool", 1)],
    "Sapphire Ring":   [("gold_ore", 1), ("sapphire", 1), ("gem_setting_tool", 1)],
    "Moonstone Ring":  [("silver_ore", 1), ("moonstone", 1), ("gem_setting_tool", 1)],
    "Dragon Ring":     [("gold_ore", 1), ("dragonstone", 1), ("gem_setting_tool", 1)],
    "Copper Bracelet": [("copper_ore", 3)],
    "Silver Bracelet": [("silver_ore", 2), ("binding_wire", 1)],
    "Golden Bracelet": [("gold_ore", 2), ("binding_wire", 1)],
    "Obsidian Bracelet":[("obsidian", 2), ("silver_ore", 1)],
    "Crystal Bracelet":[("crystal_shard", 2), ("silver_ore", 1)],
    "Copper Necklace": [("copper_ore", 2), ("leather_straps", 1)],
    "Silver Necklace": [("silver_ore", 2), ("leather_straps", 1)],
    "Golden Necklace": [("gold_ore", 2), ("leather_straps", 1)],
    "Ruby Necklace":   [("gold_ore", 1), ("ruby", 1), ("gem_setting_tool", 1)],
    "Emerald Necklace":[("gold_ore", 1), ("emerald", 1), ("gem_setting_tool", 1)],
    "Sapphire Necklace":[("gold_ore", 1), ("sapphire", 1), ("gem_setting_tool", 1)],
    "Moon Pendant":    [("silver_ore", 1), ("moonstone", 1), ("leather_straps", 1)],
    "Sun Pendant":     [("gold_ore", 1), ("sunstone", 1), ("leather_straps", 1)],
    "Crystal Charm":   [("crystal_shard", 2), ("binding_wire", 1)],
    "Bone Charm":      [("bone", 2), ("leather_straps", 1)],
    "Ancient Talisman":[("jade", 2), ("leather_straps", 1)],
    "Wizard Charm":    [("mana_crystal", 1), ("silver_ore", 1), ("gem_setting_tool", 1)],
}

CONVERSATIONS["jewelry_table"] = []
for item_name, ingredients in JEWELRY_RECIPES.items():
    out_id = sid(item_name)
    ing_desc_text = ", ".join(
        f"{iid.replace('_',' ').title()} x{qty}" for iid, qty in ingredients
    )
    CONVERSATIONS["jewelry_table"].append(_craft_entry(
        f"craft_{out_id}",
        f"Craft {item_name} [{ing_desc_text}]",
        "skill_jewelry_making",
        ingredients,
        out_id
    ))

# ============================================================
# SEWING LOOM (skill_sewing)
# ============================================================

_CLOTH_MAP = {
    "wool":     "wool_cloth",
    "silk":     "silk_cloth",
    "traveler": "linen_cloth",
    "feather":  "feather_material",
    "fur":      "fur_pelt",
    "cloth":    "linen_cloth",
    "leather":  "leather_hide",
    "work":     "linen_cloth",
    "dark":     "leather_hide",
    "night":    "linen_cloth",
    "shadow":   "leather_hide",
}

CONVERSATIONS["sewing_loom"] = []
for item_name, slot in CLOTHING_ITEMS:
    out_id = sid(item_name)
    cloth_id = "linen_cloth"
    for keyword, cid in _CLOTH_MAP.items():
        if keyword in item_name.lower():
            cloth_id = cid
            break
    ing_text = f"{cloth_id.replace('_',' ').title()} x2, Sewing Kit x1"
    CONVERSATIONS["sewing_loom"].append(_craft_entry(
        f"sew_{out_id}",
        f"Sew {item_name} [{ing_text}]",
        "skill_sewing",
        [(cloth_id, 2), ("sewing_kit", 1)],
        out_id
    ))

# ============================================================
# COOKING STOVE (skill_cooking)
# ============================================================

COOKING_RECIPES = {
    "Rabbit Stew":     [("garden_carrot", 1), ("garden_onion", 1), ("cooking_spice", 1)],
    "Beef Roast":      [("leather_hide", 1), ("cooking_spice", 2), ("salt_sack", 1)],
    "Herb Soup":       [("garden_garlic", 1), ("garden_parsley", 1), ("salt_sack", 1)],
    "Fish Chowder":    [("fish_scale", 1), ("garden_potato", 1), ("cooking_spice", 1)],
    "Apple Pie":       [("garden_apple", 2), ("garden_berry", 1)],
    "Berry Tart":      [("garden_strawberry", 2), ("garden_blueberry", 1)],
    "Vegetable Stew":  [("garden_potato", 1), ("garden_carrot", 1), ("garden_cabbage", 1)],
    "Spiced Wolf Meat":[("wolf_pelt", 1), ("cooking_spice", 2), ("salt_sack", 1)],
    "Roasted Boar":    [("boar_tusk", 1), ("cooking_spice", 2), ("salt_sack", 1)],
    "Mushroom Soup":   [("garden_mushroom", 2), ("garden_onion", 1), ("salt_sack", 1)],
    "Honey Bread":     [("garden_corn", 2), ("golden_nectar", 1)],
    "Cheese Platter":  [("garden_garlic", 1), ("salt_sack", 1), ("garden_parsley", 1)],
    "Grilled Salmon":  [("salmon_scale", 1), ("garden_parsley", 1), ("cooking_spice", 1)],
    "Baked Potato":    [("garden_potato", 2), ("salt_sack", 1)],
    "Garlic Chicken":  [("chicken_feather", 1), ("garden_garlic", 2), ("cooking_spice", 1)],
    "Fried Catfish":   [("catfish_scale", 1), ("cooking_spice", 1), ("salt_sack", 1)],
    "Pepper Steak":    [("leather_hide", 1), ("garden_pepper", 2), ("cooking_spice", 1)],
    "Mint Salad":      [("garden_lettuce", 2), ("garden_mint", 1)],
    "Pumpkin Soup":    [("garden_pumpkin", 2), ("cooking_spice", 1), ("salt_sack", 1)],
    "Roasted Duck":    [("duck_feather", 1), ("cooking_spice", 1), ("garden_apple", 1)],
    "Traveler Rations":[("garden_carrot", 1), ("garden_potato", 1), ("salt_sack", 1)],
    "Sweet Roll":      [("garden_corn", 2), ("garden_berry", 1)],
    "Berry Porridge":  [("garden_berry", 2), ("garden_bean", 1)],
    "Seafood Platter": [("crab_shell", 1), ("fish_scale", 1), ("cooking_spice", 1)],
    "Golden Omelet":   [("chicken_feather", 2), ("cooking_spice", 1), ("salt_sack", 1)],
}

CONVERSATIONS["cooking_stove"] = []
for meal_name, ingredients in COOKING_RECIPES.items():
    out_id = sid(meal_name)
    ing_text = ", ".join(f"{iid.replace('_',' ').title()} x{qty}" for iid, qty in ingredients)
    CONVERSATIONS["cooking_stove"].append(_craft_entry(
        f"cook_{out_id}",
        f"Cook {meal_name} [{ing_text}]",
        "skill_cooking",
        ingredients,
        out_id
    ))

# ============================================================
# GARDEN PLOT (skill_gardening)
# Plant seeds with fertile soil to grow crops.
# ============================================================

CONVERSATIONS["garden_plot"] = []
for crop in GARDENING:
    seed_id = f"garden_{sid(crop)}_seed"
    out_id  = f"garden_{sid(crop)}"
    CONVERSATIONS["garden_plot"].append(_craft_entry(
        f"plant_{out_id}",
        f"Plant {crop} [{crop} Seed x1, Fertile Soil x1]",
        "skill_gardening",
        [(seed_id, 1), ("fertile_soil", 1)],
        out_id
    ))

# ============================================================
# FORGE (skill_weaponsmithing)
# ============================================================

_FORGE_MAT_MAP = {
    "iron":       [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "steel":      [("iron_ore", 2), ("nickel_ore", 1), ("coal", 2), ("weapon_hilt", 1)],
    "bronze":     [("copper_ore", 2), ("tin_ore", 1), ("coal", 1), ("weapon_hilt", 1)],
    "war":        [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "battle":     [("iron_ore", 4), ("coal", 3), ("weapon_hilt", 1)],
    "knight":     [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "hunter":     [("iron_ore", 2), ("coal", 1), ("weapon_hilt", 1)],
    "oak":        [("iron_ore", 1), ("coal", 1), ("weapon_hilt", 1)],
    "crystal":    [("crystal_shard", 2), ("silver_ore", 1), ("weapon_hilt", 1)],
    "bone":       [("bone", 3), ("iron_ore", 1), ("weapon_hilt", 1)],
    "silver":     [("silver_ore", 2), ("coal", 1), ("weapon_hilt", 1)],
    "obsidian":   [("obsidian", 2), ("iron_ore", 1), ("weapon_hilt", 1)],
    "spiked":     [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "heavy":      [("iron_ore", 4), ("coal", 3), ("weapon_hilt", 1)],
    "forged":     [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "executioner":[("iron_ore", 4), ("coal", 3), ("weapon_hilt", 1)],
    "tower":      [("iron_ore", 4), ("coal", 3), ("weapon_hilt", 1)],
    "mercenary":  [("iron_ore", 2), ("coal", 1), ("weapon_hilt", 1)],
    "legionnaire":[("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "reinforced": [("iron_ore", 2), ("coal", 2), ("weapon_hilt", 1)],
    "tempered":   [("iron_ore", 2), ("coal", 2), ("weapon_hilt", 1)],
    "barbed":     [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "crusader":   [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "warlord":    [("iron_ore", 4), ("coal", 3), ("weapon_hilt", 1)],
    "arena":      [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "veteran":    [("iron_ore", 3), ("coal", 2), ("weapon_hilt", 1)],
    "champion":   [("iron_ore", 5), ("coal", 4), ("weapon_hilt", 1)],
}

CONVERSATIONS["forge"] = []
for weapon in BASE_WEAPONS + FIGHTER_WEAPONS:
    out_id = sid(weapon)
    first_word = weapon.split()[0].lower()
    ingredients = _FORGE_MAT_MAP.get(first_word, [("iron_ore", 2), ("coal", 1), ("weapon_hilt", 1)])
    ing_text = ", ".join(f"{iid.replace('_',' ').title()} x{qty}" for iid, qty in ingredients)
    CONVERSATIONS["forge"].append(_craft_entry(
        f"forge_{out_id}",
        f"Forge {weapon} [{ing_text}]",
        "skill_weaponsmithing",
        ingredients,
        out_id
    ))

# ============================================================
# ARMOR TABLE (skill_armorsmithing)
# ============================================================

_ARMOR_MAT_MAP = {
    "leather":     [("leather_hide", 2), ("leather_straps", 2), ("armor_rivets", 2)],
    "iron":        [("iron_ore", 3), ("coal", 1), ("armor_rivets", 3)],
    "traveler":    [("leather_hide", 1), ("linen_cloth", 1), ("leather_straps", 1)],
    "chain":       [("iron_ore", 2), ("armor_rivets", 4)],
    "bone":        [("bone", 3), ("leather_straps", 2)],
    "steel":       [("iron_ore", 2), ("nickel_ore", 1), ("coal", 2), ("armor_rivets", 3)],
    "shadow":      [("leather_hide", 2), ("leather_straps", 2), ("armor_rivets", 2)],
    "silent":      [("leather_hide", 2), ("leather_straps", 1)],
    "night":       [("leather_hide", 2), ("leather_straps", 1)],
    "cutpurse":    [("leather_hide", 1), ("leather_straps", 1)],
    "black":       [("leather_hide", 2), ("leather_straps", 2)],
    "smoke":       [("leather_hide", 1), ("leather_straps", 1)],
    "whisper":     [("linen_cloth", 1), ("leather_straps", 1)],
    "bandit":      [("leather_hide", 1), ("linen_cloth", 1)],
    "rogue":       [("leather_hide", 1), ("linen_cloth", 1), ("leather_straps", 1)],
    "pickpocket":  [("leather_hide", 1), ("leather_straps", 1)],
    "locksmith":   [("leather_hide", 1), ("armor_rivets", 2)],
    "softstep":    [("leather_hide", 1), ("leather_straps", 1)],
    "nightwalker": [("leather_hide", 1), ("leather_straps", 2)],
    "nightweave":  [("leather_hide", 2), ("silk_cloth", 1), ("leather_straps", 1)],
    "dark":        [("leather_hide", 3), ("leather_straps", 2)],
}

CONVERSATIONS["armor_table"] = []
all_armors_combined = list(BASE_ARMORS) + list(THIEF_ARMORS)
for armor_name, slot in all_armors_combined:
    out_id = sid(armor_name)
    first_word = armor_name.split()[0].lower()
    ingredients = _ARMOR_MAT_MAP.get(first_word, [("leather_hide", 2), ("armor_rivets", 2)])
    ing_text = ", ".join(f"{iid.replace('_',' ').title()} x{qty}" for iid, qty in ingredients)
    CONVERSATIONS["armor_table"].append(_craft_entry(
        f"craft_armor_{out_id}",
        f"Craft {armor_name} [{ing_text}]",
        "skill_armorsmithing",
        ingredients,
        out_id
    ))

# ============================================================
# WRITE SHOPKEEPER FILES
# ============================================================

for shop_type, items in SHOPKEEPER_ITEMS.items():
    write_json(RAW / f"itemlist_shop_{shop_type}.json", items)

for shop_type, conv in SHOPKEEPER_CONVERSATIONS.items():
    write_json(RAW / f"conversationlist_shop_{shop_type}.json", conv)

for shop_type, drops in SHOPKEEPER_DROPLISTS.items():
    write_json(RAW / f"droplists_shop_{shop_type}.json", [
        {"id": f"droplist_shop_{shop_type}", "items": drops}
    ])

# ============================================================
# WRITE THIEF TOOLS
# ============================================================

write_json(RAW / "itemlist_thief_tools.json", ITEMLISTS["thief_tools"])
write_json(RAW / "itemcategories_thief_tools.json", ITEMCATEGORIES["thief_tools"])

# ============================================================
# WRITE MAIN JSON FILES
# ============================================================

write_json(RAW / "itemlist_animal.json",         ITEMLISTS["animal"])
write_json(RAW / "monsterlist_animal.json",       MONSTERLISTS["animal"])
write_json(RAW / "droplists_animal.json",         DROPLISTS["animal"])
write_json(RAW / "itemcategories_animal.json",    ITEMCATEGORIES["animal"])
write_json(RAW / "itemlist_forage.json",          ITEMLISTS["forage"])
write_json(RAW / "itemcategories_forage.json",    ITEMCATEGORIES["forage"])
write_json(RAW / "itemlist_special_forage.json",  ITEMLISTS["special_forage"])
write_json(RAW / "droplists_special_forage.json", DROPLISTS["special_forage"])
write_json(RAW / "itemlist_mining.json",          ITEMLISTS["mining"])
write_json(RAW / "itemcategories_mining.json",    ITEMCATEGORIES["mining"])
write_json(RAW / "itemlist_gardening.json",       ITEMLISTS["gardening"])
write_json(RAW / "itemcategories_gardening.json", ITEMCATEGORIES["gardening"])
write_json(RAW / "actorconditions_ailment.json",  ACTORCONDITIONS["ailment"])
write_json(RAW / "itemlist_ailment.json",         ITEMLISTS["ailment"])
write_json(RAW / "itemlist_craft.json",           ITEMLISTS["craft"])
write_json(RAW / "itemcategories_craft.json",     ITEMCATEGORIES["craft"])
write_json(RAW / "itemlist_clothing.json",        ITEMLISTS["clothing"])
write_json(RAW / "itemcategories_clothing.json",  ITEMCATEGORIES["clothing"])
write_json(RAW / "itemlist_jewelry.json",         ITEMLISTS["jewelry"])
write_json(RAW / "itemcategories_jewelry.json",   ITEMCATEGORIES["jewelry"])
write_json(RAW / "itemlist_meals.json",           ITEMLISTS["meals"])
write_json(RAW / "itemcategories_meals.json",     ITEMCATEGORIES["meals"])
write_json(RAW / "itemlist_fighter.json",         ITEMLISTS["fighter"])
write_json(RAW / "itemcategories_fighter.json",   ITEMCATEGORIES["fighter"])
write_json(RAW / "itemlist_thief.json",           ITEMLISTS["thief"])
write_json(RAW / "itemcategories_thief.json",     ITEMCATEGORIES["thief"])
write_json(RAW / "itemlist_spell_materials.json", ITEMLISTS["spell_materials"])
write_json(RAW / "itemcategories_spell_materials.json", ITEMCATEGORIES["spell_materials"])
write_json(RAW / "itemlist_crafting_materials.json",    ITEMLISTS["crafting_materials"])
write_json(RAW / "itemcategories_crafting_materials.json", ITEMCATEGORIES["crafting_materials"])

# Unused ingredient source entities
write_json(RAW / "monsterlist_unused_sources.json",  UNUSED_MONSTER_LIST)
write_json(RAW / "droplists_unused_monsters.json",   UNUSED_MONSTER_DROPS)
write_json(RAW / "droplists_unused_forages.json",    UNUSED_FORAGE_DROPS)
write_json(RAW / "droplists_unused_chests.json",     UNUSED_CHEST_DROPS)
write_json(RAW / "monsterlist_unused_shopkeepers.json", UNUSED_NPC_LIST)
write_json(RAW / "conversationlist_unused_shopkeepers.json", UNUSED_NPC_CONVS)
write_json(RAW / "droplists_unused_shopkeepers.json",   UNUSED_NPC_DROPS)

# Actor conditions (exclude non-existent)
write_json(RAW / "actorconditions_adventurer.json", ACTORCONDITIONS.get("adventurer", []))
write_json(RAW / "actorconditions_fighter.json",    ACTORCONDITIONS.get("fighter", []))
write_json(RAW / "actorconditions_thief.json",      ACTORCONDITIONS.get("thief", []))
write_json(RAW / "actorconditions_skills.json",     ACTORCONDITIONS.get("skills", []))

for guild in SPELL_GUILDS:
    write_json(RAW / f"actorconditions_{guild}.json",    ACTORCONDITIONS[guild])
    write_json(RAW / f"itemlist_weapon_{guild}.json",    ITEMLISTS[f"weapon_{guild}"])
    write_json(RAW / f"itemlist_scroll_{guild}.json",    ITEMLISTS[f"scroll_{guild}"])
    write_json(RAW / f"itemlist_potion_{guild}.json",    ITEMLISTS[f"potion_{guild}"])
    write_json(RAW / f"itemlist_armor_{guild}.json",     ITEMLISTS[f"armor_{guild}"])
    write_json(RAW / f"itemcategories_{guild}.json",     ITEMCATEGORIES[guild])

# ============================================================
# WRITE CRAFTING TABLE CONVERSATION LISTS
# ============================================================

write_json(RAW / "conversationlist_ailment_cauldron.json",  CONVERSATIONS["ailment_cauldron"])
write_json(RAW / "conversationlist_jewelry_table.json",     CONVERSATIONS["jewelry_table"])
write_json(RAW / "conversationlist_sewing_loom.json",       CONVERSATIONS["sewing_loom"])
write_json(RAW / "conversationlist_cooking_stove.json",     CONVERSATIONS["cooking_stove"])
write_json(RAW / "conversationlist_garden_plot.json",       CONVERSATIONS["garden_plot"])
write_json(RAW / "conversationlist_forge.json",             CONVERSATIONS["forge"])
write_json(RAW / "conversationlist_armor_table.json",       CONVERSATIONS["armor_table"])

for guild in SPELL_GUILDS:
    write_json(RAW / f"conversationlist_cauldron_{guild}.json",       CONVERSATIONS[f"cauldron_{guild}"])
    write_json(RAW / f"conversationlist_scroll_table_{guild}.json",   CONVERSATIONS[f"scroll_table_{guild}"])
    write_json(RAW / f"conversationlist_craft_weapon_{guild}.json",   CONVERSATIONS[f"craft_weapon_{guild}"])
    write_json(RAW / f"conversationlist_craft_armor_{guild}.json",    CONVERSATIONS[f"craft_armor_{guild}"])
    write_json(RAW / f"conversationlist_craft_wand_{guild}.json",     CONVERSATIONS[f"craft_wand_{guild}"])

# ============================================================
# WRITE GUILD NPC FILES
# ============================================================

for guild in GUILDS:
    write_json(RAW / f"monsterlist_{guild}.json",      NPCS[guild])
    write_json(RAW / f"conversationlist_{guild}.json", CONVERSATIONS[guild])
    write_json(RAW / f"questlist_{guild}.json",        QUESTS[guild])

# ============================================================
# LOADRESOURCES.XML  (fixed: no .json extensions, fixed tag bug)
# ============================================================

LOADRESOURCES = """<?xml version="1.0" encoding="utf-8"?>
<resources>

    <array name="loadresource_actorconditions">
        <item>@raw/actorconditions_ailment</item>
        <item>@raw/actorconditions_mage</item>
        <item>@raw/actorconditions_cleric</item>
        <item>@raw/actorconditions_druid</item>
        <item>@raw/actorconditions_adventurer</item>
        <item>@raw/actorconditions_fighter</item>
        <item>@raw/actorconditions_thief</item>
        <item>@raw/actorconditions_skills</item>
    </array>

    <array name="loadresource_conversationlists">
        <item>@raw/conversationlist_adventurer</item>
        <item>@raw/conversationlist_fighter</item>
        <item>@raw/conversationlist_thief</item>
        <item>@raw/conversationlist_mage</item>
        <item>@raw/conversationlist_cleric</item>
        <item>@raw/conversationlist_druid</item>
        <item>@raw/conversationlist_shop_alchemist</item>
        <item>@raw/conversationlist_shop_armorer</item>
        <item>@raw/conversationlist_shop_blackmarket</item>
        <item>@raw/conversationlist_shop_crafter</item>
        <item>@raw/conversationlist_shop_farmer</item>
        <item>@raw/conversationlist_shop_grocer</item>
        <item>@raw/conversationlist_shop_jeweler</item>
        <item>@raw/conversationlist_shop_scribe</item>
        <item>@raw/conversationlist_shop_seamstress</item>
        <item>@raw/conversationlist_shop_weaponer</item>
        <item>@raw/conversationlist_unused_shopkeepers</item>
        <item>@raw/conversationlist_ailment_cauldron</item>
        <item>@raw/conversationlist_cauldron_mage</item>
        <item>@raw/conversationlist_cauldron_cleric</item>
        <item>@raw/conversationlist_cauldron_druid</item>
        <item>@raw/conversationlist_scroll_table_mage</item>
        <item>@raw/conversationlist_scroll_table_cleric</item>
        <item>@raw/conversationlist_scroll_table_druid</item>
        <item>@raw/conversationlist_craft_weapon_mage</item>
        <item>@raw/conversationlist_craft_weapon_cleric</item>
        <item>@raw/conversationlist_craft_weapon_druid</item>
        <item>@raw/conversationlist_craft_armor_mage</item>
        <item>@raw/conversationlist_craft_armor_cleric</item>
        <item>@raw/conversationlist_craft_armor_druid</item>
        <item>@raw/conversationlist_craft_wand_mage</item>
        <item>@raw/conversationlist_craft_wand_cleric</item>
        <item>@raw/conversationlist_craft_wand_druid</item>
        <item>@raw/conversationlist_jewelry_table</item>
        <item>@raw/conversationlist_sewing_loom</item>
        <item>@raw/conversationlist_cooking_stove</item>
        <item>@raw/conversationlist_garden_plot</item>
        <item>@raw/conversationlist_forge</item>
        <item>@raw/conversationlist_armor_table</item>
    </array>

    <array name="loadresource_droplists">
        <item>@raw/droplists_animal</item>
        <item>@raw/droplists_special_forage</item>
        <item>@raw/droplists_shop_alchemist</item>
        <item>@raw/droplists_shop_armorer</item>
        <item>@raw/droplists_shop_blackmarket</item>
        <item>@raw/droplists_shop_crafter</item>
        <item>@raw/droplists_shop_farmer</item>
        <item>@raw/droplists_shop_grocer</item>
        <item>@raw/droplists_shop_jeweler</item>
        <item>@raw/droplists_shop_scribe</item>
        <item>@raw/droplists_shop_seamstress</item>
        <item>@raw/droplists_shop_weaponer</item>
        <item>@raw/droplists_unused_monsters</item>
        <item>@raw/droplists_unused_forages</item>
        <item>@raw/droplists_unused_chests</item>
        <item>@raw/droplists_unused_shopkeepers</item>
    </array>

    <array name="loadresource_itemcategories">
        <item>@raw/itemcategories_animal</item>
        <item>@raw/itemcategories_forage</item>
        <item>@raw/itemcategories_mining</item>
        <item>@raw/itemcategories_gardening</item>
        <item>@raw/itemcategories_mage</item>
        <item>@raw/itemcategories_cleric</item>
        <item>@raw/itemcategories_druid</item>
        <item>@raw/itemcategories_craft</item>
        <item>@raw/itemcategories_clothing</item>
        <item>@raw/itemcategories_jewelry</item>
        <item>@raw/itemcategories_meals</item>
        <item>@raw/itemcategories_fighter</item>
        <item>@raw/itemcategories_thief</item>
        <item>@raw/itemcategories_thief_tools</item>
        <item>@raw/itemcategories_spell_materials</item>
        <item>@raw/itemcategories_crafting_materials</item>
    </array>

    <array name="loadresource_items">
        <item>@raw/itemlist_ailment</item>
        <item>@raw/itemlist_animal</item>
        <item>@raw/itemlist_forage</item>
        <item>@raw/itemlist_special_forage</item>
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
        <item>@raw/itemlist_craft</item>
        <item>@raw/itemlist_clothing</item>
        <item>@raw/itemlist_jewelry</item>
        <item>@raw/itemlist_meals</item>
        <item>@raw/itemlist_fighter</item>
        <item>@raw/itemlist_thief</item>
        <item>@raw/itemlist_thief_tools</item>
        <item>@raw/itemlist_spell_materials</item>
        <item>@raw/itemlist_crafting_materials</item>
        <item>@raw/itemlist_shop_alchemist</item>
        <item>@raw/itemlist_shop_armorer</item>
        <item>@raw/itemlist_shop_blackmarket</item>
        <item>@raw/itemlist_shop_crafter</item>
        <item>@raw/itemlist_shop_farmer</item>
        <item>@raw/itemlist_shop_grocer</item>
        <item>@raw/itemlist_shop_jeweler</item>
        <item>@raw/itemlist_shop_scribe</item>
        <item>@raw/itemlist_shop_seamstress</item>
        <item>@raw/itemlist_shop_weaponer</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_animal</item>
        <item>@raw/monsterlist_adventurer</item>
        <item>@raw/monsterlist_fighter</item>
        <item>@raw/monsterlist_thief</item>
        <item>@raw/monsterlist_mage</item>
        <item>@raw/monsterlist_cleric</item>
        <item>@raw/monsterlist_druid</item>
        <item>@raw/monsterlist_unused_sources</item>
        <item>@raw/monsterlist_unused_shopkeepers</item>
    </array>

    <array name="loadresource_quests">
        <item>@raw/questlist_adventurer</item>
        <item>@raw/questlist_fighter</item>
        <item>@raw/questlist_thief</item>
        <item>@raw/questlist_mage</item>
        <item>@raw/questlist_cleric</item>
        <item>@raw/questlist_druid</item>
    </array>

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

    # Spawn_animal
    spawn_layer = ET.SubElement(root, "objectgroup")
    spawn_layer.set("name", "Spawn_animal")
    spawn = ET.SubElement(spawn_layer, "object")
    spawn.set("id", "1"); spawn.set("type","spawn"); spawn.set("x", "0"); spawn.set("y", "0")
    spawn.set("width", "960"); spawn.set("height", "960")
    props = ET.SubElement(spawn, "properties")
    ET.SubElement(props, "property", name="spawnGroup", value=f"animal_{region}")
    ET.SubElement(props, "property", name="spawnCount", value="3")

    # Spawn_faction
    spawn_layer = ET.SubElement(root, "objectgroup")
    spawn_layer.set("name", "Spawn_faction")
    spawn = ET.SubElement(spawn_layer, "object")
    spawn.set("id", "1"); spawn.set("type","spawn"); spawn.set("x", "0"); spawn.set("y", "0")
    spawn.set("width", "960"); spawn.set("height", "960")
    props = ET.SubElement(spawn, "properties")
    ET.SubElement(props, "property", name="spawnGroup", value="faction")
    ET.SubElement(props, "property", name="spawnCount", value="3")

    # Keys_forage (special forage droplist)
    forage_layer = ET.SubElement(root, "objectgroup")
    forage_layer.set("name", "Keys_forage")
    obj = ET.SubElement(forage_layer, "object")
    obj.set("id", "2"); obj.set("x", "128"); obj.set("y", "128")
    obj.set("width", "32"); obj.set("height", "32")
    props = ET.SubElement(obj, "properties")
    ET.SubElement(props, "property", name="droplist", value=f"dl_forage_{region}")
    ET.SubElement(props, "property", name="respawnHours", value="24")

    # Keys_mining
    mining_layer = ET.SubElement(root, "objectgroup")
    mining_layer.set("name", "Keys_mining")
    obj = ET.SubElement(mining_layer, "object")
    obj.set("id", "3"); obj.set("x", "256"); obj.set("y", "256")
    obj.set("width", "32"); obj.set("height", "32")
    props = ET.SubElement(obj, "properties")
    ET.SubElement(props, "property", name="droplist", value="dl_all_mining")
    ET.SubElement(props, "property", name="requiredWeapon", value="tool_pickaxe")
    ET.SubElement(props, "property", name="respawnHours", value="48")

    # Keys_garden
    garden_layer = ET.SubElement(root, "objectgroup")
    garden_layer.set("name", "Keys_garden")
    obj = ET.SubElement(garden_layer, "object")
    obj.set("id", "4"); obj.set("x", "384"); obj.set("y", "384")
    obj.set("width", "32"); obj.set("height", "32")
    props = ET.SubElement(obj, "properties")
    ET.SubElement(props, "property", name="droplist", value="dl_all_garden")
    ET.SubElement(props, "property", name="requiredWeapon", value="tool_hoe")
    ET.SubElement(props, "property", name="respawnHours", value="72")

    # Keys_garden_plant
    plant_layer = ET.SubElement(root, "objectgroup")
    plant_layer.set("name", "Keys_garden_plant")
    obj = ET.SubElement(plant_layer, "object")
    obj.set("id", "5"); obj.set("x", "512"); obj.set("y", "512")
    obj.set("width", "32"); obj.set("height", "32")
    props = ET.SubElement(obj, "properties")
    ET.SubElement(props, "property", name="requiredWeapon", value="tool_hoe")
    ET.SubElement(props, "property", name="yieldMultiplier", value="3")
    ET.SubElement(props, "property", name="respawnHours", value="72")

    ET.indent(root)
    tree = ET.ElementTree(root)
    tree.write(XML / f"template_{region}.tmx", encoding="utf-8", xml_declaration=True)

# ============================================================
# GUILD TMX MAPS
# ============================================================

GUILDS_ALL = ["adventurer", "fighter", "thief", "mage", "cleric", "druid"]

for guild in GUILDS_ALL:

    guild_root = deepcopy(template_root)
    npc_layer = ET.SubElement(guild_root, "objectgroup")
    npc_layer.set("name", "Spawn_npc")

    for obj_id, npc_id, x, y in [
        ("100", f"grandmaster_{guild}", 128, 128),
        ("101", f"leader_{guild}",      256, 128),
        ("102", f"scholar_{guild}",     384, 128),
    ]:
        obj = ET.SubElement(npc_layer, "object")
        obj.set("id", obj_id); obj.set("name", npc_id); obj.set("type", "spawn"); obj.set("x", str(x)); obj.set("y", str(y))
        obj.set("width", "32"); obj.set("height", "32")
        props = ET.SubElement(obj, "properties")
        ET.SubElement(props, "property", name="spawngroup", value=npc_id)

    ET.indent(guild_root)
    guild_tree = ET.ElementTree(guild_root)
    guild_tree.write(XML / f"guild_{guild}.tmx", encoding="utf-8", xml_declaration=True)

# ============================================================
# TMX SHOPKEEPER NPC PLACEMENT
# ============================================================

GUILD_MAPS = {
    g: f"guild_{g}.tmx" for g in GUILDS_ALL
}

NPC_POSITIONS = {
    "adventurer": [
        ("shop_jeweler_adventurer",    10, 12),
        ("shop_seamstress_adventurer", 12, 12),
        ("shop_grocer_adventurer",     14, 12),
        ("shop_farmer_adventurer",     16, 12),
        ("shop_weaponer_adventurer",   18, 12),
        ("shop_armorer_adventurer",    20, 12)
    ],
    "fighter": [("shop_weaponer_fighter", 12, 10)],
    "thief":   [("shop_armorer_thief", 10, 10), ("shop_blackmarket_thief", 14, 10)],
    "mage":    [("shop_scribe_mage", 10, 10), ("shop_alchemist_mage", 14, 10), ("shop_crafter_mage", 18, 10)],
    "cleric":  [("shop_scribe_cleric", 10, 10), ("shop_alchemist_cleric", 14, 10), ("shop_crafter_cleric", 18, 10)],
    "druid":   [("shop_scribe_druid", 10, 10), ("shop_alchemist_druid", 14, 10), ("shop_crafter_druid", 18, 10)]
}

def add_npc_to_map(tmx_path, npc_id, x, y):
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    objectgroup = None
    for layer in root.findall("objectgroup"):
        if layer.get("name") == "Spawn":
            objectgroup = layer
            break
    if objectgroup is None:
        objectgroup = ET.SubElement(root, "objectgroup", {"id": "99", "name": "NPCs"})
    obj = ET.SubElement(objectgroup, "object", {
        "name": npc_id, "type": "spawn",
        "x": str(x * 32), "y": str(y * 32), "width": "32", "height": "32"
    })
    properties = ET.SubElement(obj, "properties")
    ET.SubElement(properties, "property", {"name": "spawngroup", "value": npc_id})
    tree.write(tmx_path, encoding="utf-8", xml_declaration=True)

for guild, filename in GUILD_MAPS.items():
    tmx_path = XML / filename
    if not tmx_path.exists():
        if TMX_TEMPLATE.exists():
            t = ET.parse(TMX_TEMPLATE)
            t.write(tmx_path, encoding="utf-8", xml_declaration=True)
        else:
            continue
    for npc_id, x, y in NPC_POSITIONS[guild]:
        add_npc_to_map(tmx_path, npc_id, x, y)

# ============================================================
# COMPLETE
# ============================================================

print("")
print("=" * 48)
print("Generation Complete")
print("=" * 48)
print(f"Raw JSON files : {len(list(RAW.glob('*.json')))}")
print(f"TMX map files  : {len(list(XML.glob('*.tmx')))}")
print(f"Item lists     : {len(ITEMLISTS)}")
print(f"Item categories: {len(ITEMCATEGORIES)}")
print(f"Monsters       : {len(MONSTERLISTS)}")
print(f"Droplists      : {len(DROPLISTS)}")
print(f"Actor conditions:{len(ACTORCONDITIONS)}")
print(f"Conversations  : {len(CONVERSATIONS)}")
print("")
print("Crafting conversations generated:")
print(f"  Ailment cauldron    : {len(CONVERSATIONS['ailment_cauldron'])} recipes")
for g in SPELL_GUILDS:
    print(f"  {g.title()} cauldron    : {len(CONVERSATIONS[f'cauldron_{g}'])} recipes")
    print(f"  {g.title()} scroll table: {len(CONVERSATIONS[f'scroll_table_{g}'])} recipes")
    print(f"  {g.title()} weapon craft: {len(CONVERSATIONS[f'craft_weapon_{g}'])} recipes")
    print(f"  {g.title()} armor craft : {len(CONVERSATIONS[f'craft_armor_{g}'])} recipes")
    print(f"  {g.title()} wand craft  : {len(CONVERSATIONS[f'craft_wand_{g}'])} recipes")
print(f"  Jewelry table       : {len(CONVERSATIONS['jewelry_table'])} recipes")
print(f"  Sewing loom         : {len(CONVERSATIONS['sewing_loom'])} recipes")
print(f"  Cooking stove       : {len(CONVERSATIONS['cooking_stove'])} recipes")
print(f"  Garden plot         : {len(CONVERSATIONS['garden_plot'])} recipes")
print(f"  Forge               : {len(CONVERSATIONS['forge'])} recipes")
print(f"  Armor table         : {len(CONVERSATIONS['armor_table'])} recipes")
print("")
print("Unused ingredient sources resolved:")
print(f"  Shopkeeper NPCs     : {len(UNUSED_NPC_LIST)}")
print(f"  Special monsters    : {len(UNUSED_MONSTER_LIST)}")
print(f"  Forage droplists    : {len(UNUSED_FORAGE_DROPS)}")
print(f"  Chest droplists     : {len(UNUSED_CHEST_DROPS)}")
print("")
print("Done.")

