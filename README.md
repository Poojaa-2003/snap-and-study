# 🎓 Snap & Study — AI Multimodal Concept Tutor

**Snap & Study** is an AI-powered educational assistant built with **Streamlit**, **Google Gemini 2.5 Flash (Vision & Chat)**, and **Telegram Bot API**. 

Students can photograph a tricky textbook problem, circuit/biological diagram, mathematical formula, or handwritten study notes—or type an academic question—and receive an intuitive, step-by-step breakdown. With a single click, students can export a high-yield study sheet straight to their personal Telegram chat for quick exam revision.

---

## 🌟 Key Features
- **Multimodal Visual Understanding**: Upload photos of diagrams, math problems, or handwritten notes directly from desktop or mobile.
- **Pedagogical AI Persona**: Gemini acts as a patient, encouraging tutor that explains core concepts intuitively rather than just dumping raw answers.
- **Context-Aware Dialogue**: Maintains conversational memory across multiple turns for clarifying follow-ups (e.g., *"Can you explain step 2 in more detail?"*).
- **One-Click Study Notes Export**: Formats an executive summary of key formulas, principles, and solved takeaways and pushes it directly to Telegram via the Bot API.
- **Zero Third-Party SMS/Sandbox Friction**: Direct Telegram Bot integration without 72-hour sandbox expiries.

---

## 🏗️ Architecture & Project Structure

```text
snap_and_study/
├── app.py                     # Main Streamlit application and UI logic
├── prompts.py                 # System prompt, welcome message, and study summary prompts
├── requirements.txt           # Project dependencies
├── .gitignore                 # Excludes venv and secrets from git
├── README.md                  # Documentation and setup instructions
└── .streamlit/
    ├── secrets.toml.example   # Template for API keys
    └── secrets.toml           # Local configuration (never committed)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9 or newer installed
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)
- A free **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

### 2. Installation
```powershell
# Navigate into the project folder
cd snap_and_study

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 3. Setup Secrets
Copy the template file to `.streamlit/secrets.toml`:
```powershell
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your real keys:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
TELEGRAM_BOT_TOKEN = "your-bot-token-from-botfather"
```

### 4. Running the Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📱 How to Get Your Telegram Bot Token & Chat ID
1. **Get Bot Token**: Open Telegram, search for `@BotFather`, send `/newbot`, follow the prompt, and copy the HTTP API Token.
2. **Start the Bot**: Open your new bot's link in Telegram and tap **Start** (or send `/start`).
3. **Get Your Chat ID**: Message `@userinfobot` or `@RawDataBot` on Telegram. It will instantly reply with your numeric `Id` (e.g., `123456789`). Use this ID in the Snap & Study onboarding screen!

---

## ☁️ Deployment (Streamlit Community Cloud)
1. Push this project to your GitHub repository (verify `.streamlit/secrets.toml` is ignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select your repository and branch, and choose `app.py` as the entrypoint.
4. Under **Advanced settings / Secrets**, paste the contents of your `secrets.toml`.
5. Click **Deploy** to receive a public URL to submit!
