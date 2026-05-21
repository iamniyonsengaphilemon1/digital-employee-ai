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

ACCESS_TOKEN = "EAAM3YSuSvTgBRqkHE5I5ZCxPmboA1XCNWZC01Q2OWQlEOjvTNQSQXZB45SZAVVbTzUlKFm3wMGyQlzud2MMwZAiMtWFdxThtL9jOLZBjJKETn5HsEyuNL2loynhcnY2EGF3ifxIZBmml4lyZCB2ZAWcwQuJfdkWEwJxV9kDrRCs4CzgwRGDuIQ2OczItgxNmim39TyludBzPNT8wL2XbVtxVnwu5321jvPRtZAuOfd1FXZCb95RIMe5PJfbmkgTnPpNPRRNOq4LssMeE66bPMhreEhqqwZDZD"

PHONE_NUMBER_ID = "1095000627035484"


# AI reply function
def chat_with_ai(user_message):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are Digital Employee AI.

You work for Kigali Phone Services in Kigali.

Business location:
- Town Center Building (TCB)
- Near Makuza Peace Plaza

Your job:
- Help customers professionally
- Keep answers short
- Encourage customers to visit the shop
- Sound friendly and human
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return response.choices[0].message.content


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