from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("系统初始化完成。数据库已连接。")

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    db = context.bot_data["db"]
    
    user_data = db.get_user(user_id)
    new_lang = "en" if user_data["language"] == "zh" else "zh"
    
    db.update_user(user_id, language=new_lang)
    await update.message.reply_text(f"Language switched to: {new_lang}")
    