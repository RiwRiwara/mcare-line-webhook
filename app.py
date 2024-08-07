from flask import Flask, request, jsonify, render_template, redirect
import requests
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from messages import register_message, register_message_existed, before_breakfast_message, after_breakfast_message, before_lunch_message, after_lunch_message, before_dinner_message, after_dinner_message, before_sleep_message
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import time
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

def static_file_exists(filename):
    filepath = os.path.join(app.static_folder, filename)
    return os.path.exists(filepath)
app.jinja_env.globals['static_file_exists'] = static_file_exists


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
        message_template = register_message
        message_template["template"]["actions"][0]["uri"] = f"https://mcare-line-webhook.vercel.app/register?user_id={user_id}"
        send_message(user_id, message_template)
    else:
        if not is_registered(user_id):
            users_collection.insert_one({"user_id": user_id})
            message_template = register_message
            message_template["template"]["actions"][0]["uri"] = f"https://mcare-line-webhook.vercel.app/register?user_id={user_id}"
            send_message(user_id, message_template)


def is_registered(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user is not None

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/register", methods=["GET"])
def register_page():
    user_data = users_collection.find_one({"user_id": request.args.get("user_id")})
    if not user_data:
        return "ผิดพลาด "
    success = request.args.get("success")
    current_time = time.strftime("%H:%M:%S", time.localtime())
    return render_template('register.html', user_data=user_data, success=success, current_time=current_time)

@app.route("/setting", methods=["POST"])
def setting_form():
    user_id = request.form.get('user_id')
    email = request.form.get('email')
    notifications = {
        "before_breakfast": False,
        "after_breakfast": False,
        "before_lunch": False,
        "after_lunch": False,
        "before_dinner": False,
        "after_dinner": False,
        "before_sleep": False
    }
    
    selected_notifications = request.form.getlist('notifications')
    for notification in selected_notifications:
        if notification in notifications:
            notifications[notification] = True

    update_data = {
        "email": email,
        **notifications  
    }

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": update_data},
        upsert=True
    )

    success_message = "บันทึกข้อมูลสำเร็จ"
    return redirect(f"/register?user_id={user_id}&success={success_message}", code=302)

    

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json

    if body["events"][0]["type"] == "message":
        message = body["events"][0]["message"]["text"]
        if message == "ลงทะเบียน":
            user_id = body["events"][0]["source"]["userId"]
            register(user_id)
    else:
        print(body)

    return jsonify({"status": "ok"}), 200


def scheduled_task(message):
    users = users_collection.find()
    for user in users:
        user_id = user["user_id"]
        
        if user["before_breakfast"]:
            if message == before_breakfast_message:
                send_message(user_id, message)
        if user["after_breakfast"]:
            if message == after_breakfast_message:
                send_message(user_id, message)
        if user["before_lunch"]:
            if message == before_lunch_message:
                send_message(user_id, message)
        if user["after_lunch"]:
            if message == after_lunch_message:
                send_message(user_id, message)
        if user["before_dinner"]:
            if message == before_dinner_message:
                send_message(user_id, message)
        if user["after_dinner"]:
            if message == after_dinner_message:
                send_message(user_id, message)
        if user["before_sleep"]:
            if message == before_sleep_message:
                send_message(user_id, message)

@app.route("/before_breakfast", methods=["GET"])
def before_breakfast():
    scheduled_task(before_breakfast_message)
    return "OK", 200

@app.route("/after_breakfast", methods=["GET"])
def after_breakfast():
    scheduled_task(after_breakfast_message)
    return "OK", 200

@app.route("/before_lunch", methods=["GET"])
def before_lunch():
    scheduled_task(before_lunch_message)
    return "OK", 200

@app.route("/after_lunch", methods=["GET"])
def after_lunch():
    scheduled_task(after_lunch_message)
    return "OK", 200

@app.route("/before_dinner", methods=["GET"])
def before_dinner():
    scheduled_task(before_dinner_message)
    return "OK", 200

@app.route("/after_dinner", methods=["GET"])
def after_dinner():
    scheduled_task(after_dinner_message)
    return "OK", 200

@app.route("/before_sleep", methods=["GET"])
def before_sleep():
    scheduled_task(before_sleep_message)
    return "OK", 200
    

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
        trigger=CronTrigger(hour=10, minute=5),
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
        trigger=CronTrigger(hour=2, minute=58),
        args=[before_sleep_message],
        id="before_bed",
        name="Before bed reminder",
        replace_existing=True,
    )

    atexit.register(lambda: scheduler.shutdown())

    app.run()
