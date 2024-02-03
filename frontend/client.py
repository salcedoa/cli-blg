import time, requests, platform
from dotenv import dotenv_values
from datetime import datetime
import json

# get .env values
config = dotenv_values(".env")
url = config['DOMAIN'] + ':' + config['PORT'] + '/'

windowsURL = 'http://' + config['DOMAIN'] + ':' + config['PORT'] + '/'

def inputNewPost():
  print("NEW POST (Press CTRL-D (on Unix) or CTRL-Z (on Windows) and Enter to finish post)")
  lines = []
  while True:
    try:
        line = input()
        lines.append(line)
    except EOFError:
      break
  
  return lines

def packagePost(postInput):
   now = datetime.now()
   sqlDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

   postJSON = {
      "title": postInput[0],
      "body": ('\n'.join(postInput[1:])).rstrip(),
      "postTime": sqlDatetime
   }

   return postJSON

def sendPost(post):
    if post["title"] != None:
      try:
        requests.post(url + "/json", json=post)
      except requests.exceptions.RequestException as e:
         print(e)
         exit()
    else:
       print("Post must not be empty")

def sendPostWindows(post):
    if post["title"] != None:
      try:
        requests.post(windowsURL + "json", json=post)
      except requests.exceptions.RequestException as e:
          print(e)
          exit()
    else:
        print("Post must not be empty")

newPostObject = packagePost(inputNewPost())
print(newPostObject)

if platform.system() == 'Windows': sendPostWindows(newPostObject)
else: sendPost(newPostObject)
