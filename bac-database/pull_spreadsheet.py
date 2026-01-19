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

def read_datapack(pack_name):
    adv_directories = [f"./packs/{pack_name}/data/blazeandcave/advancement",
                       f"./packs/{pack_name}/data/minecraft/advancement"]
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

                # Get FILE PATH
                advs[adv_index[title.upper()]]["File path"] = adv_path

                # if "extra" in adv["display"]["description"].keys() and "view progress" not in str(adv["display"]["description"]) and "The following are" not in str(adv["display"]["description"]):
                #     print(adv["display"]["description"])

                if "extra" in adv["display"]["title"].keys() and title != "Riddle Me This":
                    # print(adv["display"]["title"])
                    for extra in adv["display"]["title"]["extra"]:
                        title += extra["translate" if "translate" in extra.keys() else "text"]
                if title == "Feeding the §mDucks§r Chickens":
                    title = "Feeding the Ducks Chickens"

                if title.upper() not in adv_index:
                    print(f"Bad title: {title}")
                else:
                    # GET ICON (and if it's enchanted)
                    advs[adv_index[title.upper()]]["Icon"] = adv["display"]["icon"]["id"].replace("minecraft:", "")
                    if "components" in adv["display"]["icon"]:
                        if "minecraft:enchantment_glint_override" in adv["display"]["icon"]["components"]:
                            advs[adv_index[title.upper()]]["Enchanted"] = True
                        else:
                            advs[adv_index[title.upper()]]["Enchanted"] = False

                    # GET CRITERIA COUNT
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
READ_DATAPACK = True
SET_DATABASE = True

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
    read_datapack("BlazeandCaves Advancements Pack 1.20")
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
            file_path TEXT,
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
                trophy, file_path, parent, children, source,
                version, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            entry.get("File path"),
            entry.get("Parent"),
            entry.get("Children"),
            entry.get("Source"),
            str(entry.get("Version added")),  # Cast to string in case of floats
            entry.get("Notes")
        ))

    conn.commit()
database_data = cursor.execute('''SELECT name from advancements ''')
# database_data = cursor.execute('''SELECT name from advancements WHERE name like 'a%' ''')
# database_data = cursor.execute('''SELECT name from advancements WHERE version like '%1.20%' OR version like '%1.19%' OR version like '%1.18%' OR version like '%1.17%' OR version like '%1.16%' ''')
d = database_data.fetchall()
advs = [adv[0] for adv in d]

for l in advs:
    print(l)

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

