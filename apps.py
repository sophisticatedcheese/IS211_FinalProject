__author__ = 'T Jeremiah December 2015'

from flask import Flask, g, render_template, redirect, request, url_for, session, flash
from functools import wraps
import sqlite3
from datetime import datetime
import urllib

app = Flask(__name__)
app.secret_key = "not a good secret. Nope, not at all"
app.database = "blog.db"
app.config['DEBUG'] = True


def connect_db():
    return sqlite3.connect(app.database)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@app.route('/index')
def index():
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts WHERE pub_status="published" ORDER BY `date_posted` DESC')
    posts = [dict(id=row[0], author=row[1], title=row[2], content=row[3], pub_status=row[4], permalink=row[5], category=row[6], date=datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S')) for row in cur.fetchall()]
    cur = g.db.execute('SELECT * FROM categories')
    categories = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]

    return render_template('index.html', posts=posts, categories=categories, title='Blog')


@app.route('/posts/<post_id>/<permalink>', methods=['GET','POST'])
def display_post(post_id, permalink):
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts WHERE id = ? AND permalink = ?', (post_id, permalink))
    post = cur.fetchone()

    cur = g.db.execute('SELECT * FROM categories')
    categories = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]

    if( post ):
        return render_template('single-post.html', post = post, categories=categories, title='Edit Post' )

    return redirect(url_for('index'))


@app.route('/<category>', methods=['GET'])
def display_category(category):

    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts WHERE pub_status="published" AND category = ? ORDER BY `date_posted` DESC', (category,))
    posts = [dict(id=row[0], author=row[1], title=row[2], content=row[3], pub_status=row[4], permalink=row[5], category=row[6], date=datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S')) for row in cur.fetchall()]

    cur = g.db.execute('SELECT * FROM categories')
    categories = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]

    if( category ):
        return render_template('single-category.html', posts = posts, categories=categories, title='Edit Post' )

    return redirect(url_for('index'))


@app.route('/remove-category/<category>', methods=['GET','POST'])
@login_required
def remove_category(category):
    g.db = connect_db()
    g.db.execute('DELETE FROM categories WHERE category = ?', (category,))

    g.db.execute('UPDATE posts SET category=NULL WHERE category=?', (category,))
    g.db.commit()

    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    username = session['username']
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts WHERE author = ?', (username,))
    posts = [dict(id=row[0], author=row[1], title=row[2], content=row[3], pub_status=row[4], category=row[6]) for row in cur.fetchall()]

    cur = g.db.execute('SELECT * FROM categories')
    categories = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]

    return render_template('dashboard.html', posts=posts, categories=categories, title='Dashboard')


@app.route('/add_post', methods=['POST'])
@login_required
def add_post():
    username = session['username']

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        permalink = urllib.parse.quote_plus(title, safe='', encoding=None, errors=None)

        if len(title.strip()) < 1 or len(content.strip()) < 1:
            flash("Empty field. Please try again.")
        else:
            g.db = connect_db()
            g.db.execute('INSERT INTO posts (author, title, content, permalink, category) values (?, ?, ?, ?, ?)', (username, title, content, permalink, category))
            g.db.commit()
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', title='Blog')


@app.route('/add_category', methods=['POST'])
@login_required
def add_category():

    if request.method == 'POST':
        category = request.form['category']

        if len(category.strip()) > 0:

            g.db = connect_db()
            g.db.execute('INSERT INTO categories (category) values (?)', (category,))
            g.db.commit()

    return redirect(url_for('dashboard'))


@app.route('/delete/<post_id>', methods=['GET','POST'])
@login_required
def delete(post_id):
    g.db = connect_db()
    g.db.execute('DELETE FROM posts WHERE id = %s' % (post_id))
    g.db.commit()

    return redirect(url_for('dashboard'))


@app.route('/unpublish/<post_id>', methods=['GET','POST'])
@login_required
def unpublish(post_id):
    g.db = connect_db()
    g.db.execute('UPDATE posts SET pub_status="unpublished" WHERE id=?', (post_id))
    g.db.commit()

    return redirect(url_for('dashboard'))


@app.route('/publish/<post_id>', methods=['GET','POST'])
@login_required
def publish(post_id):
    g.db = connect_db()
    g.db.execute('UPDATE posts SET pub_status="published" WHERE id=?', (post_id))
    g.db.commit()

    return redirect(url_for('dashboard'))


@app.route('/edit/<post_id>', methods=['GET','POST'])
@login_required
def edit(post_id):
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM posts WHERE id = %s' % (post_id))
    post = cur.fetchone()

    cur = g.db.execute('SELECT * FROM categories')
    categories = [dict(name=row[1]) for row in cur.fetchall()]

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']

        g.db = connect_db()
        g.db.execute('UPDATE posts SET title=?, content=?, category=? WHERE id=?', (title, content, category, post_id))
        g.db.commit()
        return redirect(url_for('dashboard'))

    return render_template('post-edit.html', post = post, categories=categories, title='Edit Post' )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(username.strip()) < 1 or len(password.strip()) < 1:
            flash("Empty field. Please try again.")
        else:
            g.db = connect_db()
            cur = g.db.execute('SELECT * from users where user_name = ? AND password = ?', (username, password,))
            data = cur.fetchone()

            if data is None:
                flash("Wrong username or password. Please try again.")
            else:
                session['username'] = username
                session['logged_in'] = True
            return redirect(url_for('dashboard'))

    return render_template('login.html',title='Login')


@app.route('/logout')
def logout():
    session.pop('logged_in', True)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()