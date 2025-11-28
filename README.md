# Jarvis AI - Desktop Voice Assistant

Jarvis is a voice-activated AI desktop assistant built using Python.  
It can listen to your voice, answer questions, open websites, search Wikipedia, tell the time, and even use Generative AI (Gemini/OpenAI).

---

## 🔧 Features
### Level 1: Basic I/O
- Speak using pyttsx3
- Listen using microphone
- Time-based greeting

### Level 2: Automation
- Tell current time
- Wikipedia search
- Open YouTube, Google, LinkedIn

### Level 3: Generative AI
- Uses Gemini API via google-generativeai library
- "Think" command → sends query to LLM

Component:
- TTS (pyttsx3)
- Speech -> text (SpeechRecognition)
- Wikipedia search
- Open Websites (YouTube, Google, LinkedIn)
- Gemini (google-generativeai) LLM "think"
- Music player (play / next / previous / stop) using pygame (fallback to os.startfile)
- Open apps (Notepad, Calculator, Chrome, VS Code)
- System control (shutdown / restart / sleep)
- News reader (NewsAPI)
- Memory mode (remember / recall)
- PDF reader (PyPDF2)
- Helpful prompts & safe .env usage
"""

## 🛠 Setup

### 1. Create Virtual Environment
```
python -m venv env
env\Scripts\activate
```

### 2. Install Libraries
```
pip install -r requirements.txt
```

### 3. Run Project
```
python main.py
```

---

## 🧠 Tech Used
- Python
- pyttsx3
- SpeechRecognition
- pyaudio
- wikipedia
- google-generativeai
- python-dotenv
- pygame
- PyPDF2
- requests
- psutil
- pyautogui
- webbrowser
---

## 👤 Author
Your Name
Md Mahabub Alam Bishal
Inspired by
Bappy Choudhury jarvis-AI project