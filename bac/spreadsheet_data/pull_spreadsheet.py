import json
import math
import random
import sqlite3
import time
import textwrap
from collections import Counter, defaultdict

import gspread
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import logging
logging.getLogger().setLevel(logging.INFO)

import os

# image function for preloading images
image_cache = {}


# BACAP Bot Reloaded
# emotes = {
#
# }

################### ACTUAL BACAP BOT STUFF #######################

advs = []
adv_index = {}

def find_children():
    # Cycle through every advancement (child)
    for i, advancement in enumerate(advs):
        child_name = advancement["Advancement Name"]

        try:
            # Safeguard: Initialize parent_name with a default value
            parent_name = advancement.get("Parent", "")

            # Skip if the parent_name is empty
            if not parent_name:
                continue

            # Find the ID of the parent and assign it the child's name
            parent_id = adv_index[parent_name.upper()]

            if advs[parent_id]["Children"] != "":
                advs[parent_id]["Children"] = advs[parent_id]["Children"] + ", " + child_name
            else:
                advs[parent_id]["Children"] = child_name

        except Exception as e:
            logging.warning(f"WARNING: Advancement {parent_name} NOT FOUND!")
            logging.warning(e)

    # for a in advs:
    #     children = a["Children"]
    #     if "and" in children:
    #         print(a["Advancement Name"], children.count("and") + 1, children)

# GET COLOR FROM CELLS
def get_category_from_color_or_so_help_me_god(rgb):
    colors = {
        (243, 243, 243): "root",
        (147, 196, 125): "task",
        (109, 158, 235): "goal",
        (194, 123, 160): "challenge",
        (224, 102, 102): "super_challenge",
        (213, 166, 189): "hidden",
        (255, 217, 102): "milestone",
        (246, 178, 107): "advancement_legend",
    }
    if rgb not in colors:
        logging.warning(f"Color combination {rgb} not found in color dictionary.")

    return colors.get(rgb, "task")

def get_cell_color(background_color):
    red = round(background_color.get("red", 1) * 255, 0)
    green = round(background_color.get("green", 1) * 255, 0)
    blue = round(background_color.get("blue", 1) * 255, 0)
    return (red, green, blue)

def assign_cell_colors(sheet_key):
    try:
        # Authenticate with Google Sheets API
        creds = Credentials.from_service_account_file("Text/google_auth.json")
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        logging.info("Starting to assign cell colors to advancements.")

        # Group advancements by their worksheet
        advancements_by_worksheet = {}
        for adv in advs:
            worksheet_title = adv["adv_tab"]
            if worksheet_title not in advancements_by_worksheet:
                advancements_by_worksheet[worksheet_title] = []
            advancements_by_worksheet[worksheet_title].append(adv)

        # Process each worksheet
        for worksheet_title, worksheet_advs in advancements_by_worksheet.items():
            logging.info(f"Processing worksheet: {worksheet_title}")

            # Fetch cell formatting data for column A
            range_name = f"'{worksheet_title}'!A2:A"
            formatting = sheet.get(
                spreadsheetId=sheet_key,
                ranges=range_name,
                fields="sheets(data(rowData(values(effectiveFormat(backgroundColor)))))"
            ).execute()

            # Extract row data
            row_data = formatting["sheets"][0]["data"][0].get("rowData", [])
            row_colors = []

            for row in row_data:
                background_color = row.get("values", [{}])[0].get("effectiveFormat", {}).get("backgroundColor", {})
                cell_color = get_cell_color(background_color)
                row_colors.append(cell_color)

            # Assign colors to advancements
            for i, adv in enumerate(worksheet_advs):
                if i < len(row_colors):

                    index = adv_index[adv['Advancement Name'].upper()]
                    advs[index]['Category'] = get_category_from_color_or_so_help_me_god(row_colors[i])


                    # logging.info(f"Assigned color {row_colors[i]} to advancement '{adv['Advancement Name']}'")
                else:
                    adv["Cell Color"] = None
                    logging.warning(f"No color data found for advancement '{adv['Advancement Name']}' in worksheet '{worksheet_title}'")
            # print(worksheet_advs)

        logging.info("Finished assigning cell colors to advancements.")

    except Exception as e:
        logging.error(f"An error occurred while assigning cell colors: {e}")

# open sheet if possible
def access_sheet(sheet_key):
    global advs
    global adv_index
    global sorted_adv_names
    global additional_adv_info
    advs = []
    adv_index = {}
    sorted_adv_names = []
    additional_adv_info = {}

    # Open sheet and extract all advancements
    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(sheet_key)
        logging.info(f"THIS MESSAGE IS TO INDICATE {sheet} WAS OPENED SUCCESSFULLY")


        for worksheet in sheet.worksheets():
            if worksheet.title == "Introduction" or worksheet.title == "Terralith":
                continue
            records = worksheet.get_all_records(head=1)
            logging.info(f"Fetched {len(records)} records from sheet: {worksheet.title}")

            grab_more_info = False

            # Iterate through advancements
            for row in records:

                # In "Additional Info Mode" append any new descriptions as "Additional Info" to the respective adv
                if grab_more_info == True:

                    if row['Advancement Name'] == "Full requirement notes:" or row['Advancement Name'] == "":
                        continue

                    if row['Advancement Name'] == "Riddle Me This":
                        additional_adv_info[row['Advancement Name']] = "Run /riddlemethis for more information."
                        continue

                    adv_note_names = row['Advancement Name'].split("\n")
                    for name in adv_note_names:
                        additional_adv_info[name] = row['Description'].replace("\n", "")

                    continue

                # After the bulk advancements are done, set info gathering mode to "Additional Info"
                if any(row.values()) == False:
                    grab_more_info = True
                    continue

                # The loop will only get down here if it's reading a valid advancement (due to continues)
                row["adv_tab"] = worksheet.title

                # Add each advancement row into the advs list
                advs.append(row)
            logging.info(f"Fetched {len(advs)} advancements from {sheet.title}")

        for i, adv in enumerate(advs):
            name = adv["Advancement Name"]

            if name == "" or name == "(description)":
                continue

            # Set to empty string
            adv['Children'] = ""

            adv_index[name.upper()] = i
            sorted_adv_names.append(name)

        find_children()
        # print(additional_adv_info)
        # Assign cell colors to advancements

        # Get backgrounds
        assign_cell_colors(sheet_key)

    except Exception as e:
        logging.error(f"\nWHILE LOADING SPREADSHEET {sheet}, AN ERROR OCCURED :sadcave:\n{e}")

