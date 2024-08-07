register_message = {
    "type": "template",
    "altText": "This is a buttons template",
    "template": {
        "type": "buttons",
        # "thumbnailImageUrl": "https://example.com/bot/images/image.jpg",
        "imageAspectRatio": "rectangle",
        "imageSize": "cover",
        "imageBackgroundColor": "#FFFFFF",
        "title": "แก้ไขการแจ้งเตือน",
        "text": "กดที่ลิงค์ด้านล่าง",
        "actions": [
            {
                "type": "uri",
                "label": "ตั้งค่าการแจ้งเตือน",
                "uri": "https://mcare-line-webhook.vercel.app/register",
            }
        ],
    },
}

register_message_existed = {"type": "text", "text": "You have already registered."}

before_breakfast_message = {"type": "text", "text": "ได้เวลาทานยาก่อนอาหารเช้าแล้วจ้า 🍽"}
after_breakfast_message = {"type": "text", "text": "ได้เวลาทานยาหลังอาหารเช้าแล้วจ้า 🍽"}

before_lunch_message = {"type": "text", "text": "ได้เวลาทานยาก่อนอาหารกลางวันแล้วจ้า 🍽"}
after_lunch_message = {"type": "text", "text": "ได้เวลาทานยาหลังอาหารกลางวันแล้วจ้า 🍽"}

before_dinner_message = {"type": "text", "text": "ได้เวลาทานยาก่อนอาหารเย็นแล้วจ้า 🍽"}
after_dinner_message = {"type": "text", "text": "ได้เวลาทานยาหลังอาหารเย็นแล้วจ้า 🍽"}

before_sleep_message = {"type": "text", "text": "ได้เวลาทานยาก่อนนอนแล้วจ้า 🍽"}
after_sleep_message = {"type": "text", "text": "ได้เวลาทานยาหลังนอนแล้วจ้า 🍽"}
