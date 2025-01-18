
import os
import requests
import json
import random
import time
import re
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from io import BytesIO
from urllib.parse import urlparse


#load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("careerwill_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

u = [
    "okhttp/5.0.0-alpha.1",
    "okhttp/5.0.0-alpha.2",
    "okhttp/5.0.0-alpha.3",
    "okhttp/5.0.0-alpha.4",
    "okhttp/5.0.0-alpha.5",
    "okhttp/5.0.0-alpha.6",
    "okhttp/5.0.0-alpha.7",
    "okhttp/5.0.0-alpha.8",
    "okhttp/5.0.0-alpha.9",
    "okhttp/5.0.0-alpha.10",
]

headers = {
    "authority": "elearn.crwilladmin.com",
    "accept": "application/json",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://web.careerwill.com",
    "apptype": "web",
    "referer": "https://web.careerwill.com/",
    "user-agent": "okhttp/5.0.0-alpha.2",
}

headers2 = headers.copy()
batchidl = {}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_token(email, password):
    data1 = {
        "email": email,
        "password": password,
        "deviceType": "web",
        "deviceVersion": "Chrome 122",
        "deviceModel": "chrome",
    }
    headers1 = headers
    response1 = requests.post(
        "https://elearn.crwilladmin.com/api/v5/login-other",
        headers=headers1,
        data=data1,
        timeout = 30,
    )
    response1.raise_for_status()
    resp1 = response1.text
    token = json.loads(resp1)["data"]["token"]
    return token

def print_batches(token):
    headers2["token"] = token
    response2 = requests.get(
        "https://elearn.crwilladmin.com/api/v5/my-batch", headers=headers2, timeout = 30
    )
    response2.raise_for_status()
    resp2 = response2.text
    batch_data = json.loads(resp2)["data"]["batchData"]
    table_data = [(batch["id"], batch["batchName"]) for batch in batch_data]
    return tabulate(
                table_data, headers=["Batch ID", "Batch Name"], tablefmt="simple_grid"
            )

def get_batches(token):
    headers2["token"] = token
    response2 = requests.get(
        "https://elearn.crwilladmin.com/api/v5/my-batch", headers=headers2, timeout = 30
    )
    response2.raise_for_status()
    resp2 = response2.text
    l = len(json.loads(resp2)["data"]["batchData"])
    for i in range(l):
      global batchidl, batchid, batchname
      batchname = json.loads(resp2)["data"]["batchData"][i]["batchName"]
      batchid = json.loads(resp2)["data"]["batchData"][i]["id"]
      batchidl[batchid] = batchname
    return batchidl

def get_class_detail(session, classid):
  try:
      response = session.get(f"https://elearn.crwilladmin.com/api/v5/class-detail/{classid}", timeout = 30)
      response.raise_for_status()
      lessonurl = response.json()["data"]["class_detail"]["lessonUrl"]
      return lessonurl
  except Exception as e:
      print(f"Error fetching class detail for classid={classid}: {str(e)}")
      return None

@bot.on_message(filters.command("cw"))
async def start_command(client, message):
    await message.reply_text(
        "Hello! I am the careerwill bot. Please provide login credentials"
    )

@bot.on_message(filters.text)
async def handle_auth(client, message):
   if not hasattr(message, 'login_step'):
        message.login_step = 0 #Create variable if it doesn't exist.

   if message.login_step == 0:
        await message.reply_text("Enter E-Mail/Phone:")
        message.login_step = 1
        return
   if message.login_step == 1:
        message.email = message.text
        await message.reply_text("Enter Password:")
        message.login_step = 2
        return
   if message.login_step == 2:
        message.password = message.text
        try:
           await message.reply_text("Attempting Login. Please wait")
           token = get_token(message.email, message.password)
           await message.reply_text("Login successful, getting your batches")
           table = print_batches(token)
           await message.reply_text(f"Here are your batches: \n{table}")
           message.token = token #Setting the token to the message object.
           batches = get_batches(token)
           keyboard = []
           for batch_id, batch_name in batches.items():
               keyboard.append([InlineKeyboardButton(f"{batch_name}", callback_data=str(batch_id))])
           reply_markup = InlineKeyboardMarkup(keyboard)
           await message.reply_text(f"Select a batch to get the classes", reply_markup=reply_markup)
        except Exception as e:
          await message.reply_text(f"There was an error {e}")
        message.login_step = 0 #reset the login step after completing.
        return


@bot.on_callback_query()
async def handle_batch_selection(client, callback_query):
    batch_id = callback_query.data
    await callback_query.answer(f"Fetching classes for batch: {batchidl[int(batch_id)]}")
    await callback_query.message.reply_text(f"Getting the classes of the selected batch {batchidl[int(batch_id)]}")
    token = callback_query.message.token

    headers2["token"] = token
    try:
      response = requests.get(
          f"https://elearn.crwilladmin.com/api/v5/my-batch-detail/{batch_id}", headers=headers2, timeout = 30
      )
      response.raise_for_status()
      resp = response.text
      topics = json.loads(resp)["data"]["topics"]
      with ThreadPoolExecutor(max_workers=5) as executor:
          future_lessons = [
               executor.submit(reqq, topic['id'], topic["topicName"], batch_id) for topic in topics
          ]
          results = [f.result() for f in future_lessons]
          lessonurls = [ url for url in results if url]
          if lessonurls:
                await callback_query.message.reply_text(f"Here are the lesson urls for batch: {batchidl[int(batch_id)]}\n{chr(10).join(lessonurls)}")
          else:
               await callback_query.message.reply_text(f"No lessons found for batch: {batchidl[int(batch_id)]}")
    except Exception as e:
      await callback_query.message.reply_text(f"An error has ocurred {e}")


def reqq(topicid, topicname, idd, max_retries=3, wait_time=30):
    with requests.Session() as session:
      session.headers.update(headers2)
      lessonurls = []
      try:
         response = session.get(
           f"https://elearn.crwilladmin.com/api/v5/topic-detail/{topicid}", timeout = 30
          )
         response.raise_for_status()
         classes = response.json()["data"]["classes"]

         with ThreadPoolExecutor(max_workers=5) as executor:
             future_class_detail = [
                executor.submit(get_class_detail, session, class_obj['id']) for class_obj in classes
             ]
             urls = [ f.result()  for f in future_class_detail if f.result()]
             lessonurls.extend(urls)
      except Exception as e:
           print(f"Error fetching classes for topicid={topicid}: {str(e)}")
      return lessonurls
bot.run()