# open trophy sheet if possible
def access_trophy_sheet(trophy_sheet_key):
    global trophy_data
    global trophy_index
    trophy_data = []
    trophy_index = {}

    try:
        gc = gspread.service_account(filename="Text/google_auth.json")
        sheet = gc.open_by_key(trophy_sheet_key)
        logging.info(f"THIS MESSAGE IS TO INDICATE {sheet} WAS OPENED SUCCESSFULLY")

        for worksheet in sheet.worksheets():
            records = worksheet.get_all_records(head=1)
            logging.info(f"Fetched {len(records)} records from sheet: {worksheet.title}")

            # Truncate tab (not necessary)
            for trophy in records:
                trophy.pop('Tab')

            for row in records:
                if row['Trophy Name'] != '':
                    trophy_data.append(row)

            for idx, trophy in enumerate(trophy_data):
                trophy_index[trophy['Advancement']] = idx

        logging.info(f"Fetched {len(trophy_data)} sections of trophies from the sheet.")
        # print(f"Trophy Indexes: {trophy_index}")
    except Exception as e:
        logging.error(f"\nWHILE LOADING SPREADSHEET {sheet}, AN ERROR OCCURED :sadcave:\n{e}")

def read_datapack():
    adv_directories = ["./packs/BlazeandCaves Advancements Pack 1.20/data/blazeandcave/advancement",
                       "./packs/BlazeandCaves Advancements Pack 1.20/data/minecraft/advancement"]
    adv_paths = []
    adv_namespace = []
    print(adv_index)
    for directory in adv_directories:
        for root, dirs, files in os.walk(directory, topdown=True):
            for file in files:
                adv_path = os.path.join(root, file).replace('\\', '/')
                if '/'.join(adv_path.split('/')[-4:]) not in adv_namespace:
                    adv_paths.append(adv_path)
                    adv_namespace.append('/'.join(adv_path.split('/')[-4:]))

    adv_paths = [adv for adv in adv_paths if '/technical' not in adv]

    # lang_url = 'https://raw.githubusercontent.com/misode/mcmeta/refs/heads/assets/assets/minecraft/lang/en_us.json'
    # response = requests.get(lang_url)
    # lang = response.json()

    o = open("Text/out.txt", "w+")
    for adv_path in adv_paths:
        with open(adv_path, encoding='utf-8') as adv_file:
            adv = json.load(adv_file)

            try:
                title = adv["display"]["title"]["translate"]

                if "extra" in adv["display"]["description"].keys() and "view progress" not in str(adv["display"]["description"]) and "The following are" not in str(adv["display"]["description"]):
                    print(adv["display"]["description"])

                if "extra" in adv["display"]["title"].keys() and title != "Riddle Me This":
                    # print(adv["display"]["title"])
                    for extra in adv["display"]["title"]["extra"]:
                        title += extra["translate" if "translate" in extra.keys() else "text"]
                if title == "Feeding the §mDucks§r Chickens":
                    title = "Feeding the Ducks Chickens"

                if title.upper() not in adv_index:
                    print(f"Bad title: {title}")
                else:
                    advs[adv_index[title.upper()]]["Icon"] = adv["display"]["icon"]["id"].replace("minecraft:", "")
                    if "components" in adv["display"]["icon"]:
                        if "minecraft:enchantment_glint_override" in adv["display"]["icon"]["components"]:
                            advs[adv_index[title.upper()]]["Enchanted"] = True
                        else:
                            advs[adv_index[title.upper()]]["Enchanted"] = False

                    if "requirements" in adv:
                        # if len(adv["requirements"]) != len(adv["criteria"]):
                        #     print(title, len(adv["requirements"]), len(adv["criteria"]))
                        advs[adv_index[title.upper()]]["Criteria Count"] = len(adv["requirements"])
                    else:
                        advs[adv_index[title.upper()]]["Criteria Count"] = len(adv["criteria"])


                    # o.write(f"====={title} ({str(len(adv["criteria"]))})=====\n")
                    # for c in adv["criteria"]:
                    #     o.write(f"{c}    {str(adv["criteria"][c])}")
                    #     o.write("\n")
                    # o.write("\n")

            except Exception as e:
                print(f"Error parsing {adv_path} with error {e}")
                continue



    # print(adv_namespace)

# CONFIG
READ_SHEET = False
READ_DATAPACK = False
SET_DATABASE = False

if READ_SHEET:
    trophy_sheet_key = "1yGppfv2T5KPtFWzNq25RjlLyerbe-OjY_jnT04ON9iI"
    access_trophy_sheet(trophy_sheet_key)

    sheet_key = "1_DwKEZ0vqCOp2POhiOVSoMVeVNpU1WNPzk0L8qR_y2s"
    access_sheet(sheet_key)
    with open("raw_output.txt", "w+", encoding="utf-8") as out:
        json.dump(advs, out)
    with open("readable_output.txt", "w+", encoding="utf-8") as out:
        json.dump(advs, out, indent=3)
else:
    # print("unused for now")
    data = open("raw_output.txt", "r+").read()
    advs = json.loads(data)
    # build adv indices
    for i, adv in enumerate(advs):
        adv_index[adv['Advancement Name'].upper()] = i


if READ_DATAPACK:
    read_datapack()
# print(advs)

# for adv in advs:
#     name = "".join([c if c in "abcdefghijklmnopqrstuvwxyz0123456789_" else "" for c in adv['Advancement Name'].replace(" ", "_").lower()])
#     print(name)


# Connect to SQLite database (will create if not exists)
conn = sqlite3.connect('bacap.db')
cursor = conn.cursor()

