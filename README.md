# 📖 Diary-Fairy: AI Companion & Lifelog Archival System

> **"Weaving a lifetime of memory wealth through seamless companionship, especially for those who struggle to keep a journal."**

Frieren-Bot is a highly engineered, lightweight personal AI companion system that balances warmth and rationality. It is not just a chatbot, but a fully automated **digital archive of your life cycle**. 

Through daily, fragmented conversations, the system silently extracts your life trajectory and emotional fluctuations in the background, generating a beautifully formatted, timeline-based journal that is safely stored in your private cloud.

## ✨ Core Features

* 🧠 **Dual-AI Engine**: Utilizes OpenAI for the frontend (fast response times, handling high-frequency emotional companionship) and Anthropic Claude 3.5 Sonnet for the backend (strict logic, executing late-night long-text memory compression). This maximizes the strengths of both models while optimizing API costs.
* 🛤️ **Dual-Track Memory Architecture**:
    * **Human Diary**: Generates beautifully formatted Markdown journals with emotional and literary value for humans to read later.
    * **Bot Memory**: Extracts dry, high-density objective facts and preference tags to inject into the AI's long-term subconsciousness.
* 🌊 **Cascade Summarization**: The ultimate solution to LLM token limits and hallucinations. Triggered automatically every midnight, it filters and compresses memories hierarchically from "Daily -> Weekly -> Monthly -> Yearly". 
* 🛡️ **Open Source Code, Private Data (Nested Repositories)**: Drops heavy databases in favor of local, pure-text Markdown storage. The outer code repository can be safely open-sourced, while the `archives` folder acts as an independent Git repository. An automated script pushes the vault daily to your private GitHub repository, achieving physical-level privacy isolation. 
* ⚙️ **Geek-Level Config-Driven Design**: All system prompts, model parameters, cron times, and directory paths are extracted into JSON files. The core code remains absolutely clean with zero hardcoding.

## 🛠️ Tech Stack

* **Language**: Python 3.12+
* **LLM APIs**: OpenAI API (Chat), Anthropic API (Summarize)
* **Version Control & Storage**: Git, GitHub (Automated Archiving)
* **Task Scheduling**: `schedule` library, `subprocess`

## 📂 Architecture

```text
📁 Frieren_Bot/                 <-- Public Repository (Code is fully open)
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
git clone https://github.com/harkerxia/diary-fairy.git
cd diary-fairy
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
2. **03:00 AM**: `scheduler.py` wakes up `summarizer.py`, calling Claude 3.5 Sonnet to read the previous day's logs, generating hierarchical summaries and categorizing them into `archives/memory/`.
3. **04:00 AM**: `scheduler.py` wakes up `archiver.py`, steps into the `archives` directory, and executes `git add`, `commit`, and `push`, locking the updated data securely into your cloud vault.

## 🤝 Contributing & Feedback

Issues and Pull Requests are welcome! If you are also passionate about "Digital Life" and "LLM Long-term Memory", I look forward to connecting with you.
