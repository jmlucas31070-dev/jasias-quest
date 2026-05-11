#!/usr/bin/env python3

import json
import os
import random

# ============================================================
# HOLIDAY + HORROR RESOURCE GENERATOR
#
# Generates:
#   ./raw/itemlist_holiday.json
#   ./raw/monsterlist_holiday.json
#   ./raw/itemlist_horror.json
#   ./raw/monsterlist_horror.json
#   ./raw/droplists_horror.json
#   ./raw/itemlist_tower.json
#   ./raw/monsterlist_tower.json
#   ./raw/droplists_tower.json
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
        <item>@raw/itemlist_holiday</item>
        <item>@raw/itemlist_horror</item>
        <item>@raw/itemlist_tower</item>
    </array>

    <array name="loadresource_droplists">
        <item>@raw/droplists_horror</item>
        <item>@raw/droplists_tower</item>
    </array>

    <array name="loadresource_monsters">
        <item>@raw/monsterlist_holiday</item>
        <item>@raw/monsterlist_horror</item>
        <item>@raw/monsterlist_tower</item>
    </array>

</resources>
"""

# ============================================================
# HOLIDAYS
# ============================================================

HOLIDAYS = {
    "new_years": [
        "Firework Bundle",
        "Golden Champagne",
        "Celebration Horn",
        "Lucky Coin",
        "Party Mask",
        "Clock Pendant",
        "Sparkler Wand",
        "Festive Banner",
        "New Year Cake",
        "Crystal Confetti",
        "Silver Goblet",
        "Fortune Scroll",
        "Midnight Lantern",
        "Moonfire Rocket",
        "Lucky Ribbon",
        "Joyful Drum",
        "Celestial Crown",
        "Starburst Orb",
        "Resolution Journal",
        "Golden Watch",
        "Festival Charm",
        "Victory Medal",
        "Sunrise Crystal",
        "Holiday Trumpet",
        "Prosperity Ring"
    ],

    "easter": [
        "Painted Egg",
        "Golden Bunny",
        "Spring Basket",
        "Chocolate Rabbit",
        "Flower Crown",
        "Pastel Ribbon",
        "Easter Candle",
        "Sunrise Egg",
        "Blooming Rose",
        "Spring Lantern",
        "Carrot Pie",
        "Sacred Lily",
        "Blessed Basket",
        "Honey Cookie",
        "Rabbit Charm",
        "Spring Bell",
        "Pasture Necklace",
        "Butterfly Brooch",
        "Daisy Bracelet",
        "Tulip Ring",
        "Eggshell Pendant",
        "Spring Cloak",
        "Joy Bouquet",
        "Festival Bonnet",
        "Bloom Pendant"
    ],

    "fourth_of_july": [
        "Patriot Banner",
        "Liberty Torch",
        "Firecracker Box",
        "Freedom Medal",
        "Festival Drum",
        "Rocket Firework",
        "Star Shield",
        "Liberty Ring",
        "Celebration Cape",
        "Freedom Flag",
        "Spark Fountain",
        "Patriot Necklace",
        "Honor Badge",
        "Festival Lantern",
        "Glory Ribbon",
        "Red White Cloak",
        "Blue Ember",
        "Victory Charm",
        "Liberty Crown",
        "Festival Gloves",
        "Star Pendant",
        "Skyfire Orb",
        "Rocket Tube",
        "Freedom Bracelet",
        "Celebration Staff"
    ],

    "halloween": [
        "Pumpkin Lantern",
        "Witch Hat",
        "Ghost Cloak",
        "Candy Basket",
        "Spider Ring",
        "Bat Pendant",
        "Haunted Doll",
        "Skull Mask",
        "Night Candle",
        "Bone Wand",
        "Cursed Pumpkin",
        "Black Rose",
        "Phantom Bell",
        "Shadow Orb",
        "Moonlit Charm",
        "Ghoul Lantern",
        "Specter Cloak",
        "Spider Brooch",
        "Raven Feather",
        "Dark Apple",
        "Tomb Key",
        "Soul Candle",
        "Crypt Pendant",
        "Monster Fang",
        "Necro Tome"
    ],

    "thanksgiving": [
        "Harvest Basket",
        "Golden Turkey",
        "Autumn Leaf",
        "Cornucopia",
        "Pumpkin Pie",
        "Harvest Lantern",
        "Family Necklace",
        "Warm Blanket",
        "Autumn Ring",
        "Festival Bread",
        "Harvest Bell",
        "Thankful Charm",
        "Corn Necklace",
        "Wooden Goblet",
        "Maple Cloak",
        "Autumn Crown",
        "Festival Mug",
        "Harvest Gloves",
        "Golden Wheat",
        "Oak Pendant",
        "Harvest Drum",
        "Warm Candle",
        "Blessing Scroll",
        "Turkey Feather",
        "Autumn Crystal"
    ],

    "christmas": [
        "Candy Cane",
        "Santa Hat",
        "Snow Globe",
        "Christmas Bell",
        "Winter Cloak",
        "Holiday Stocking",
        "Frost Lantern",
        "Silver Snowflake",
        "Toy Soldier",
        "Holiday Ribbon",
        "Christmas Candle",
        "Frozen Ornament",
        "Reindeer Charm",
        "Yule Log",
        "Winter Crown",
        "Gift Box",
        "Holiday Mittens",
        "Snow Crystal",
        "Elf Boots",
        "North Star Ring",
        "Jingle Pendant",
        "Holiday Drum",
        "Ice Bell",
        "Mistletoe Pendant",
        "Frostfire Orb"
    ],

    "birthday": [
        "Birthday Cake",
        "Party Balloon",
        "Gift Ribbon",
        "Celebration Hat",
        "Birthday Candle",
        "Golden Present",
        "Festival Necklace",
        "Party Horn",
        "Celebration Cloak",
        "Joy Bracelet",
        "Birthday Bell",
        "Candy Necklace",
        "Party Lantern",
        "Friendship Ring",
        "Gift Basket",
        "Celebration Gloves",
        "Birthday Medal",
        "Confetti Orb",
        "Golden Cake Slice",
        "Party Mask",
        "Friendship Charm",
        "Birthday Rose",
        "Festival Crown",
        "Spark Candle",
        "Party Crystal"
    ],

    "graduation": [
        "Graduate Cap",
        "Honor Medal",
        "Diploma Scroll",
        "Scholar Ring",
        "Wisdom Pendant",
        "Achievement Trophy",
        "Knowledge Tome",
        "Golden Feather",
        "Academic Cloak",
        "Victory Ribbon",
        "Scholar Gloves",
        "Graduation Bell",
        "Mastery Crown",
        "Achievement Badge",
        "Honor Bracelet",
        "Wisdom Orb",
        "Learning Crystal",
        "Graduate Lantern",
        "Study Journal",
        "Knowledge Charm",
        "Scholar Staff",
        "Honor Banner",
        "Success Medal",
        "Academic Brooch",
        "Victory Crown"
    ],

    "wedding": [
        "Wedding Ring",
        "White Rose",
        "Ceremony Candle",
        "Love Pendant",
        "Bride Veil",
        "Golden Bouquet",
        "Marriage Scroll",
        "Silver Goblet",
        "Sacred Ribbon",
        "Wedding Crown",
        "Unity Bracelet",
        "Ceremony Lantern",
        "Heart Charm",
        "Celebration Cloak",
        "Love Crystal",
        "Golden Promise",
        "Blessing Bell",
        "White Gloves",
        "Wedding Necklace",
        "Rose Crown",
        "Sacred Flame",
        "Love Brooch",
        "Marriage Seal",
        "Heart Ring",
        "Ceremony Orb"
    ],

    "funeral": [
        "Black Rose",
        "Memorial Candle",
        "Grief Pendant",
        "Silver Cross",
        "Funeral Veil",
        "Memory Ring",
        "Sacred Ashes",
        "Prayer Scroll",
        "Soul Lantern",
        "Remembrance Charm",
        "Silent Bell",
        "Mourning Cloak",
        "Cemetery Flower",
        "Spirit Candle",
        "Grave Token",
        "Blessed Ribbon",
        "Angel Feather",
        "Remembrance Medal",
        "Funeral Gloves",
        "Silent Rose",
        "Soul Crystal",
        "Prayer Beads",
        "Memorial Bracelet",
        "Peace Pendant",
        "Funeral Crown"
    ]
}

# ============================================================
# HORROR LOCATIONS
# ============================================================

LOCATIONS = {
    "haunted_house": [
        "Ghost", "Phantom", "Cursed Child", "Possessed Doll",
        "Haunted Butler", "Spirit Maid", "Shadow Beast",
        "Whispering Soul", "Dark Widow", "Rotting Guest"
    ],

    "haunted_mansion": [
        "Spectral Noble", "Ghost Baron", "Phantom Maid",
        "Shadow Knight", "Haunted Aristocrat", "Possessed Guard",
        "Ancient Spirit", "Dark Servant", "Soul Collector",
        "Cursed Duchess"
    ],

    "mausoleum": [
        "Bone Priest", "Ancient Wraith", "Tomb Guardian",
        "Soul Keeper", "Rotting Monk", "Crypt Specter",
        "Death Watcher", "Undead Saint", "Ash Spirit",
        "Funeral Shade"
    ],

    "crypt": [
        "Crypt Ghoul", "Bone Horror", "Dark Skeleton",
        "Tomb Spider", "Shadow Lurker", "Soul Drinker",
        "Necro Beast", "Death Hound", "Cursed Shade",
        "Crypt Phantom"
    ],

    "graveyard": [
        "Zombie", "Restless Spirit", "Grave Keeper",
        "Bone Crow", "Cemetery Ghoul", "Buried Horror",
        "Rotting Corpse", "Dark Raven", "Lost Soul",
        "Night Stalker"
    ],

    "haunted_prison": [
        "Ghost Prisoner", "Executioner", "Chain Specter",
        "Tormented Guard", "Prison Shade", "Death Row Spirit",
        "Iron Phantom", "Dark Inmate", "Wailing Soul",
        "Cursed Warden"
    ],

    "haunted_asylum": [
        "Mad Spirit", "Insane Patient", "Dark Doctor",
        "Twisted Nurse", "Hallway Phantom", "Lost Patient",
        "Lobotomy Horror", "Screaming Soul", "Asylum Beast",
        "Shadow Surgeon"
    ]
}

# ============================================================
# HORROR DROP ITEMS
# ============================================================

DROP_ITEMS = [
    "Haunted Bone",
    "Cursed Lantern",
    "Dark Crystal",
    "Soul Fragment",
    "Ancient Skull",
    "Necro Dust",
    "Ghost Cloth",
    "Phantom Ring",
    "Spirit Orb",
    "Shadow Fang",
    "Rotting Heart",
    "Moon Charm",
    "Bone Key",
    "Cemetery Ash",
    "Dark Candle",
    "Crypt Coin",
    "Soul Shard",
    "Death Relic",
    "Haunted Feather",
    "Night Gem",
    "Ghostly Essence",
    "Phantom Mask",
    "Shadow Core",
    "Undead Totem",
    "Eternal Skull"
]

# ============================================================
# TOWERS
# ============================================================
TOWERS = {
    "mage": [
        "Medium", "Seer", "Conjurer", "Theurgist",
        "Thaumaturgist", "Magician", "Enchanter",
        "Warlock", "Sorcerer", "Necromancer",
        "Wizard", "Archmage"
    ],
    "cleric": [
        "Acolyte", "Adept", "Priestess", "Curate",
        "Vicar", "Elder", "Bishop",
        "Lama", "Patriarch", "Priest",
        "High Priest", "Hierophant"
    ],
    "druid": [
        "Aspirant", "Ovate", "Initiate of the 1st Circle", "Initiate of the 2nd Circle",
        "Initiate of the 3rd Circle", "Initiate of the 4th Circle", "Initiate of the 5th Circle",
        "Initiate of the 6th Circle", "Initiate of the 7th Circle", "Initiate of the 8th Circle",
        "Initiate of the 9th Circle", "Archdruid"
    ]
}

# ============================================================
# TOWER DROP ITEMS
# ============================================================

TOWER_DROP = [
    "Rusty Key", "Combat Wrench", "Worn Pickaxe", "Half-Eaten Rations", "Bottle of Cheap Ale",
     "Bundle of Wires", "Burned out Torch", "Sewing Needle", "Tattered Map", "Matches", "Small Bag of Copper Coins",
     "Uncut Sapphire", "Silver Locket (Empty)", "Glass Eye", "Golden Seed", "Ivory Comb", "Shiny Button",
     "Used Spell Scroll", "Red Hat", "Leather Gloves (Stained)", "Fine Clothes (Damaged)",
     "Amulet of Protection (broken)", "Broken Spectacles", "Iron Dagger", "Warrior Jar Shard"
]
# ============================================================
# OUTPUT ARRAYS
# ============================================================

holiday_items = []
holiday_monsters = []

horror_items = []
horror_monsters = []
horror_droplists = []

tower_items = []
tower_monsters = []
tower_droplists = []

# ============================================================
# HOLIDAY NPCS + ITEMS
# ============================================================

def create_holiday_content():

    for holiday, gifts in HOLIDAYS.items():

        # ====================================================
        # HOLIDAY NPC
        # ====================================================

        npc = {
            "id": f"npc_{holiday}",
            "name": holiday.replace("_", " ").title() + " Host",
            "iconID": MONSTER_ICON,
            "maxHP": 100,
            "attackChance": 5,
            "attackDamage": {
                "min": 1,
                "max": 2
            },
            "moveCost": 4,
            "attackCost": 4
        }

        holiday_monsters.append(npc)

        # ====================================================
        # HOLIDAY ITEMS
        # ====================================================

        for gift in gifts:

            item = {
                "id": f"item_{holiday}_{gift.lower().replace(' ', '_')}",
                "name": gift,
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "hasManualPrice": 1,
                "baseMarketCost": random.randint(50, 500),
                "category": "misc",
                "description": f"A special {holiday.replace('_', ' ')} gift item."
            }

            holiday_items.append(item)

# ============================================================
# HORROR MONSTERS + ITEMS + DROPS
# ============================================================

def create_horror_content():

    for location, monsters in LOCATIONS.items():

        for i in range(25):

            monster_name = (
                f"{random.choice(monsters)} "
                f"of the "
                f"{location.replace('_', ' ').title()}"
            )

            item_name = random.choice(DROP_ITEMS)

            item_id = f"item_{location}_{i+1}"

            droplist_id = f"droplist_{location}_{i+1}"

            # ====================================================
            # ITEM
            # ====================================================

            item = {
                "id": item_id,
                "name": item_name,
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "hasManualPrice": 1,
                "baseMarketCost": random.randint(100, 1200),
                "category": "misc",
                "description": (
                    f"A haunted relic recovered from a "
                    f"{location.replace('_', ' ')}."
                )
            }

            horror_items.append(item)

            # ====================================================
            # DROPLIST
            # ====================================================

            droplist = {
                "id": droplist_id,
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

            horror_droplists.append(droplist)

            # ====================================================
            # MONSTER
            # ====================================================

            low = random.randint(5, 25)
            high = low + random.randint(5, 30)

            monster = {
                "id": f"monster_{location}_{i+1}",
                "name": monster_name,
                "iconID": MONSTER_ICON,
                "maxHP": random.randint(60, 500),
                "attackChance": random.randint(45, 85),
                "attackDamage": {
                    "min": low,
                    "max": high
                },
                "moveCost": random.randint(3, 8),
                "attackCost": random.randint(3, 8),
                "droplistID": droplist_id
            }

            horror_monsters.append(monster)

# ============================================================
# TOWER MONSTERS + ITEMS + DROPS
# ============================================================

def create_tower_content():

    for location, monsters in TOWERS.items():

        for i in range(4):

            monster_name = (
                f"{random.choice(monsters)} "
                f"of the "
                f"{location.replace('_', ' ').title()}"
            )

            item_name = random.choice(TOWER_DROP)

            item_id = f"item_{location}_{i+1}"

            droplist_id = f"droplist_{location}_{i+1}"

            # ====================================================
            # ITEM
            # ====================================================

            item = {
                "id": item_id,
                "name": item_name,
                "iconID": ITEM_ICON,
                "displaytype": "ordinary",
                "hasManualPrice": 1,
                "baseMarketCost": random.randint(100, 1200),
                "category": "misc",
                "description": (
                    f"A relic recovered from a "
                    f"{location.replace('_', ' ')} Tower."
                )
            }

            tower_items.append(item)

            # ====================================================
            # DROPLIST
            # ====================================================

            droplist = {
                "id": droplist_id,
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

            tower_droplists.append(droplist)

            # ====================================================
            # MONSTER
            # ====================================================

            low = random.randint(5, 25)
            high = low + random.randint(5, 30)

            monster = {
                "id": f"monster_{location}_{i+1}",
                "name": monster_name,
                "iconID": MONSTER_ICON,
                "maxHP": random.randint(60, 500),
                "attackChance": random.randint(45, 85),
                "attackDamage": {
                    "min": low,
                    "max": high
                },
                "moveCost": random.randint(3, 8),
                "attackCost": random.randint(3, 8),
                "droplistID": droplist_id
            }

            tower_monsters.append(monster)

# ============================================================
# GENERATE EVERYTHING
# ============================================================

create_holiday_content()
create_horror_content()
create_tower_content()

# ============================================================
# WRITE JSON
# ============================================================

def write_json(path, data):

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ============================================================
# WRITE FILES
# ============================================================

with open(
    os.path.join(OUTPUT_RAW, "itemlist_holiday.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(holiday_items, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "monsterlist_holiday.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(holiday_monsters, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "itemlist_horror.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(horror_items, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "monsterlist_horror.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(horror_monsters, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "droplists_horror.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(horror_droplists, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "itemlist_tower.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(tower_items, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "monsterlist_tower.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(tower_monsters, f, indent=4)

with open(
    os.path.join(OUTPUT_RAW, "droplists_tower.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(tower_droplists, f, indent=4)

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
print(" Holiday + Horror Resources Generated")
print("===================================================")
print(f"Holiday Items: {len(holiday_items)}")
print(f"Holiday NPCs: {len(holiday_monsters)}")
print(f"Horror Items: {len(horror_items)}")
print(f"Horror Monsters: {len(horror_monsters)}")
print(f"Horror Droplists: {len(horror_droplists)}")
print(f"Tower Items: {len(tower_items)}")
print(f"Tower Monsters: {len(tower_monsters)}")
print(f"Tower Droplists: {len(tower_droplists)}")
print("===================================================")
print("./raw/itemlist_holiday.json")
print("./raw/monsterlist_holiday.json")
print("./raw/itemlist_horror.json")
print("./raw/monsterlist_horror.json")
print("./raw/droplists_horror.json")
print("./raw/itemlist_tower.json")
print("./raw/monsterlist_tower.json")
print("./raw/droplists_tower.json")
print("===================================================")
