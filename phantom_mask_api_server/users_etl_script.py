import json
import sqlite3
import re

"""
ETL script to extract, transform and load user data from JSON file into SQLite database

"""

# read json data
with open("../data/users.json", "r", encoding="utf-8") as f:
    users_data = json.load(f)

# SQLite connection
conn = sqlite3.connect("phantom_mask_db.sqlite3")
cursor = conn.cursor()

def parse_mask_name(mask_name):
    """Parses a mask name string and extracts model, color and num_per_pack

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
def insert_data():
    for user in users_data:
        # insert user data
        cursor.execute("""
            INSERT INTO users (name, cash_balance)
            VALUES (?, ?)
        """, (user["name"], user["cashBalance"]))

        # get user ID
        user_id = cursor.execute("""SELECT id FROM users WHERE name = ?""", (user["name"],)).fetchone()[0]

        #  "pharmacyName": "Keystone Pharmacy",
        # "maskName": "True Barrier (green) (3 per pack)",
        # "transactionAmount": 12.35,
        # "transactionDate": "2021-01-04 15:18:51"

        # insert transaction data
        for transaction in user["purchaseHistories"]:
            model, color, num_per_pack = parse_mask_name(transaction["maskName"])

            # get pharmacy ID
            cursor.execute("SELECT id FROM pharmacies WHERE name = ?", (transaction["pharmacyName"],))
            pharmacy_id = cursor.fetchone()[0]

            # get mask ID
            cursor.execute("SELECT id FROM masks WHERE model = ? AND color = ? AND num_per_pack = ?", (model, color, num_per_pack))
            mask_result = cursor.fetchone()
            if mask_result is None:
                print(f"{user["name"]}, Mask not found: {model}, {color}, {num_per_pack}")
                continue
            else:
                mask_id = mask_result[0]

            # insert transaction
            cursor.execute("""
                INSERT INTO transactions (user_id, pharmacy_id, mask_id, transaction_amount, transaction_date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, pharmacy_id, mask_id, transaction["transactionAmount"], transaction["transactionDate"]))

insert_data()
conn.commit()
conn.close()