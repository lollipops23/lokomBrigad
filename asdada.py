import sqlite3

conn = sqlite3.connect('driver.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM driv")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.execute("SELECT * FROM face")
rows = cursor.fetchall()

for row in rows:
    print(row)
conn.close()