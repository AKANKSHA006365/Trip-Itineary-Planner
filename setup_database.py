import sqlite3
import csv

conn = sqlite3.connect("itinerary.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    place_name TEXT,
    hours INTEGER
)
""")

# Clear old data (optional)
cursor.execute("DELETE FROM places")

# Read CSV and insert data
with open("places.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # skip header

    for row in reader:
        if len(row)!=3:
            continue
        city, place, hours = row
        cursor.execute(
            "INSERT INTO places (city, place_name, hours) VALUES (?, ?, ?)",
            (city, place, int(hours))
        )

conn.commit()
conn.close()

print("Database created from CSV successfully!")