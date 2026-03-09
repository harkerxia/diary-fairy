# 📖 Diary-Frieren: AI Companion & Lifelog Archival System

> **"Weaving a lifetime of memory wealth through seamless companionship, especially for those who struggle to keep a journal."**

Diary-Frieren is a highly engineered, lightweight personal AI companion system that balances warmth and rationality. It is not just a chatbot, but a fully automated digital archive of your life cycle. 

Through daily, fragmented conversations, the system silently extracts multi-dimensional facets of your life based on your custom configurations—whether it's emotional fluctuations, interpersonal dynamics, or goal progression. In the background, it weaves these fragments into a beautifully formatted, first-person daily journal, safely archived in your private cloud.

## ✨ Core Features

* 🧠 **Dual-AI Engine**: Utilizes OpenAI for the frontend (fast response times, handling high-frequency emotional companionship) and Anthropic Claude Sonnet 4.6 for the backend (strict logic, executing late-night long-text memory compression). This maximizes the strengths of both models while optimizing API costs.
* 🛤️ **Dual-Track Memory Architecture**:
    * **Human Diary (First-Person Lifelog)**: Synthesizes your fragmented daily chats into beautifully formatted Markdown journals written entirely from **your perspective ("I")**. It perfectly mimics your voice, turning casual conversations into a cohesive personal narrative.
    * **Bot Memory**: Extracts dry, high-density objective facts and preference tags to inject into the AI's long-term subconsciousness.
* 🧩 **Configurable Life-Tracking Dimensions**: Not just an emotional tracker! By simply tweaking the system prompts, you can instruct the backend to silently extract specific life metrics—such as **interpersonal dynamics (Personal CRM), goal progression, or habit streaks**—weaving these custom dimensions seamlessly into your nightly journal.
* 🌊 **Hierarchical Summarization**: The ultimate solution for managing LLM token limits and optimizing context retention. Triggered automatically at midnight, it efficiently filters and compresses data from the bottom up—"Daily -> Weekly -> Monthly -> Yearly"—ensuring deep, long-term memory without exorbitant token costs.
* 🛡️ **Open Source Code, Private Data (Nested Repositories)**: Drops heavy databases in favor of local, pure-text Markdown storage. The outer code repository can be safely open-sourced, while the `archives` folder acts as an independent Git repository. An automated script pushes the vault daily to your private GitHub repository, achieving physical-level privacy isolation. 
* ⚙️ **Geek-Level Config-Driven Design**: All system prompts, model parameters, cron times, and directory paths are extracted into JSON files. The core code remains absolutely clean with zero hardcoding.

## 🛠️ Tech Stack

* **Language**: Python 3.12+
* **LLM APIs**: OpenAI API (Chat), Anthropic API (Summarize)
* **Version Control & Storage**: Git, GitHub (Automated Archiving)
* **Task Scheduling**: `schedule` library, `subprocess`

## 📂 Architecture

```text
📁 diary-frieren/                 <-- Public Repository (Code is fully open)
├── 📁 archives/                <-- Private Repository (Independent Git for private data)
│   ├── 📁 diary/               <-- Generated beautifully formatted Markdown journals
│   └── 📁 memory/              <-- Extracted facts and preferences for Bot's subconscious
├── 📁 configs/                 <-- Configuration Hub
│   ├── 📄 archiver_config.json 
│   ├── 📄 bot_config.json          
│   ├── 📄 scheduler_config.json
│   └── 📄 summarizer_config.json
├── 📁 venv/                    <-- Python virtual environment
├── 📄 .env                     <-- Environment variables (Ignored by Git)
├── 📄 .gitignore               <-- Invisibility cloak (Ignores .env, venv/, and archives/)
├── 📄 archiver.py              <-- Automated Git backup worker
├── 📄 bot.py                   <-- Core interaction brain
├── 📄 README.md                <-- Project documentation
├── 📄 requirements.txt         <-- Python dependencies
├── 📄 scheduler.py             <-- Global time manager
└── 📄 summarizer.py            <-- Memory compression engine
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/harkerxia/diary-frieren.git
cd diary-frieren
```

### 2. Setup Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
*(Ensure your `requirements.txt` includes: `openai`, `anthropic`, `python-dotenv`, `schedule`)*

### 3. Initialize the Privacy Vault (Archives)
Create an independent private repository to store your data:
```bash
mkdir archives
cd archives
git init
git remote add origin https://github.com/YourName/Your-Private-Archive-Repo.git
# Note: Manually push once to save your Git credentials or test your SSH Key
cd ..
```

### 4. Environment Variables & Configuration
Create a `.env` file in the project root and add your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here
```
Next, fine-tune the JSON configuration files in the `configs/` directory according to your preferences (e.g., bot name, scheduled task times).

### 5. Start the Services
Use the global time manager to run all background tasks seamlessly:
```bash
python scheduler.py
```
*(For Linux servers, it is recommended to run this in the background using `tmux` or `nohup`)*

## 🕰️ Runtime Logic Sequence

1. **All Day**: `bot.py` runs continuously, chatting with the user and appending real-time dialogue into `archives/diary/YYYY-MM-DD.md`.
2. **03:00 AM**: `scheduler.py` wakes up `summarizer.py`, calling Claude Sonnet 4.6 to read the previous day's logs, generating hierarchical summaries and categorizing them into `archives/memory/`.
3. **04:00 AM**: `scheduler.py` wakes up `archiver.py`, steps into the `archives` directory, and executes `git add`, `commit`, and `push`, locking the updated data securely into your cloud vault.

## 🤝 Contributing & Feedback

Issues and Pull Requests are welcome! If you are also passionate about "Digital Life" and "LLM Long-term Memory", I look forward to connecting with you.