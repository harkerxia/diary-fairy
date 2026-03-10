import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import config, DIRS
from core.database import MemoryDB
from handlers.commands import start_command, language_command
from handlers.messages import handle_message
from utils.helpers import get_scheduled_time

async def daily_reset_job(context):
    pass

if __name__ == '__main__':
    db_path = os.path.join(DIRS["memory"], "memory.db")
    db_instance = MemoryDB(db_path)

    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    app.bot_data["db"] = db_instance
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & (~filters.COMMAND), handle_message))
    
    env_config = config.get("environment_settings", {})
    tz_setting = env_config.get("timezone", "local")
    target_time = get_scheduled_time("03:00", tz_setting)
    
    app.job_queue.run_daily(daily_reset_job, time=target_time)
    
    app.run_polling()