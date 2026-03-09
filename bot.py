import io
import os
import json
import base64
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "configs", "bot_config.json")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts", "bot_prompts")

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = json.load(file)

def load_prompt(filename):
    path = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

BASE_SYSTEM_PROMPT = load_prompt("system_prompt.md") + "\n\n"
IMAGE_PROMPT = load_prompt("image_prompt.md") + "\n\n"
MINI_SUMMARY_PROMPT = load_prompt("mini_summary_prompt.md") + "\n\n"
MEGA_SUMMARY_PROMPT = load_prompt("mega_summary_prompt.md") + "\n\n"
    
MEMORY_SYSTEM = config["memory_system"]
LOGS = config["logs"]
MODEL = config["model"]
PARAMS = config["parameters"]
BOT_NAME = config["bot_name"]
USER_NAME = config["user_name"]
CHAT_FORMAT = config["chat"]

chat_history = {}

DIRS = {
    "logs": "archives/memory/logs",
    "memory": "archives/memory"
}

for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

def get_system_prompt(user_id=None):
    prompt = BASE_SYSTEM_PROMPT + "\n\n"
    
    state_files = {
        "core": os.path.join(DIRS["memory"], "core.md"),
        "yearly": os.path.join(DIRS["memory"], "recent_years.md"),
        "monthly": os.path.join(DIRS["memory"], "recent_months.md"),
        "weekly": os.path.join(DIRS["memory"], "recent_weeks.md")
    }
    
    for level, path in state_files.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    prompt += f"### {level.capitalize()} Memory:\n{content}\n\n"
        
    if user_id and chat_history.get(user_id):
        history = chat_history[user_id]
        
        if history.get("mega_summary"):
            prompt += "\n### Today's Previous Memories ():\n"
            for s in history["daily_previous_summary"]:
                prompt += f"- {s}\n"
                
        if history.get("daily_summary"):
            prompt += "\n### Today's Recent Memories ():\n"
            for s in history["daily_recent_summary"]:
                prompt += f"- {s}\n"
    
    prompt += "\nCurrent date and time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    return prompt.strip()

def buffer_log(user_id, role, text):
    time_min = datetime.now().strftime("%H:%M") 
    
    if role == "user":
        name = USER_NAME
        entry = f"[{time_min}] **{name}**: {text}\n"
    elif role == "assistant":
        name = BOT_NAME
        entry = f"[{time_min}] **{name}**: {text}\n\n---\n\n"
    else:
        return
        
    chat_history[user_id]["log_buffer"].append(entry)

def flush_logs(user_id, today_str):
    if user_id in chat_history and chat_history[user_id]["log_buffer"]:
        filename = os.path.join(DIRS["logs"], f"{today_str}.md")
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, "a", encoding="utf-8") as f:
            for log_entry in chat_history[user_id]["log_buffer"]:
                f.write(log_entry)
        
        chat_history[user_id]["log_buffer"] = []
        
def encode_image(image_path, max_size=512):
    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        img.thumbnail((max_size, max_size))
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
async def daily_reset_job(context: ContextTypes.DEFAULT_TYPE):
    today_str = datetime.now().strftime("%Y-%m-%d")
    for user_id in chat_history.keys():
        flush_logs(user_id, today_str)
        old_messages = chat_history[user_id]["messages"]
        user_assistant_msgs = [msg for msg in old_messages if msg["role"] != "system"]
        
        recent_20 = user_assistant_msgs[-20:] if len(user_assistant_msgs) > 20 else user_assistant_msgs
        
        chat_history[user_id]["messages"] = [{"role": "system", "content": get_system_prompt()}] + recent_20

async def generate_mini_summary(user_id):
    recent_msgs = [m for m in chat_history[user_id]["messages"] if m["role"] != "system"][-20:]
    summary_instruction = MINI_SUMMARY_PROMPT
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=recent_msgs + [{"role": "user", "content": summary_instruction}],
            temperature=0.3
        )
        summary = response.choices[0].message.content
        chat_history[user_id]["daily_summary"].append(summary)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [MEMORY] New mini-summary: {summary}")
    except Exception as e:
        print(f"Summary Error: {e}")
        
