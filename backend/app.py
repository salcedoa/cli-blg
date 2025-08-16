from flask import Flask, request, render_template
from dotenv import dotenv_values
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import re, os

db = SQLAlchemy()
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "db/posts.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.init_app(app)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=False)
    postTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# tables and models are created
with app.app_context():
    db.create_all()

# Setting up variables from .env
config = dotenv_values(".env")
customTimeFormat = config["TIMEFORMAT"]
name = config["TITLE"]
postsPerPage = int(config["POSTS_PER_PAGE"])

@app.route('/')
def posts(page=1):
    # Query the database for all posts and return them in a JSON string object
    page = db.paginate(db.select(Posts).order_by(Posts.postTime.desc()), per_page=postsPerPage)
    
    # Reformat the text and date for display
    for post in page.items:
        post.body = parseBody(post.body)
        post.postTime = convertTime(post.postTime)
    
    return render_template("index.html",page=page, name=name)

@app.route('/json', methods=['POST'])
def processPost():
    # Get the JSON data from request and create dictionary
    postObject = request.json

    post = Posts(title=postObject['title'], body=postObject['body'], postTime=convertJsonToDatetime(postObject['postTime']))
    db.session.add(post)
    db.session.commit()

    return 'New post added!'

# SQLite Datetime only accepts Python datetime, so the JSON request is converted
def convertJsonToDatetime(jsonTime):
    datetimeObject = datetime.strptime(jsonTime, "%Y-%m-%d %H:%M:%S")
    return datetimeObject

@app.teardown_appcontext
def close_connection(exception):
    db.session.remove()

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
    displayTime = datetime.strftime(fetchedDateTime, customTimeFormat)
    return displayTime

if __name__ == '__main__':
    db.create_all()
    app.run()