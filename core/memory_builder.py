import os
from datetime import datetime
from config import BASE_SYSTEM_PROMPT, DIRS

def get_system_prompt(db, user_id, retrieved_docs=""):
    prompt = BASE_SYSTEM_PROMPT
    
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
     
    if retrieved_docs:
        prompt += f"{retrieved_docs}\n\n"
                       
    user_data = db.get_user(user_id)
    
    if user_data["mega_summary"]:
        prompt += "\n### Today's Previous Memories:\n"
        for s in user_data["mega_summary"]:
            prompt += f"- {s}\n"
            
    if user_data["daily_summary"]:
        prompt += "\n### Today's Recent Memories:\n"
        for s in user_data["daily_summary"]:
            prompt += f"- {s}\n"
            
    prompt += "\nCurrent date and time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    return prompt.strip()
