import time, requests

url = "192.168.0.0" # take from .env file

def inputNewPost():
  print("NEW POST (Press Ctr-D and Enter to finsih post)")
  lines = []
  while True:
    try:
        line = input()
        lines.append(line)
    except EOFError:
      break
  
  return lines

def packagePost(postInput):
   postJSON = {
      "title": postInput[0],
      "body": ('\n'.join(postInput[1:])).rstrip(),
      "postTime": int(time.time())
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

newPostObject = packagePost(inputNewPost())
print(newPostObject)
sendPost(newPostObject)