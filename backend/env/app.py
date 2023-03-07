from flask import Flask, request, render_template, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "test"
customTimeFormat = "%d-%m-%Y @ %H:%M"

@app.route("/")
def index():
    # query the database for all posts and return them in a JSON string object
    return render_template("index.html",posts=fetchPosts())

@app.route('/json', methods=['POST'])
def processPost():
    # Get the JSON data from request and create dictionary
    postObject = request.json
    
    # Insert the dictionary data into the database
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO posts (title, body, postTime) VALUES (?, ?, ?)', (postObject['title'], postObject['body'], postObject['postTime']))
    conn.commit()
    conn.close()
    
    return 'Post saved!'

# DATABASE FUNCTIONS
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("db/posts.db")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# returns all posts from the database
def fetchPosts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY postTime DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # store the query results into a json object (python list)
    allPosts = [{'title': row[1], 'body': row[2], 'postTime': convertTime(row[3])} for row in rows]
    return allPosts

def convertTime(fetchedTime):
    # Convert epoch time to datetime object
    datetimeObject = datetime.fromtimestamp(fetchedTime)

    # Convert datetime object to custom format string
    displayTime = datetimeObject.strftime(customTimeFormat)

    return displayTime

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    app.run()