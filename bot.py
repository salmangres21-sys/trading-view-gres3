import os
import requests
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    print("⚠️ خطأ: لم يتم تعيين متغيرات البيئة TELEGRAM_TOKEN أو OPENAI_API_KEY")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload)
        print(f"رسالة مرسلة: {r.status_code} {r.text}")
    except Exception as e:
        print(f"خطأ أثناء إرسال الرسالة: {e}")

def ask_ai(user_message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a professional crypto trading assistant."},
            {"role": "user", "content": user_message}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"خطأ من OpenAI: {e}")
        return "⚠️ هناك خطأ في الاتصال بـ OpenAI."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    print(f"Incoming update: {data}")  # 👈 سيظهر كل تحديث من Telegram في Logs
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    if text:
        ai_reply = ask_ai(text)
        send_message(chat_id, ai_reply)
    return {"ok": True}

@app.route("/")
def home():
    return "Trading View GRES Bot Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
