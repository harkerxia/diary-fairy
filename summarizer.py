import os
import json
import time
import schedule
import anthropic
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("config/summarizer_config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

API_CONF = config["api_config"]
MODEL = API_CONF["model"]
TEMP = API_CONF["parameters"]["temperature"]
MAX_TOKENS = API_CONF["parameters"]["max_tokens"]

USER_NAME = config["entities"]["user_name"]
BOT_NAME = config["entities"]["bot_name"]

PATHS = config["storage_paths"]
LOGS_DIR = PATHS["input_logs"]
ARCHIVES = PATHS["output_archives"]

PROMPTS = {
    k: v.format(user_name=USER_NAME, bot_name=BOT_NAME) 
    for k, v in config["prompts"].items()
}

for path in ARCHIVES.values():
    os.makedirs(path, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def call_sonnet(system_prompt, user_text):
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMP,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Claude Summarize Error: {e}")
        return ""

def read_files_in_range(folder, prefix, start_date, end_date):
    combined_text = ""
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime(prefix)
        filename = os.path.join(folder, f"{date_str}.md")
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                combined_text += f"[{date_str}]:\n{f.read().strip()}\n\n"
        current_date += timedelta(days=1)
    return combined_text

def execute_cascade_summary():
    now = datetime.now()
    target_date = now - timedelta(days=1)
    target_str = target_date.strftime("%Y-%m-%d")
    
    log_file = os.path.join(LOGS_DIR, f"{target_str}.md")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            daily_raw = f.read().strip()
        if daily_raw:
            daily_summary = call_sonnet(PROMPTS["daily"], daily_raw)
            if daily_summary:
                with open(os.path.join(ARCHIVES["daily"], f"{target_str}_daily.md"), "w", encoding="utf-8") as f:
                    f.write(daily_summary)
                print(f"[{target_str}] Daily summary created via Sonnet.")

    if target_date.weekday() == 6:
        start_of_week = target_date - timedelta(days=6)
        weekly_raw = read_files_in_range(ARCHIVES["daily"], "%Y-%m-%d_daily", start_of_week, target_date)
        if weekly_raw:
            week_str = target_date.strftime("%Y-W%V")
            weekly_summary = call_sonnet(PROMPTS["weekly"], weekly_raw)
            if weekly_summary:
                with open(os.path.join(ARCHIVES["weekly"], f"{week_str}_weekly.md"), "w", encoding="utf-8") as f:
                    f.write(weekly_summary)
                print(f"[{week_str}] Weekly summary created via Sonnet.")

    if now.day == 1:
        start_of_month = target_date.replace(day=1)
        monthly_raw = read_files_in_range(ARCHIVES["daily"], "%Y-%m-%d_daily", start_of_month, target_date)
        if monthly_raw:
            month_str = target_date.strftime("%Y-%m")
            monthly_summary = call_sonnet(PROMPTS["monthly"], monthly_raw)
            if monthly_summary:
                with open(os.path.join(ARCHIVES["monthly"], f"{month_str}_monthly.md"), "w", encoding="utf-8") as f:
                    f.write(monthly_summary)
                print(f"[{month_str}] Monthly summary created via Sonnet.")

    if now.month == 1 and now.day == 1:
        year_str = target_date.strftime("%Y")
        yearly_raw = ""
        for month in range(1, 13):
            m_str = f"{year_str}-{month:02d}"
            filename = os.path.join(ARCHIVES["monthly"], f"{m_str}_monthly.md")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    yearly_raw += f"[{m_str}]:\n{f.read().strip()}\n\n"
        
        if yearly_raw:
            yearly_summary = call_sonnet(PROMPTS["yearly"], yearly_raw)
            if yearly_summary:
                with open(os.path.join(ARCHIVES["yearly"], f"{year_str}_yearly.md"), "w", encoding="utf-8") as f:
                    f.write(yearly_summary)
                print(f"[{year_str}] Yearly summary created via Sonnet.")

if __name__ == "__main__":
    run_time = config["scheduler"]["run_time"]
    schedule.every().day.at(run_time).do(execute_cascade_summary)
    print(f"Summarizer scheduler started. Running daily at {run_time} using Claude Sonnet 4.6.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
