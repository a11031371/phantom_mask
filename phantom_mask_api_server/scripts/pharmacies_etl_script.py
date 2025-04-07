import json
import sqlite3
import re

""" ETL script to extract, transform and load pharmacy data from JSON file into SQLite database """

# read json data
with open("data/pharmacies.json", "r", encoding="utf-8") as f:
    pharmacies_data = json.load(f)

# SQLite connection
conn = sqlite3.connect("../db/phantom_mask_db.db")
cursor = conn.cursor()

def parse_opening_hours(opening_hours):
    """ Parses an opening hours string and converts it into a structured format

    Args:
        opening_hours (str): A string representing the opening hours

    Returns:
        dict[str, tuple[str | None, str | None]]: 
            A dictionary where keys are weekdays (Mon - Sun);
            and values are tuples representing (opening_time, closing_time)
    """


    # initialize return dict
    hours_dict = {
        "Mon": (None, None), "Tue": (None, None), "Wed": (None, None), "Thu": (None, None), 
        "Fri": (None, None), "Sat": (None, None), "Sun": (None, None)
    }

    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]   # used for days string in range expression 
    
    periods = opening_hours.split(" / ")    # opening hours for multiple days (split by " / "")
    for period in periods:
        match = re.match(r"([\w, -]+) (\d{2}:\d{2}) - (\d{2}:\d{2})", period)   # regex pattern to match the format
        if match:
            days, opening_time, closing_time = match.groups()
            if "-" in days: # range expression
                start, end = days.split(" - ")
                start_idx = day_order.index(start)
                end_idx = day_order.index(end)  # note that start_idx must before end_idx
                for i in range(start_idx, end_idx + 1):
                    hours_dict[day_order[i]] = (opening_time, closing_time) 
            elif "," in days: # comma expression
                for day in days.split(", "):
                    hours_dict[day] = (opening_time, closing_time)
            # any other expression in the future

    return hours_dict


def parse_mask_name(mask_name):
    """ Parses a mask name string and extracts model, color and num_per_pack

    Args:
        mask_name (str): A string representing the mask name (e.g. "MaskT (green) (10 per pack)")

    Returns:
        tuple[str, str, int]: A tuple containing model, color and num_per_pack
    """
    match = re.match(r"(.+) \((.+)\) \((\d+) per pack\)", mask_name)    # regex pattern to match the format
    if match:
        model, color, num_per_pack = match.groups()
        return model.strip(), color.strip(), int(num_per_pack)
    # else:
    #     raise ValueError("Invalid mask name format")

# insert data
def insert_pharmacy_data():
    for pharmacy in pharmacies_data:
        hours = parse_opening_hours(pharmacy["openingHours"])
        # insert pharmacy name, cash balance, and opening hours
        cursor.execute("""
            INSERT INTO pharmacies (name, cash_balance, 
            mon_open, mon_close, tue_open, tue_close, wed_open, wed_close, 
            thu_open, thu_close, fri_open, fri_close, sat_open, sat_close, 
            sun_open, sun_close)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pharmacy["name"], pharmacy["cashBalance"],
            hours["Mon"][0], hours["Mon"][1], hours["Tue"][0], hours["Tue"][1],
            hours["Wed"][0], hours["Wed"][1], hours["Thu"][0], hours["Thu"][1],
            hours["Fri"][0], hours["Fri"][1], hours["Sat"][0], hours["Sat"][1],
            hours["Sun"][0], hours["Sun"][1]
        ))

def insert_masks_data():
    for pharmacy in pharmacies_data:
        for mask in pharmacy["masks"]:
            model, color, num_per_pack = parse_mask_name(mask["name"])
            cursor.execute("""
                INSERT OR IGNORE INTO masks (model, color, num_per_pack, name)
                VALUES (?, ?, ?, ?)
            """, (model, color, num_per_pack, mask["name"]))

def insert_pharmacy_masks_data():
    for pharmacy in pharmacies_data:
        pharmacy_id = cursor.execute("""
            SELECT id FROM pharmacies WHERE name = ?""", (pharmacy["name"],)
        ).fetchone()[0]

        for mask in pharmacy["masks"]:
            model, color, num_per_pack = parse_mask_name(mask["name"])
            cursor.execute("""
                SELECT id FROM masks WHERE model = ? AND color = ? AND num_per_pack = ?
            """, (model, color, num_per_pack))
            mask_id = cursor.fetchone()[0]
            price = mask["price"]
            cursor.execute("""
                INSERT INTO pharmacy_masks (mask_id, pharmacy_id, price)
                VALUES (?, ?, ?) """, (mask_id, pharmacy_id, price)
            )
            
insert_pharmacy_data()
insert_masks_data()
insert_pharmacy_masks_data()

conn.commit()
conn.close()


