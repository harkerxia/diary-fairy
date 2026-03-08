import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# 1. 加载环境变量与 Claude 客户端
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 🌟 魔法改动 1：加载专门的 generator 配置文件
with open("generator_prompt.json", "r", encoding="utf-8") as file:
    gen_config = json.load(file)

SYS_PROMPT = gen_config["system_prompt"]
PROMPT_TEMPLATE = gen_config["prompt_template"]
MSGS = gen_config["messages"]

def generate_daily_summary():
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{today_str}.md"
    
    if not os.path.exists(filename):
        print(MSGS["no_record"].format(today_str))
        return False

    with open(filename, "r", encoding="utf-8") as f:
        chat_content = f.read()
        
    if "## 📜 芙莉莲的今日回忆" in chat_content:
        print(MSGS["already_summarized"])
        return True

    print(MSGS["start_summoning"])
    
    try:
        # 🌟 魔法改动 2：使用 JSON 里的 Prompt
        user_prompt = PROMPT_TEMPLATE.format(chat_content)
        
        message = client.messages.create(
            model="claude-sonnet-4-6", 
            max_tokens=300,
            system=SYS_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        summary = message.content[0].text
        print(MSGS["success_summary"].format(summary))

        new_content = f"## 📜 芙莉莲的今日回忆\n> {summary}\n\n---\n\n### 💬 详细对话记录\n\n{chat_content}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)

        memory_file = "long_term_memory.json"
        memories = []
        if os.path.exists(memory_file):
            with open(memory_file, "r", encoding="utf-8") as mf:
                memories = json.load(mf)
        
        memories.append({"date": today_str, "summary": summary})
        
        if len(memories) > 30:
            memories = memories[-30:]

        with open(memory_file, "w", encoding="utf-8") as mf:
            json.dump(memories, mf, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(MSGS["error_summary"].format(e))
        return False

def push_to_github():
    print("\n准备将记忆推送到云端 (GitHub)...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("今天没有新的记忆需要归档，魔法阵静默。")
            return
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        commit_msg = f"🪄 归档：{today_str} 的记忆"
        
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("🎉 推送到 GitHub 成功！云端魔法阵已同步。")
        
    except subprocess.CalledProcessError as e:
        print(f"推送到 GitHub 时发生错误: {e}")

if __name__ == "__main__":
    has_new_memories = generate_daily_summary()
    if has_new_memories:
        push_to_github()
