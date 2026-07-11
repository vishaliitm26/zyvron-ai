import sqlite3

conn = sqlite3.connect("zyvron.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    date TEXT,

    time TEXT,

    pregnancies REAL,

    glucose REAL,

    blood_pressure REAL,

    skin_thickness REAL,

    insulin REAL,

    bmi REAL,

    dpf REAL,

    age REAL,

    prediction TEXT,

    risk REAL

)
""")

conn.commit()

conn.close()

print("Database Created Successfully!")