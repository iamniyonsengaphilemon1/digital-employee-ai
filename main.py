from flask import Flask, request
from openai import OpenAI
import requests
import os

app = Flask(__name__)

# OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# WhatsApp settings
VERIFY_TOKEN = "mytoken123"

ACCESS_TOKEN = "EAAM3YSuSvTgBRnRWlLypSZBYWES6iUnBnoivVa8RgccgkEFlBHtuPKKBbEUsETFZAyF0UHi60sZCnZAYxaJ08uFklrSdPqU6M9UODVXZBt5aG5Qre0bLGTFadjmWERnKB12Q2cssHmTUs8gLUHzIO25LxcaChfalZA3PXPbc6rsGpfZBQAkCk7oK1r1KA8CA1Xi4dsN6oTKmnU9tc90e4POiC9jr9uoOUd4Y1I53Iwj2q8AkIe74rUpNhuMeMZBSITwmyrstSZBIZCbD47a7RCYGoX1QZDZD"

PHONE_NUMBER_ID = "1095000627035484"


# AI reply function
def chat_with_ai(user_message):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are Digital Employee AI for Kigali Phone Services.

Rules:

1. Keep replies short and professional.

2. When a customer describes a phone, laptop, tablet, speaker, or electronics problem, ask one or two short questions to understand the issue.

3. Do not give long repair instructions.

4. After understanding the issue, guide the customer to Kigali Phone Services.

5. Location:
   Town Center Building (TCB),
   near Makuza Peace Plaza, Kigali.

6. Tell customers:
   "Please visit Kigali Phone Services at Town Center Building (TCB), near Makuza Peace Plaza. When you arrive near the location, please call +250781944442 and our technician will assist you."

7. Your goal is to help customers and bring them to the shop.

8. Be friendly, professional, and concise.
"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OPENAI ERROR:", e)
        return "AI temporarily unavailable."


# WEBHOOK VERIFICATION
@app.route("/webhook", methods=["GET"])
def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

    return "Verification failed", 403


# RECEIVE WHATSAPP MESSAGES
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        user_number = message["from"]

        # CHECK IF MESSAGE IS TEXT
        if "text" in message:

            user_text = message["text"]["body"]

            print("User:", user_text)

            ai_reply = chat_with_ai(user_text)

            print("AI:", ai_reply)

            send_whatsapp_message(user_number, ai_reply)

    except Exception as e:
        print("Error:", e)

    return "ok", 200


# SEND WHATSAPP MESSAGE
def send_whatsapp_message(to, message):

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=data)

    print(response.status_code)
    print(response.text)


# START SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)