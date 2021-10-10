import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, logging
from werkzeug.exceptions import abort

from logging.config import dictConfig


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s: %(module)s: [%(asctime)s]: %(message)s', 
        'datefmt': '%Y/%m/%d %H:%M:%S',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Define an variable for database connection cound
db_connections = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    #count +1 to the variable everytime the connection is initialized
    global db_connections
    db_connections += 1

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    if post is not None:
        app.logger.info('Article %s received', post["title"])

    connection.close()
    return post

# Function to count all posts using the IDs
def count_posts():
    connection = get_db_connection()
    count = connection.execute('SELECT count(id) FROM posts').fetchone()[0]
    connection.close()
    return count

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('404 Page received')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page received')

    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New article with title %s created', title)

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def health():
    app.logger.info('Status request successfull')
    return "result: OK - healthy", 200

@app.route('/metrics')
def metrics():
    app.logger.info('metrics request successfull')

    global db_connections

    metrics = {
        "db_connection_count":db_connections,
        "post_count":count_posts()
    }

    return jsonify(metrics),200

# start the application on port 3111
# according to the flask documentation:
# Set debug to true
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111', debug=True)