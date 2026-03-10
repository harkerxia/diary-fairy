import io
import os
import base64
import zoneinfo
from PIL import Image
from datetime import datetime, time

def encode_image(image_path, max_size=512):
    with Image.open(image_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((max_size, max_size))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_scheduled_time(time_str, tz_str):
    if tz_str.lower() == "local":
        run_tz = datetime.now().astimezone().tzinfo
    else:
        try:
            run_tz = zoneinfo.ZoneInfo(tz_str)
        except zoneinfo.ZoneInfoNotFoundError:
            run_tz = datetime.now().astimezone().tzinfo
            
    h, m = map(int, time_str.split(":"))
    return time(hour=h, minute=m, second=0, tzinfo=run_tz)

def format_log_entry(role, text, bot_name, user_name):
    time_min = datetime.now().strftime("%H:%M") 
    if role == "user":
        return f"[{time_min}] **{user_name}**: {text}\n"
    elif role == "assistant":
        return f"[{time_min}] **{bot_name}**: {text}\n\n---\n\n"
    return ""

def flush_logs_to_file(log_buffer, logs_dir, today_str):
    if not log_buffer:
        return []
        
    filename = os.path.join(logs_dir, f"{today_str}.md")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "a", encoding="utf-8") as f:
        for log_entry in log_buffer:
            f.write(log_entry)
            
    return []
