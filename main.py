import os
import json
from datetime import datetime  # 🌟 魔法改动 1：引入时间魔法，用来获取今天的日期
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

SYSTEM_PROMPT = config["system_prompt"]
MESSAGES = config["messages"]

chat_history = {}

# 🌟 魔法改动 2：新增一个专门用来写日记的函数
def write_to_diary(role, text):
    # 获取当天的日期和时间
    today_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")
    filename = f"{today_str}.md" # 比如生成 2026-03-07.md
    
    # 用 "a" (append) 模式打开文件。如果文件不存在会自动创建，如果存在就会追加在末尾
    with open(filename, "a", encoding="utf-8") as f:
        if role == "user":
            f.write(f"**👤 主人** ({time_str}):\n{text}\n\n")
        elif role == "assistant":
            f.write(f"**🧝‍♀️ 芙莉莲** ({time_str}):\n{text}\n\n---\n\n")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    print(MESSAGES["receive_log"].format(user_text)) 
    
    # 🌟 魔法改动 3：把主人的话写进本地日记本
    write_to_diary("user", user_text)
    
    if user_id not in chat_history:
        chat_history[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
    chat_history[user_id].append({"role": "user", "content": user_text})
    
    if len(chat_history[user_id]) > 21:
        chat_history[user_id] = [chat_history[user_id][0]] + chat_history[user_id][-20:]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history[user_id]
        )
        
        reply_text = completion.choices[0].message.content
        chat_history[user_id].append({"role": "assistant", "content": reply_text})
        
        # 🌟 魔法改动 4：把芙莉莲的回答也写进本地日记本
        write_to_diary("assistant", reply_text)
        
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        error_msg = MESSAGES["error"].format(e)
        await update.message.reply_text(error_msg)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print(MESSAGES["startup"])
    app.run_polling()