if SET_DATABASE:



    # Create table (adjust schema as needed)
    cursor.execute('''DROP TABLE IF EXISTS advancements''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS advancements (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            icon TEXT,
            adv_tab TEXT,
            category TEXT,
            criteria_count INTEGER,
            actual_req TEXT,
            item_reward TEXT,
            xp_reward INTEGER,
            hidden TEXT,
            trophy TEXT,
            parent TEXT,
            children TEXT,
            source TEXT,
            version TEXT,
            notes TEXT
        )
    ''')

    # Insert each record from the JSON data
    for entry in advs:
        cursor.execute('''
            INSERT INTO advancements (
                name, description, icon, adv_tab, category, criteria_count,
                actual_req, item_reward, xp_reward, hidden,
                trophy, parent, children, source,
                version, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.get("Advancement Name"),
            entry.get("Description"),
            entry.get("Icon"),
            entry.get("adv_tab"),
            entry.get("Category"),
            entry.get("Criteria Count"),
            entry.get("Actual Requirements (if different)"),
            entry.get("Item rewards"),
            entry.get("XP Rewards"),
            entry.get("Hidden?"),
            entry.get("Trophy"),
            entry.get("Parent"),
            entry.get("Children"),
            entry.get("Source"),
            str(entry.get("Version added")),  # Cast to string in case of floats
            entry.get("Notes")
        ))

    conn.commit()
database_data = cursor.execute('''SELECT name from advancements ''')
# database_data = cursor.execute('''SELECT name from advancements WHERE version like '%1.20%' OR version like '%1.19%' OR version like '%1.18%' OR version like '%1.17%' OR version like '%1.16%' ''')
d = database_data.fetchall()
advs = [adv[0] for adv in d]

for l in advs:
    print(l)

ladvs = ["".join([c.upper() for c in adv if c.lower() in "abcdefghijklmnopqrstuvwxyz0123456789"]) for adv in advs]

arr = [a for a in ladvs if len(a) == 8]
print(arr)
print(len(arr))

# Add addons or trophies to word list
# advs += "Hardcore Advancement Legend, Terralith Advancement Legend, Alpha Slab, Happy 10 years Minecraft, Cereal Dedication, Alpha Collection, A Complete Collection!, Illegal Collection, Imperfect Mirror, Triple Trouble, Advancement Info, Copper Armor, Din-Don, Do You See This?, Dual Reality, Emerald Armor?, Eye Contact Master, Fake Netherite Armor, General Cleaning, Herbalist's Dream, I Hate All of You, Jurassic Park, Komaru ♥, Midnight Snack, My Personal Slave, Nobody Needs Rockets!, Not Profitable Transportation, No-Water Team, Oh You Again?, Ominous Ocean, On Site Sale, On the Wings of the Wind, Placeholder, Pottery Collector, Real Immortal, Real Netherite Armor, Restoring Population, Save Me!, Silent Armor, Supply Chain, Suspicious Miner, Sus Miner, That's a New Style, The Beginning of the Day, The Cult of the Spyglass, The Hardest and Unfairest One Yet, Thorny Prices, Uncontrolled Reproduction, Wandering Caravane, Warden's Thrust, Water-Dependent, Water Team, We Are Fine Really, Accept Cookies, Air Balloon, An Ewe for Every Hue, Baby Zoo, Beezlebooster, Blind Friend, Buff Axolotl, Camel Adventure, Cheers!, Crab Should've Won, Desert Warrior, Dinner Time, Driven to Death, Echoing Call, Extraordinary Duel, Fox Poses, Full Catch, Furry Fury, Horse Health Hunter, Horse to Honse, Hot!, I Love Salmons, Live Salmon, More Colorful Wool!, Ok I Pull Up, One More Frog!, Pie-Fox Fest, Poisoned Ball, Scared Box, Skill Issue, SnifferSniffEvent, TeleFoxing, The Fox's Banquet, The Invisible Turtle, The Sugar Cane Diet, The Wool Magnate, Turtle Bowl, What's the Best Transport?, What About Mooblooms?, What Are You Doing in My Swamp, What a Mess This Horse Is!, You're Bald, You're Part of a Hive Mind Now, Enh. Adventure Milestone, Enh. Animal Milestone, Enh. Biomes Milestone, Enh. Building Milestone, Enh. Super Challenges Milestone, Enh. Enchanting Milestone, Enh. End Milestone, Enh. Farming Milestone, Enhanced Legend, Enh. Mining Milestone, Enh. Monsters Milestone, Enh. Nether Milestone, Enh. Potions Milestone, Enh. Redstone Milestone, Enh. Statistics Milestone, Enh. Weaponry Milestone, Australia, CoolGrill, Good Dreams!, Hydrodynamic, Ice Sculptor, Icy Pirates, Lost Ruin, My Mountains, Pandas Express, Ready for Everything, Stop There You're Tall Enough, The Boatman, The Infernal Cauldron, Treasure Compass, Underwater Pirates, Unite Storm, Artificial Forest, Art Lover, Bee Design, Chromatic Completion, Potception, Pot on a Pot, Smoke Signal, Statue, Stickman, 5G Connectivity, Five Birds One Stone, Airborne Annihilator, Astronomer, Baron Munchausen, Big End Adventure, Big Horse Adventure, Big Pig Adventure, Celestial Protocol, Circus Act, Command Work, Compass Overload, Dead Carnival, Definitely Not Raid Farming, Dragon vs Warden VI, Dragon vs Wither IV, End of the World as We Know It, Explosive Elixir, Extinction, From the Underworld, Happy Anniversary, Happy Minecraft Year, How Did You End Up Here, Interspecific Adventure, Magic Kingdom, Mob Universe, Monstrous Rocket, Mounted Menace, My Little Pig, No Shield Please, Oh My Broken Legs, One in a Million Steed, Piggish Poison Tango, Pooch Purge Pilot, Professional Assassin, Pulse Detonation Engine, Pyrotechnic vs Dragon V, Raise the Stakes, Red + Red = Brown, Riddle Me That, Sandwich, Shield of Achilles, Shopaholic, Show the Nether to a Silverfish, Silence Is Loud Here, So Bright, Star Fisherman, The Apocalyptic Decalogy, The King of the Redskins, The World Is Actually Ending 2, Thousand Lives, Void Being, What Are the Chances, What a Stupid Purchase, Wither Aboard!, Yes, Zero Coordinates Magnet, All the Netherite Tools, Elementals, Fully Charged, Heavy Catch, Master Shearer, Master Shieldman, Master Sweeper, Oh I Forgot About the Anvil, Pyromaniac, Small Targets, Thin Line, Useless, Bee Colonist, Compact Base, Dragon Blitz, Endergardener, End at the Start of the Game, Interdimensional Travel, Intergalactic Journey, Last Hit, Speed of Light, The Lockbox, The V O I D, Universal Solitude, Apple Addiction, Auto Cactus, Christmas Spirit, Cookie Eater, Delicious, Eco Warrior, Golems, High Risk, It's Midnight Already!?, More More Cookies!, Not Fireflies, Overpayment, Plant Enthusiast, Preventive Conversation, Raising Canes, Bat-Man, Chief Spide, Complete Orellection, Copper King, Deepslated Miner, Deepslate Master, Distorted Cave Maze, Flint and Steal, Light at the End of the Tunnel, Pointy Problems, Redstoner, Reinforced Miner, The Master of Falls, Time Killer, Arachnophobia, Born to Spawn, Frozen Heart, Get Out of My Sky, High Explosives, I Uh... Forgot a Composter, Live Cactus, More Impossible, Not That Impossible, One Minute Warden's Hugs, Phantom Rider, Spider's Lair, Suspicious Duel, The Inquisition, The Undertaker's Revenge, A Long Journey, Bastion Robber, Bastion Sweet Bastion, Beyond the Rings, Blaze3D, Diamond Beacon, Emerald Beacon, Firefox, Flap Don't Fall, Ghast Squad, Give Them Everything They Want, Gold Beacon, Herbarium to My Friend, High Pitch, Hot Combat, Hot Lake, Impostor, Inside Out, Iron Beacon, Netherite Beacon!, Never Careful Enough, Rainbow!, Show the Wither His Home, The Last Deal, The New Swamp Won't Be Here, Withering Depths, Armor in a Bottle, Cowabunga It Is, Flashlight, Healed by Pain, Jump for Joy, Master of Effects, Trial Potions, Worst Cleric in the World, You're Not the Zillager, Crafting Lockdown, Craft Me ALL!, Farm Basics, Fat Cat, Heavy Steps, Light Touch, More Optimisations!, Night Shift, Old Optimisations, Say NO to Campfires, Using a Bow a Bow a Bow a Bow, What Do You Know About Pistons, Absolutely Ablaze Journey, Ancient Sorcerer Sage, Artisan Adept, Ascension Ace, Bedrock Breaker, Chests Aficionado, Chest Lover, Climb Expert, Craftsman Novice, Culinary Delight Maestro, Diamond Digger, Duo Dynamo, Epic Capital Conqueror, Eternal Vanguard, Experienced Angler, Ghastonaut, Happy 1000 Days!, Happy Chest Year!, Intercontinental Rail Nexus, Intermediate Fisher, Jetsetter of the Skies, Jungle Gymnast, Ladder Legend, Legendary Artisan, Legend of the Races, Ligmifitation, Master Artificer, Master Fisherman, Master of Survival, Metal Miner, Mr. Chester, My Chest!, Navigator of the Infinite Waters, Novice Angler, Novice Scout, Pillager Protector, Raid Resister, Ravager Repeller, Resilient Centenarian, Shulker Explorer, Shulker Maestro, Shulker Seeker, Shulker Voyager, Skyward Legs, Sovereign of Martial Shifting, Speed Master, Stone Cutter, Storm Hog Pilgrim, Survival Saga, Survivor's Hour, Swift Herder, Titan of Olympian Gold Triumphs, Totem Adept, Totem Expert, Totem Immortal, Totem Tinkerer, Vindicator Vanquisher, Wrath of the Western Frontier, Your Legs Are Beat, Air Battle, Cold Betrayal, Dead-Eye, Deflector, Explosive Fisherman, Frightening Fishing, Glowball, Meet the Snipe, More Shields!, Snow Fights!, Surface-to-Air Missile, The Explosive Adventure, Unlucky, Wind Burst Fox, A.N.F.O., Back From Whence You Came, Phosphorescence, Pseudo Zone, Subterranean Animism, Return of the Piglins, The Art of War, Will you ever rest?, The Conqueror, Duel of the Fates, In the Hall of the Piglin King, The Dust Settles, Border of Life, Light-Sensitive, Darude - Firestorm, Forged In Flames, Fallen to Ashes, Lunatic Mode, Beyond the Embers, Risen from Fire, Ceci n'est pas un blaze, Plumber's Plunder, Pipe Dream, Piglin Pillage, Alchemical Experiments, Soul Searcher, Feed the Beast, The Floor is Tears, Ghast Buster, Rescue Mission, Hellish Paradise, An Illager Refuge?, Subterranean Animism, Kitchen's Treasure, Hell's Kitchen, Mystic Wisdom, Pocket Edition Alpha, Radioactive, Toxic Personality, Hellfire Mantle, Chained Spirits, Apparitions, Ancient Battlefield, Adrenaline Rush, Advancement Legend, Any%, An Exaltedly Resplendent Quartet, An Ineffably Sublime Trio, Arsonist, A Transcendently Superb Duo, Behold the Malgosha's Army, Behold the Malgosha's Army, Biome Rush, Blazeandcave, Boss Rush idk, CaseOh's Unbalanced Diet, Charge Off!, A Complete Collection!, Extinguished, Get to the Tardis, Ghost in the Graveyard, Highway to Heaven, Horrible Accident, I'm More Perfect!, It's Over 9000, I've seen this somewhere..., I should riddle you a job, King's Mace, Lumber Legend, Making the Pack Harder, Master Miner, Ocean of Blood, Plantsman, Potato, Return the music, Riddle Me Azure Bluet, Riddle Me Azure Bluet: A Sequel, Riddle Me Not, Riddle Me Twice, Shiny Kingdom, Suggestion Advancement Legend, The bee movie abridged, The Black Pearl, The Blue Marble, This is Tough, This Won't be a Breeze, Thrift Master, Turn My World Upside-Down, Wandering Caravan, When Hogs Fly, Working Overtime, Wow this is pretty cool, You're Not Getting This One, You and What Army?, A Journey Begins, Castle of Hrrms, Expedition of Discovery, Remote Shelter, Spire of Ice, Totally Not Terraria, Under the Ice, A E S T H E T I C, Alpha Days, A Cliffhanger!, A Grassy Nature, Bushranger, Choco Mountain, Eruption in the Air, Highlander, Land of Icicles, Master Spelunker, One Small Steppe For Man, Over the Moon, O-Land-o Bloom, Pretty in Purple, Skylanders, Smarter than the Average Bear, Terralithic, The Boreal Deal, The World Is Your Canvas, You are already Dead, Happy 10 Years Minecraft, What do you even need this for, 223380 Dragons worth of Exp, Hello from 2059, ( ͡o ͜ʖ ͡o),  , ( ͡O ͜ʖ ͡O), ( ͡° ͜ʖ ͡°), Food is Love Food is Life, I'm gonna explode, I'm not Fat you're Fat., Very Elderly Enchanter, Dead Enchanter, Eternal Enchanter, Fishing Fun, Fisher Addict, Fisherman, Best Mechanic in the Game, Go watch a Movie, Get some Help, A     Are you a Plane?, Are you a Bird?, You're a Birdplane., No Tears left to Happ', Happy it's done, Happy Stroll, Is it a Skeleton Horse yet?, Constable Clomper, YEEEEEE-HAAAAAW, Trampolout, Trampoline, Trampoline in your Step, Rock or let roll, Burn or save your Soul, Live or let die, RAGE QUIT, 10 Leaves, 1 Stack + 36, 15 Stacks + 40, 5 Shulkers + 21 Stacks + 16, 2 Shulkers + 24 Stacks + 8, Still no Notch Apples :(, 100GB World, He's a Pirate, 500km in a Minecart, 5000km in a Minecart, 50000km in a Minecart, Riding Something gives off Heat, And eventually it'll turn to Ashes, It'll die if you ride it too much, Ding Ding Ding!, Stuck in my Head, Can't stop hearing it, Are your Ears bleeding yet?, CAN'T GET IT OUT, It's all I hear, Captain Barbossa, Captain Coldbeard, Captain Jack Sparrow, I'm Invisibler, I'm Invisiblest, I'm Invisible, Fitness Gram Pacer Test, Stop it get some help, Sonic Speed!, Get Macro Time here, Master AFKer, Stride Time, §lYou are the Fish, It can all fit in this Bucket, And now without getting Air, I'm still standing, Why are you so Bad at this, I hope you've built a Raid Farm, Hardcore Player, Skill Issue!, You are the Evoker now, MEGA STONKS!, UBER STONKS!, ULTRA STONKS!, The Grindy Super Challenges Tab, The Statistics Tab SHALL be, Spin Cycle, Electrolux-EFLS627U, Washing is Faster than refilling, Washing Machine, Got me spinning like a Ballerina, You know what makes no Sense?, 2b2t Player, 5 Birds 1 Stone, 8bit Wither, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA, Actual Immortal, Actual Tropical Collection, Al Gore's Redemption, An Apple a Year, Armory of the Ages, Arrows are off, Ascended Dedication, A Complete Collection, A Poison a Day, A Tropical Meal, Bacon Punch, Baterang Duel, Because I'm Batman, Big Nose Close-up, Care for Wardens, Celestial Protocol, Yes, Barried Alive, The Ritual continues, https://www.chunkbase.com, Dispensers are Stackable Bows, The End of City looting, Mountain Miner, Have Fun lol, Build a Rabbit Farm, What did it cost? 8 years., Communism, Complete Waste, Consistency, Corner Camping, Cursed Enchanter, Death from all 2.0, Does this belong to you?, Double Nose, Dragon Destroyer, Endermite Ender, End Limit, Even Future Entities, Even the Children too, EXTINCTION, Extinction of the Villagers, Farm Destroyer, Fasty Flappy, Florida Man, Get out of my Sky, Gluttonous, GMHorse, Gotta feed them all!, Guardian of the Peace, Halloween Massacre, Handsome JackS, Hardcore Hell, Hardcore Hell 2.0, Headception, How did we get here 2.0, Hyper Insomniac, Impossible... 2.0..., I'm a Pigman, I'm still Hungry, I love Brownies, Jockeys Down, Jockey Exterminator, Just kidding, Legend of Hell Rider, Legolas, Like an Enderman, Llama Farrier, Locked Position, Macro Time, Master Assassin, Master Comparator, Master Villager, Mr. Worldwide, Must... Find... Land...!, Nether Limit, Nice View, Nose Wars, Not Spawn Camping, No Friends, Overworld Limit, Pain in the Grass, Pegasus, Permanent Destruction, Phineas and Fern, Pig Ben, Pixel Perfecter, Pixel Perfectest, Puffer Poppers, Revaulting Destruction, Riddle me this 2.0, Right Click Master, Salad Slurper, Get an Iron Farm... or 50, Silverfish Hater, Unlucky Break, Splat, :startrekkin:, Starvin' Marvin, Statistics Legend, Statistics Mad Lad, Storage Upgrade Required, Suffer, Suffer 2.0, Superduperoverpowered, Super Insomniac, Suspicious Milk, Take Everything, There has to be another Way 2.0, The Great Flood, The Talkative Pack, The World is actually ending, This one's Free, This one definitely isn't Free, This one isn't as Free, This one isn't Free, Tools Reunion, Torture Legend, Torture Mad Lad, Training Session, Trial Destruction, vAccINaTIon bAd, Void Being, Waiting is Fun, Wandered and Traded, We were Bad but now we're Good, What are the Requirements?, Where are the Farlands?, You're the Nitwit now, You Monster, You want some more?".split(",")
# advs += "Miner's Trophy,Builder's Trophy,Farmer's Trophy,Butcher's Trophy,Slayer's Trophy,Sword Trophy,Explorer's Trophy,Adventurer's Trophy,Mechanic's Trophy,Enchanter's Trophy,Statistician's Trophy,Nether Adventurer's Trophy,Potion Brewer's Trophy,End Adventurer's Trophy,Challenger's Trophy,Yellow T-Shirt,,Azalea Parachute,Octuple Compressed Cobblestone,Golden Cobblestone,Steve's Head,Pyro's Mask,Spoon,Underpants,Santa's Present,Golem Kit,Copper Golem,Weathered Copper BlocK,Green Lantern Ring,M.A.R.I.L.L.A.,Copper Shortsword,Piñata,Baseball Bat,Energy Crystal,Golden Crown,Bean Block,Mayor's Throne,Chaos Emerald,Deepslate Emerald Ore,,Claptrap,Flex Tape,Stairway to Heaven,Logolas,Ch-ch-ch-ch-ch-ch-Cherry bomb!,Birthday Cake,Pickle Rick,Torch God's Favor,The Journal,Magic Wand,Magic Paintbrush,Sleepless Anchor,Silver Armor Stand,Very Muddy Boots,,Serenity,A Glutton's Meal,Mega Spud,Annoying Orange,Wilson,Mr Finch's Hoe,Compost Mate,Farmer's Badge,,Armored Paws,Black Bird,Cowboy Hat,Earth,Pride Rock,Fake Tropical Fish,Super Rod,Potato Mine,Llama Drama,Matryoshka Doll,Barry B. Benson's Hive,Toilet,Ice Wand,Copper Goat Horn,FrogChamp,,Mobestiary,Lava Chicken,Vanilla Ice Cream,Molten Ice Cream,Hyperlink,Handsome Pumpkin,Pink Camo Pants,The Walking Head,Sans's Head,Ender Arrow,Basketblock,Etho's Anvil,Warden Head,The Warden's Sign,Nokia 3310,,Boomer T-Shirt,The Hylian Shield,1000-degree knife,Sculk Meteorite,Multiweapon,Really Really Pointy Arrow,Reuben the Wither Storm Ender,,Voyager 1,A blessing in love,Bouquet,,Hot Potato,Captain America's Shield,Bamboo Sword (Sharpness I),The Jungle Book,Waterbed,,Dinnerbone's Head,Jeb's Head,Crown of the Potato King,Medal of Honor,The Salad Bowl,Body Pillow,Ominous Shield,The Moon,Stonk Man's Head,Fogg's Pocket Watch,Your Cat's Prize,Eridium,Klefki,Uru,The Trophy Trophy,Golden Idol,Tron Suit,Vent,Iron Man Suit,,Spongebob Squarepants,,Quiver,Harp String,The Midnight - Monsters,Roller Coaster Cart,,Mobbo,The Cataclyst,,Steam Engine,,Finger Guns,1-UP Life,One-Punch Man's Fist,Fence Post,Fart in a Jar,Tinfoil Mining Helmet,,Strider Treat,M.O.A.B.,Enchanter's Tome,World's Most Reliable Shoes,Time Machine,Portable Trampoline,Noah's Ark,Zero Tick Farm,God Particle,Mammoth Steak,Black Pearl,Big Pointy Arrow,Superman's Cape,Flowey the Flower,Firearm's Firearm,Mimic,Refreshment,Gold Medal,New Year's Firework,Piston Cup,Thomas the Tank Engine,Black Belt,,Farmer's Badge V2,Brick Astley,Ultimate Flex,Plaid Block,Wormhole,Spinny Top,Mini Ghast,Stormbreaker,Baconator,Gilded Blade,Zork Chop,,Unknown Mixture,Fast and Furious,This is Anarchy,Stink Bomb,,TARS,Wizard's Fruit,Calendar,Portal Bow,Moon Rock,Ring of Bedrock,Singularity,Amalgamation,,Cosmonaut Helmet,Astronaut Helmet,Dragon Bro,Power Stone,Shiny Netherite Grade Ender Dragon Mob Trophy,Mario's Hat,Golden Advancement Plaque,Heart of a Siren,Amphitrite,Devil's Pitchfork,Space Stone,Reality Stone,Eye of the Apocalypse,Viceroy Nute Gunray,Notch's Head,Wishing Star,Corrupted Beacon,Treasure Chest,Frame of Infinite Items,Pandora's Box,Doraemon's Pocket,Nuclear Reactor,Mind Stone,Soul Stone,Cursed Creeper Head,Poglin,Hubble Space Telescope,ACDC - Back in Black,Endfinity Source,Potion Master's Diploma,Poison Mask,Infinity Gauntlet,Totem of Immortality,Time Stone,Instant Death,Stale Milk,Groot's Stick,Master Enchanter's Book,Cartographer's Quill,Wall Street,Stone of the Farlands".split(",")
# advs += "Miner's Trophy,Builder's Trophy,Farmer's Trophy,Butcher's Trophy,Slayer's Trophy,Sword Trophy,Explorer's Trophy,Adventurer's Trophy,Mechanic's Trophy,Enchanter's Trophy,Statistician's Trophy,Nether Adventurer's Trophy,Potion Brewer's Trophy,End Adventurer's Trophy,Challenger's Trophy,Yellow T-Shirt,,Azalea Parachute,Octuple Compressed Cobblestone,Golden Cobblestone,Steve's Head,Pyro's Mask,Spoon,Underpants,Santa's Present,Golem Kit,Copper Golem,Weathered Copper BlocK,Green Lantern Ring,M.A.R.I.L.L.A.,Copper Shortsword,Piñata,Baseball Bat,Energy Crystal,Golden Crown,Bean Block,Mayor's Throne,Chaos Emerald,Deepslate Emerald Ore,,Claptrap,Flex Tape,Stairway to Heaven,Logolas,Ch-ch-ch-ch-ch-ch-Cherry bomb!,Birthday Cake,Pickle Rick,Torch God's Favor,The Journal,Magic Wand,Magic Paintbrush,Sleepless Anchor,Silver Armor Stand,Very Muddy Boots,,Serenity,A Glutton's Meal,Mega Spud,Annoying Orange,Wilson,Mr Finch's Hoe,Compost Mate,Farmer's Badge,,Armored Paws,Black Bird,Cowboy Hat,Earth,Pride Rock,Fake Tropical Fish,Super Rod,Potato Mine,Llama Drama,Matryoshka Doll,Barry B. Benson's Hive,Toilet,Ice Wand,Copper Goat Horn,FrogChamp,,Mobestiary,Lava Chicken,Vanilla Ice Cream,Molten Ice Cream,Hyperlink,Handsome Pumpkin,Pink Camo Pants,The Walking Head,Sans's Head,Ender Arrow,Basketblock,Etho's Anvil,Warden Head,The Warden's Sign,Nokia 3310,,Boomer T-Shirt,The Hylian Shield,1000-degree knife,Sculk Meteorite,Multiweapon,Really Really Pointy Arrow,Reuben the Wither Storm Ender,,Voyager 1,A blessing in love,Bouquet,,Hot Potato,Captain America's Shield,Bamboo Sword (Sharpness I),The Jungle Book,Waterbed,,Dinnerbone's Head,Jeb's Head,Crown of the Potato King,Medal of Honor,The Salad Bowl,Body Pillow,Ominous Shield,The Moon,Stonk Man's Head,Fogg's Pocket Watch,Your Cat's Prize,Eridium,Klefki,Uru,The Trophy Trophy,Golden Idol,Tron Suit,Vent,Iron Man Suit,,Spongebob Squarepants,,Quiver,Harp String,The Midnight - Monsters,Roller Coaster Cart,,Mobbo,The Cataclyst,,Steam Engine,,Finger Guns,1-UP Life,One-Punch Man's Fist,Fence Post,Fart in a Jar,Tinfoil Mining Helmet,,Strider Treat,M.O.A.B.,Enchanter's Tome,World's Most Reliable Shoes,Time Machine,Portable Trampoline,Noah's Ark,Zero Tick Farm,God Particle,Mammoth Steak,Black Pearl,Big Pointy Arrow,Superman's Cape,Flowey the Flower,Firearm's Firearm,Mimic,Refreshment,Gold Medal,New Year's Firework,Piston Cup,Thomas the Tank Engine,Black Belt,,Farmer's Badge V2,Brick Astley,Ultimate Flex,Plaid Block,Wormhole,Spinny Top,Mini Ghast,Stormbreaker,Baconator,Gilded Blade,Zork Chop,,Unknown Mixture,Fast and Furious,This is Anarchy,Stink Bomb,,TARS,Wizard's Fruit,Calendar,Portal Bow,Moon Rock,Ring of Bedrock,Singularity,Amalgamation,,Cosmonaut Helmet,Astronaut Helmet,Dragon Bro,Power Stone,Shiny Netherite Grade Ender Dragon Mob Trophy,Mario's Hat,Golden Advancement Plaque,Heart of a Siren,Amphitrite,Devil's Pitchfork,Space Stone,Reality Stone,Eye of the Apocalypse,Viceroy Nute Gunray,Notch's Head,Wishing Star,Corrupted Beacon,Treasure Chest,Frame of Infinite Items,Pandora's Box,Doraemon's Pocket,Nuclear Reactor,Mind Stone,Soul Stone,Cursed Creeper Head,Poglin,Hubble Space Telescope,ACDC - Back in Black,Endfinity Source,Potion Master's Diploma,Poison Mask,Infinity Gauntlet,Totem of Immortality,Time Stone,Instant Death,Stale Milk,Groot's Stick,Master Enchanter's Book,Cartographer's Quill,Wall Street,Stone of the Farlands".split(",")
# advs += "Miner's Trophy,Builder's Trophy,Farmer's Trophy,Butcher's Trophy,Slayer's Trophy,Sword Trophy,Explorer's Trophy,Adventurer's Trophy,Mechanic's Trophy,Enchanter's Trophy,Statistician's Trophy,Nether Adventurer's Trophy,Potion Brewer's Trophy,End Adventurer's Trophy,Challenger's Trophy,Yellow T-Shirt,,Azalea Parachute,Octuple Compressed Cobblestone,Golden Cobblestone,Steve's Head,Pyro's Mask,Spoon,Underpants,Santa's Present,Golem Kit,Copper Golem,Weathered Copper BlocK,Green Lantern Ring,M.A.R.I.L.L.A.,Copper Shortsword,Piñata,Baseball Bat,Energy Crystal,Golden Crown,Bean Block,Mayor's Throne,Chaos Emerald,Deepslate Emerald Ore,,Claptrap,Flex Tape,Stairway to Heaven,Logolas,Ch-ch-ch-ch-ch-ch-Cherry bomb!,Birthday Cake,Pickle Rick,Torch God's Favor,The Journal,Magic Wand,Magic Paintbrush,Sleepless Anchor,Silver Armor Stand,Very Muddy Boots,,Serenity,A Glutton's Meal,Mega Spud,Annoying Orange,Wilson,Mr Finch's Hoe,Compost Mate,Farmer's Badge,,Armored Paws,Black Bird,Cowboy Hat,Earth,Pride Rock,Fake Tropical Fish,Super Rod,Potato Mine,Llama Drama,Matryoshka Doll,Barry B. Benson's Hive,Toilet,Ice Wand,Copper Goat Horn,FrogChamp,,Mobestiary,Lava Chicken,Vanilla Ice Cream,Molten Ice Cream,Hyperlink,Handsome Pumpkin,Pink Camo Pants,The Walking Head,Sans's Head,Ender Arrow,Basketblock,Etho's Anvil,Warden Head,The Warden's Sign,Nokia 3310,,Boomer T-Shirt,The Hylian Shield,1000-degree knife,Sculk Meteorite,Multiweapon,Really Really Pointy Arrow,Reuben the Wither Storm Ender,,Voyager 1,A blessing in love,Bouquet,,Hot Potato,Captain America's Shield,Bamboo Sword (Sharpness I),The Jungle Book,Waterbed,,Dinnerbone's Head,Jeb's Head,Crown of the Potato King,Medal of Honor,The Salad Bowl,Body Pillow,Ominous Shield,The Moon,Stonk Man's Head,Fogg's Pocket Watch,Your Cat's Prize,Eridium,Klefki,Uru,The Trophy Trophy,Golden Idol,Tron Suit,Vent,Iron Man Suit,,Spongebob Squarepants,,Quiver,Harp String,The Midnight - Monsters,Roller Coaster Cart,,Mobbo,The Cataclyst,,Steam Engine,,Finger Guns,1-UP Life,One-Punch Man's Fist,Fence Post,Fart in a Jar,Tinfoil Mining Helmet,,Strider Treat,M.O.A.B.,Enchanter's Tome,World's Most Reliable Shoes,Time Machine,Portable Trampoline,Noah's Ark,Zero Tick Farm,God Particle,Mammoth Steak,Black Pearl,Big Pointy Arrow,Superman's Cape,Flowey the Flower,Firearm's Firearm,Mimic,Refreshment,Gold Medal,New Year's Firework,Piston Cup,Thomas the Tank Engine,Black Belt,,Farmer's Badge V2,Brick Astley,Ultimate Flex,Plaid Block,Wormhole,Spinny Top,Mini Ghast,Stormbreaker,Baconator,Gilded Blade,Zork Chop,,Unknown Mixture,Fast and Furious,This is Anarchy,Stink Bomb,,TARS,Wizard's Fruit,Calendar,Portal Bow,Moon Rock,Ring of Bedrock,Singularity,Amalgamation,,Cosmonaut Helmet,Astronaut Helmet,Dragon Bro,Power Stone,Shiny Netherite Grade Ender Dragon Mob Trophy,Mario's Hat,Golden Advancement Plaque,Heart of a Siren,Amphitrite,Devil's Pitchfork,Space Stone,Reality Stone,Eye of the Apocalypse,Viceroy Nute Gunray,Notch's Head,Wishing Star,Corrupted Beacon,Treasure Chest,Frame of Infinite Items,Pandora's Box,Doraemon's Pocket,Nuclear Reactor,Mind Stone,Soul Stone,Cursed Creeper Head,Poglin,Hubble Space Telescope,ACDC - Back in Black,Endfinity Source,Potion Master's Diploma,Poison Mask,Infinity Gauntlet,Totem of Immortality,Time Stone,Instant Death,Stale Milk,Groot's Stick,Master Enchanter's Book,Cartographer's Quill,Wall Street,Stone of the Farlands".split(",")


# Count all duplicate advs
# advs = [a.strip() for a in advs]
# c = [(a, b) for a, b in Counter(advs).items()]
# print([cn for cn in c if cn[1] >= 2])

# Single letters in words
# for a in ladvs:
#     a = a.split()
#     for w in a:
#         if len(w) == 1 and w != 'A' and w != 'I':
#             print(" ".join(a))
#             break

# Repeated words
# for a in ladvs:
#     a = a.split()
#     words = []
#     for w in a:
#         if w in words:
#             print(" ".join(a))
#             break
#         words.append(w)

# Sort advs into non-title case
# for a in advs:
#     a = a.split()
#     if len(a) == 4:
#         print(" ".join(a))
#     for w in a:
#         words = []
#         if w[0] in "abcdefghijklmnopqrstuvwxyz" and len(w) > 3:
#             print(" ".join(a))
#             break

#

# Sort words by how many times they appear in adv names
words = defaultdict(int)
for a in ladvs:
    for word in a.split():
        words[word] += 1
print(sorted([(a, b) for a, b in words.items()], key=lambda x: x[1], reverse=True))

obscurity = [(a,
              sum(words[w] for w in a.split()),
              [(w, words[w]) for w in a.split()]
              ) for a in ladvs]
obscurity.sort(key=lambda x: x[1])
print(obscurity)

    # if len(o[0].split()) == o[1]:
    #     print(o)

# for a in ladvs:
#     a = a.split()
#     if len(a) == 4:
#         print([(w, words[w]) for w in a])


time.sleep(1000)

# Sort advs by length letters only
# ladvs = ["".join([c.upper() for c in adv if c.lower() in "abcdefghijklmnopqrstuvwxyz0123456789"]) for adv in advs]
# res = list(zip(ladvs, [len(l) for l in ladvs]))
# res.sort(key=lambda x: x[1])
# for l in res:
#     print(l)

#
# # Exit code 1
# print(advs[1000000])

candidates = []

# candidates = [a for a in advs if len(a) > 10 and len(a.split()) == 1] + [a for a in advs if len(a) > 10 and len(a.split()) == 1] + [a for a in advs if len(a) > 10 and len(a.split()) == 1] + [a for a in advs if len(a) > 10 and len(a.split()) == 1] + [a for a in advs if len(a) <= 10 and len(a.split()) == 1]
candidates = [a for a in advs if len(a) <= 32]
# candidates = [a for a in advs if len(a.split()) >= 4 and len(a) <= 32]
# advs = [a for a in advs2 if len(a) >= 12 and len(a) <= 32]
# advs = [a for a in advs2 if len(a.split()) > 1 and len(a) <= 32]

filler = []
# vowels = "a e i o u".split()
# for a in advs:
#     vowelsonly = [c for c in a.lower() if c in vowels]
#     # print(vowelsonly)
#     filler.append((len(vowelsonly), a, vowelsonly))
# filler.sort(key=lambda a: len(a[2]))

for q in filler:
    print(q)

# advs is after processing
for i in range(len(candidates)):
    candidates[i] = candidates[i].replace("!", "")
    candidates[i] = candidates[i].replace(",", "")
    candidates[i] = candidates[i].replace(".", "")
    candidates[i] = candidates[i].replace("?", "")
    candidates[i] = candidates[i].replace("…", "")
    candidates[i] = candidates[i].replace(":", "")
    candidates[i] = candidates[i].replace("(", "")
    candidates[i] = candidates[i].replace(")", "")
    candidates[i] = candidates[i].replace("&", "and")
    # c = candidates[i].split()
    # candidates[i] = " ".join(c[:2]) + "," + " ".join(c[2:])

for a in candidates:
    print(a)
print(len(candidates))

res = []

while candidates:
    res.append(candidates.pop(random.randrange(0, len(candidates))))

str = ",".join(res)
print(str)
print(len(str))


# database_data = cursor.execute('''SELECT name, description from advancements''')
# d = database_data.fetchall()

# d.sort(key=lambda d: len(d[1]))
# for name, description in d:
#     print(name, len(description), "       ", description)



#    {
#       name "Advancement Name": "BlazeandCave's Advancements Pack",
#       description "Description": "Loads of brand new advancements for your Minecraft world!",
#       adv_tab "adv_tab": "B&C Advancements",
#       category "Category": "root"
#       actual_reqs "Actual Requirements (if different)": "Obtained automatically when entering the world",
#       item_reward "Item rewards": "",
#       xp_reward "XP Rewards": "",
#       hidden "Hidden?": "-",
#       "Trophy": "",
#       parent "Parent": "",
#       children "Children": "Getting Wood",
#       "Source": "Original tab",
#       "Version added": 1.4,
#       "Notes": "Named \"BlazeandCave's Advancements\" until BACAP 1.18",

#    },



# for i, adv in enumerate(candidates):
#     # 20 to 70
#     print(f"{"".join([
#         ((" " if c == " " else "_")
#         if random.randrange(0, 100) > 70-i/2 and c in "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
#         else c)
#         for c in adv
#
#     ])}" + "\t" + f"{adv}")

# for i in range(472):
#     print(advs[i][:3] + f" ({len(advs[i])})" + "\t" + advs[i])

