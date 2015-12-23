import sqlite3

with sqlite3.connect("blog.db") as connection:
	c = connection.cursor()
	c.execute("""DROP TABLE IF EXISTS users""")
	c.execute("""DROP TABLE IF EXISTS posts""")
	c.execute("""DROP TABLE IF EXISTS categories""")

	c.execute("""CREATE TABLE users(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_name TEXT NOT NULL,
	password TEXT NOT NULL)""")

	c.execute("""CREATE TABLE posts(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	author TEXT,
	title TEXT,
	content TEXT,
	pub_status BOOLEAN NOT NULL DEFAULT "published",
	permalink TEXT,
	category TEXT,
	date_posted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP )""")

	c.execute("""CREATE TABLE categories(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	category TEXT NOT NULL)""")

	c.execute('INSERT INTO users (user_name, password) values ("user01", "password01")')
	c.execute('INSERT INTO users (user_name, password) values ("user02", "password02")')
	c.execute('INSERT INTO posts (author, title, content, permalink) values ("user01", "Python user01 Basics", "Lorem ipisum dorem.", "test-for-user1")')
	c.execute('INSERT INTO posts (author, title, content, permalink) values ("user02", "Another Python user02 Basics", "Lorem ipisum dorem.", "test-for-user2")')
	c.execute('INSERT INTO categories (category) values ("category01")')
	c.execute('INSERT INTO categories (category) values ("category02")')
