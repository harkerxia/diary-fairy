import os
import anthropic
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from core.memory_builder import get_system_prompt
from utils.helpers import encode_image, format_log_entry, flush_logs_to_file
from config import config, IMAGE_PROMPT, DIRS

client = anthropic.Anthropic(api_key=os.getenv("LLM_API_KEY"))

def should_search(text):
    trigger_words = ["以前", "记得", "上次", "qmd", "总结", "之前", "什么来着", "架构", "计划"]
    return any(word in text for word in trigger_words)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    retrieved_docs = ""
    if should_search(user_text):
        retrieved_docs = db.search_memory(user_id, user_text, limit=3)
    
    if not user_data["messages"] or user_data["messages"][0].get("role") != "system":
        user_data["messages"].insert(0, {"role": "system", "content": ""})
        
    user_data["messages"][0]["content"] = get_system_prompt(db, user_id, retrieved_docs)

    try:
        system_content = user_data["messages"][0]["content"]
        chat_history = user_data["messages"][1:]
        
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_content,
            messages=chat_history
        )
        reply_text = response.content[0].text
    except Exception as e:
        reply_text = f"API 调用出错: {str(e)}"
    
    await update.message.reply_text(reply_text)