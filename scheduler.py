import sys
import time
import json
import subprocess
import schedule
from datetime import datetime

with open("settings/scheduler_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SCHEDULER_CONF = config["scheduler_config"]
REPORTS = config["status_reports"]

def run_script(script_name):
    print(REPORTS["executing"].format(task_id=script_name))
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(REPORTS["success"].format(task_id=script_name))
    except subprocess.CalledProcessError as e:
        print(REPORTS["error"].format(task_id=script_name, error=str(e)))

def job_summarizer():
    run_script("summarizer.py")

def job_archiver():
    run_script("archiver.py")

if __name__ == "__main__":
    print(REPORTS["startup"].format(
        summarizer_time=SCHEDULER_CONF["summarizer_execution_time"],
        archiver_time=SCHEDULER_CONF["archiver_execution_time"]
    ))
    
    schedule.every().day.at(SCHEDULER_CONF["summarizer_execution_time"]).do(job_summarizer)
    schedule.every().day.at(SCHEDULER_CONF["archiver_execution_time"]).do(job_archiver)
    
    while True:
        schedule.run_pending()
        time.sleep(30)
        