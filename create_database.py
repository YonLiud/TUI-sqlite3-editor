import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# create a template table
c.execute('''CREATE TABLE IF NOT EXISTS foo (
    id INTEGER PRIMARY KEY,
    name TEXT
    )''')
conn.commit()

# insert a row of data
c.execute("INSERT INTO foo (name) VALUES ('bar')")
c.execute("INSERT INTO foo (name) VALUES ('baz')")
c.execute("INSERT INTO foo (name) VALUES ('qux')")
conn.commit()

conn.close()