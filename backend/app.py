from flask import Flask, request, render_template, g
from dotenv import dotenv_values
from datetime import datetime
import sqlite3, re

app = Flask(__name__)

# config for development
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Setting up variables from .env
config = dotenv_values(".env")
customTimeFormat = config["TIMEFORMAT"]
name = config["NAME"]

# Set the main header of the web page
if name != "": name = config["NAME"]
elif name == "": name = "my"
else: raise Exception("No name variable detected, please ensure that you set up the .env file")
currentMonth = datetime.now().strftime("%B").lower() + " " + str(datetime.now().year)

@app.route("/")
def index():
    # Query the database for all posts and return them in a JSON string object
    return render_template("index.html",posts=fetchPosts(), name=name, date=currentMonth)

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
    
    return render_template('index.html', posts=fetchPosts(), name=name)

@app.route('/archive')
def handleArchive():
    return render_template("archive.html", name=name, months=fetchMonths())

# DATABASE FUNCTIONS
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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

# Returns all posts from the database
def fetchPosts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY postTime DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Store the query results into a json object (python list)
    allPosts = [{'title': row[1], 'body': parseBody(row[2]), 'postTime': convertTime(row[3])} for row in rows]
    return allPosts

# Returns all unique month and year combinations from posts
def fetchMonths():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT strftime('%m', postTime) AS month, strftime('%Y', postTime) AS year FROM posts")
    rows = cursor.fetchall()
    conn.close()

    # Convert month number received from the SQLite query to month name
    months = [list(row) for row in rows]
    for m in months:
        m[0] = datetime.strptime(m[0], '%m').strftime('%B').lower()
    
    return months

# Returns an entry body which has been formatted to be displayed with HTML
def parseBody(text):

    # Detect links - excludes links inside quotes
    urlRegex = r'(?<![\"\'])\bhttps?://\S+\b(?!(?:(?!<img\s).)*<\/img>)'
    text = re.sub(urlRegex, r'<a href="\g<0>">\g<0></a>', text)

    # Replace \n with HTML line breaks
    formattedText = text.replace('\n', '<br>')
    
    return formattedText

# Returns the timestamp in the specified format
def convertTime(fetchedDateTime):
    print(fetchedDateTime)
    formatTime = datetime.strptime(fetchedDateTime, '%Y-%m-%d %H:%M:%S')
    displayTime = datetime.strftime(formatTime, customTimeFormat)
    return displayTime

# For filtering, this function returns the date and year of the post
def getMonthYear(fetchedDateTime):
    fullDateTime = datetime.strptime(fetchedDateTime, '%Y-%m-%d %H:%M:%S')
    return fullDateTime.strftime('%B %Y')

if __name__ == '__main__':
    app.run()