async def generate_mega_summary(user_id):
    if len(chat_history[user_id]["daily_summary"]) < 10:
        return

    summaries_to_combine = chat_history[user_id]["daily_summary"][-10:]
    text_to_process = "\n".join(summaries_to_combine)

    instruction = MEGA_SUMMARY_PROMPT
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"{instruction}\n\n内容如下：\n{text_to_process}"}],
            temperature=0.3
        )
        mega_summary = response.choices[0].message.content
        
        chat_history[user_id]["mega_summary"].append(mega_summary)
        chat_history[user_id]["daily_summary"] = chat_history[user_id]["daily_summary"][:-10]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [MEGA-MEMORY] 10 mini-summaries collapsed into 1 mega-summary.")
    except Exception as e:
        print(f"Mega Summary Error: {e}")
        
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text or update.message.caption or ""
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    log_time = now.strftime("%Y-%m-%d %H:%M:%S") 
    
    user_log = CHAT_FORMAT.format(user_name=USER_NAME, text=user_text)
    print(f"[{log_time}] {user_log}")
    
    if user_id not in chat_history:
        chat_history[user_id] = {
            "messages": [{"role": "system", "content": get_system_prompt(user_id)}],
            "log_buffer": [],
            "daily_summary": [],
            "mega_summary": [],
            "msg_cnt": 0
        }

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        path = f"{user_id}_{now.timestamp()}.jpg"
        await photo_file.download_to_drive(path)
        base64_img = encode_image(path)
        content_list = [
            {"type": "text", "text": IMAGE_PROMPT + user_text if user_text else IMAGE_PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "low"}}
        ]
        os.remove(path)
        buffer_log(user_id, "user", f"[Image] {user_text}") 
        chat_history[user_id]["messages"].append({"role": "user", "content": content_list})
    else:
        buffer_log(user_id, "user", user_text)
        chat_history[user_id]["messages"].append({"role": "user", "content": user_text})

    try:
        chat_history[user_id]["messages"][0]["content"] = get_system_prompt(user_id)

        completion = client.chat.completions.create(
            model=MODEL,
            messages=chat_history[user_id]["messages"],
            temperature=PARAMS["temperature"],
            presence_penalty=PARAMS["presence_penalty"],
            frequency_penalty=PARAMS["frequency_penalty"]
        )
        
        now = datetime.now()
        log_time = now.strftime("%Y-%m-%d %H:%M:%S")
        reply_text = completion.choices[0].message.content
        
        bot_log = CHAT_FORMAT.format(user_name=BOT_NAME, text=reply_text)
        print(f"[{log_time}] {bot_log}")
        print(f"[{log_time}] [{MODEL}] Usage: Input={completion.usage.prompt_tokens} | Output={completion.usage.completion_tokens} | Total={completion.usage.total_tokens}\n" + "-"*50)
        
        chat_history[user_id]["messages"].append({"role": "assistant", "content": reply_text})
        buffer_log(user_id, "assistant", reply_text)
        await update.message.reply_text(reply_text)

        chat_history[user_id]["msg_cnt"] += 2 
        if chat_history[user_id]["msg_cnt"] >= 20:
            await generate_mini_summary(user_id)
            chat_history[user_id]["msg_cnt"] = 0
            
            if len(chat_history[user_id]["daily_summary"]) >= 10:
                await generate_mega_summary(user_id)

            preserved_system = chat_history[user_id]["messages"][0]
            recent_context = chat_history[user_id]["messages"][-20:]
            chat_history[user_id]["messages"] = [preserved_system] + recent_context

        if len(chat_history[user_id]["log_buffer"]) >= 20:
            flush_logs(user_id, today_str)

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"[{log_time}] [Error]: {error_msg}")
        await update.message.reply_text("抱歉，我刚才走神了...")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), handle_message))
    local_tz = datetime.now().astimezone().tzinfo
    target_time = time(hour=3, minute=0, second=0, tzinfo=local_tz) 
    app.job_queue.run_daily(daily_reset_job, time=target_time)
    print(LOGS["start"].format(model=MODEL, bot_name=BOT_NAME))
    app.run_polling()