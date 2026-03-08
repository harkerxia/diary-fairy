import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

BASE_SYSTEM_PROMPT = config["system_prompt"]
MEMORY_SYSTEM = config["memory_system"]
LOGS = config["logs"]
MODEL = config["model"]
PARAMS = config["parameters"]
BOT_NAME = config["bot_name"]
USER_NAME = config["user_name"]

chat_history = {}

DIRS = {
    "logs": "archives/logs",
    "daily": "archives/daily",
    "weekly": "archives/weekly",
    "monthly": "archives/monthly",
    "yearly": "archives/yearly"
}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

def get_latest_file(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    if not files:
        return None
    files.sort() 
    return os.path.join(folder_path, files[-1])

def get_system_prompt():
    prompt = BASE_SYSTEM_PROMPT + "\n\n"
    templates = MEMORY_SYSTEM["inject_templates"]
    
    time_order = ["yearly", "monthly", "weekly", "daily"]
    
    for time_level in time_order:
        if time_level in templates:
            folder_path = DIRS[time_level]
            latest_file = get_latest_file(folder_path)
            
            if latest_file:
                with open(latest_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        prompt += templates[time_level].format(**{f"{time_level}_summary": content}) + "\n\n"
                        
    return prompt.strip()

def write_to_diary(role, text, today_str, time_str):
    filename = os.path.join(DIRS["logs"], f"{today_str}.md")
    with open(filename, "a", encoding="utf-8") as f:
        if role == "user":
            f.write(f"**{USER_NAME}** ({time_str}):\n{text}\n\n")
        elif role == "assistant":
            f.write(f"**{BOT_NAME}** ({time_str}):\n{text}\n\n---\n\n")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    print(LOGS["chat"].format(user_name=USER_NAME, text=user_text))

    if user_id not in chat_history or chat_history[user_id].get("date") != today_str:
        chat_history[user_id] = {
            "date": today_str,
            "messages": [{"role": "system", "content": get_system_prompt()}]
        }

    write_to_diary("user", user_text, today_str, time_str)
    chat_history[user_id]["messages"].append({"role": "user", "content": user_text})

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=chat_history[user_id]["messages"],
            temperature=PARAMS["temperature"],
            presence_penalty=PARAMS["presence_penalty"],
            frequency_penalty=PARAMS["frequency_penalty"]
        )

        reply_text = completion.choices[0].message.content
        chat_history[user_id]["messages"].append({"role": "assistant", "content": reply_text})

        write_to_diary("assistant", reply_text, today_str, time_str)

        await update.message.reply_text(reply_text)

    except Exception as e:
        error_msg = LOGS["error"].format(error=str(e))
        await update.message.reply_text(error_msg)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print(LOGS["start"].format(model=MODEL, bot_name=BOT_NAME))
    app.run_polling()
