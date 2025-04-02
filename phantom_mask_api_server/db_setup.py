import sqlite3

# SQLite connection 
conn = sqlite3.connect("phantom_mask_db.sqlite3")
cursor = conn.cursor()

# create tables (users, pharmacies, masks, transactions, pharmacy_masks)
cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cash_balance REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS pharmacies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    cash_balance REAL NOT NULL,
    mon_open TEXT, mon_close TEXT,
    tue_open TEXT, tue_close TEXT,
    wed_open TEXT, wed_close TEXT,
    thu_open TEXT, thu_close TEXT,
    fri_open TEXT, fri_close TEXT,
    sat_open TEXT, sat_close TEXT,
    sun_open TEXT, sun_close TEXT
);

CREATE TABLE IF NOT EXISTS masks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    color TEXT NOT NULL,
    num_per_pack INTEGER NOT NULL,
    UNIQUE (model, color, num_per_pack)
);
                     
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pharmacy_id INTEGER NOT NULL,
    mask_id INTEGER NOT NULL,
    transaction_amount REAL NOT NULL,
    transaction_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id),
    FOREIGN KEY (mask_id) REFERENCES masks(id)
);
                     
CREATE TABLE IF NOT EXISTS pharmacy_masks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mask_id INTEGER NOT NULL,
    pharmacy_id INTEGER NOT NULL,
    price REAL NOT NULL,
    UNIQUE (mask_id, pharmacy_id),
    FOREIGN KEY (mask_id) REFERENCES masks(id),
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id)
);
""")

conn.commit()
conn.close()