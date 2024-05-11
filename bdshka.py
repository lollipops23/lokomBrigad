import sqlite3 as sq

# Создание таблицы "Mach" в базе данных "driver.db"
with sq.connect('driver.db') as conn:
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE driv_info(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        sex TEXT CHECK(sex IN ('M', 'F')),
        izo BLOB,
        data TEXT,
        smena TEXT
    )""")


    cursor.execute("""CREATE TABLE face(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_ID INTEGER,
        izo BLOB,
        time TIMESTAMP
        data TEXT,
        )""")

    cursor.execute("INSERT INTO driv_info (id, name, age, sex, data, smena) VALUES (1, 'Eugene', 18, 'M', 'aye', 'smena')")
    cursor.execute("INSERT INTO driv_info (id, name, age, sex, data, smena) VALUES (2, 'Eugene', 19, 'F', 'aye', 'smena')")
    cursor.execute("INSERT INTO face(ID, machine_ID, izo, time) VALUES (3,1,2,1500)")
    with sq.connect('driver.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM driv")
        rows = cursor.fetchall()

        for row in rows:
            print(row)
