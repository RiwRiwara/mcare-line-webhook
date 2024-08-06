from flask import Flask, request, jsonify
import requests
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from messages import register_message, register_message_existed, before_breakfast_message, after_breakfast_message, before_lunch_message, after_lunch_message, before_dinner_message, after_dinner_message, before_sleep_message
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["mcare"]
users_collection = db["user"]


def send_message(user_id, message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
    }
    payload = {"to": user_id, "messages": [message]}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message: {response.status_code}")
        print(response.json())


def register(user_id):
    user = users_collection.find_one({"user_id": user_id})

    if user:
        send_message(user_id, register_message_existed)
    else:
        users_collection.insert_one({"user_id": user_id})
        send_message(user_id, register_message)


def is_registered(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user is not None


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json

    if body["events"][0]["type"] == "message":
        message = body["events"][0]["message"]["text"]
        if message == "ลงทะเบียน":
            user_id = body["events"][0]["source"]["userId"]
            register(user_id)

    return jsonify({"status": "ok"}), 200


def scheduled_task(message):
    users = users_collection.find()
    for user in users:
        user_id = user["user_id"]
        send_message(user_id, message)


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()

    # Breakfast reminders
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=7, minute=30),
        args=[before_breakfast_message],
        id="breakfast_before",
        name="Breakfast before meal reminder",
        replace_existing=True,
    )
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=8, minute=0),
        args=[after_breakfast_message],
        id="breakfast_after",
        name="Breakfast after meal reminder",
        replace_existing=True,
    )

    # Lunch reminders
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=11, minute=30),
        args=[before_lunch_message],
        id="lunch_before",
        name="Lunch before meal reminder",
        replace_existing=True,
    )
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=12, minute=0),
        args=[after_lunch_message],
        id="lunch_after",
        name="Lunch after meal reminder",
        replace_existing=True,
    )

    # Dinner reminders
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=16, minute=30),
        args=[before_dinner_message],
        id="dinner_before",
        name="Dinner before meal reminder",
        replace_existing=True,
    )
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=17, minute=0),
        args=[after_dinner_message],
        id="dinner_after",
        name="Dinner after meal reminder",
        replace_existing=True,
    )

    # Before bed reminder
    scheduler.add_job(
        func=scheduled_task,
        trigger=CronTrigger(hour=20, minute=0),
        args=[before_sleep_message],
        id="before_bed",
        name="Before bed reminder",
        replace_existing=True,
    )

    atexit.register(lambda: scheduler.shutdown())

    app.run(port=8000)
