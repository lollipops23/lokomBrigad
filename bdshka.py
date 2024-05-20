import sqlite3 as sq

with sq.connect('driver.db') as conn:
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE driv_info(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        sex TEXT CHECK(sex IN ('M', 'F')),
        image_driv BLOB
    )""")

    cursor.execute("""CREATE TABLE face(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_ID INTEGER,
        image_contol BLOB,
        time TEXT,
        date TEXT,
        control TEXT CHECK(control IN ('прошел', 'не прошел'))
    )""")

    cursor.execute("INSERT INTO driv_info (name, age, sex, image_driv) VALUES ('Abramovich Eugene', 19, 'M', 'photo/Abramovich.jpg')")
    cursor.execute("INSERT INTO driv_info (name, age, sex, image_driv) VALUES ('Tirsina Ekaterina', 20, 'F', 'photo/Tirsina.jpg')")
    cursor.execute("INSERT INTO face(machine_ID, image_contol, time, date, control) VALUES (1, 'control_image', '10:30:00', '2024-05-16', 'прошел')")

with sq.connect('driver.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM driv_info")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.execute("SELECT * FROM face")
    rows = cursor.fetchall()

    for row in rows:
        print(row)