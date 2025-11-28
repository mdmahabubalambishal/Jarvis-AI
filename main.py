
import os
import sys
import time
import json
import webbrowser
import datetime
import threading
import pyttsx3
import speech_recognition as sr
import wikipedia
from dotenv import load_dotenv
try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    import requests
except Exception:
    requests = None

#Music
pygame_available = False
try:
    import pygame
    pygame_available = True
except Exception:
    pygame_available = False

# pdf
try:
    import PyPDF2
except Exception:
    PyPDF2 = None

# system info
try:
    import psutil
except Exception:
    psutil = None

# screenshot
try:
    import pyautogui
except Exception:
    pyautogui = None

#   Load environment (API keys)
load_dotenv()
GEMINI_API_KEY = os.getenv("AIzaSyCFjU8-AfnAE51YJcxwvDoiUnwwUr_dYBk")     
NEWS_API_KEY = os.getenv("f744d4744591ce171671948986360b35")          

if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        genai = None


#   Initialize TTS
engine = pyttsx3.init()
engine.setProperty("rate", 170)  # speech rate

def speak(text):
    """Speak and print."""
    print("Jarvis:", text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS error:", e)

#   Speech recognition
recognizer = sr.Recognizer()

def take_command(timeout=5, phrase_time_limit=8):
    """Listen from microphone and return lowercase string. Returns 'none' on failure."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-US")
        print("You said:", query)
        return query.lower()
    except sr.WaitTimeoutError:
        print("Listening timed out")
        return "none"
    except sr.UnknownValueError:
        speak("Could not understand audio")
        return "none"
    except Exception as e:
        print("Speech recognition error:", e)
        speak("Sorry, I couldn't hear you properly.")
        return "none"

#   Greeting
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning, Sir!")
    elif hour < 18:
        speak("Good Afternoon, Sir!")
    else:
        speak("Good Evening, Sir!")
    speak("I am Jarvis. How may I help you?")

#   AI THINK (Gemini) wrapper
def ai_think(prompt):
    if not genai:
        return "Generative AI is not configured. Please set GEMINI_API_KEY in the .env file."
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        # response object shape may vary; attempt to extract text
        if hasattr(response, "text"):
            return response.text
        elif isinstance(response, dict):
            return response.get("content", "No response text")
        else:
            return str(response)
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, I couldn't get an answer from the AI."

#   Music Player (pygame fallback to os.startfile)
# #music folder path here
MUSIC_DIR = r"D:\jarvis-ai\music"  
music_files = []
current_song_idx = 0
music_lock = threading.Lock()
music_playing = False

def load_music_files():
    global music_files
    if not os.path.isdir(MUSIC_DIR):
        music_files = []
        return
    music_files = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith((".mp3", ".wav", ".ogg"))]

def play_music(idx=0):
    global music_playing, current_song_idx
    load_music_files()
    if not music_files:
        speak("There are no music files in the configured folder.")
        return
    idx = idx % len(music_files)
    current_song_idx = idx
    path = os.path.join(MUSIC_DIR, music_files[current_song_idx])
    if pygame_available:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            music_playing = True
            speak(f"Playing {music_files[current_song_idx]}")
            return
        except Exception as e:
            print("pygame play error:", e)
    # fallback
    try:
        os.startfile(path)
        music_playing = True
        speak(f"Opening {music_files[current_song_idx]} in default player")
    except Exception as e:
        print("fallback play error:", e)
        speak("Couldn't play the music file.")

def stop_music():
    global music_playing
    if pygame_available:
        try:
            pygame.mixer.music.stop()
            music_playing = False
            speak("Music stopped")
            return
        except Exception:
            pass
    # fallback: no reliable stop for os.startfile
    speak("Stopped (if using default player, please stop it manually).")

def next_song():
    global current_song_idx
    load_music_files()
    if not music_files:
        speak("No songs available.")
        return
    current_song_idx = (current_song_idx + 1) % len(music_files)
    play_music(current_song_idx)

def previous_song():
    global current_song_idx
    load_music_files()
    if not music_files:
        speak("No songs available.")
        return
    current_song_idx = (current_song_idx - 1) % len(music_files)
    play_music(current_song_idx)

#   Open apps helper
def open_app(app_name):
    # Update paths to match your system if needed
    apps = {
        "notepad": r"C:\Windows\System32\notepad.exe",
        "calculator": r"C:\Windows\SystemApps\Microsoft.WindowsCalculator_8wekyb3d8bbwe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "vscode": r"C:\Users\<mdmah>\AppData\Local\Programs\Microsoft VS Code\Code.exe".replace("{user}", os.getlogin())
    }
    path = apps.get(app_name)
    if path and os.path.exists(path):
        try:
            os.startfile(path)
            speak(f"Opening {app_name}")
        except Exception as e:
            speak(f"Couldn't open {app_name}.")
            print("open_app error:", e)
    else:
        speak(f"Path for {app_name} not found. Please update the path in the script.")

#   System control
def system_shutdown():
    speak("Shutting down my computer")
    os.system("shutdown /s /t 5")

def system_restart():
    speak("Restarting my computer")
    os.system("shutdown /r /t 5")

def system_sleep():
    speak("Putting my computer to sleep")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

#   News reader (NewsAPI)
def read_news(top_n=3, country="us"):
    if requests is None or not NEWS_API_KEY:
        speak("News feature is not configured. Please install requests and set NEWS_API_KEY in .env.")
        return
    try:
        url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={NEWS_API_KEY}"
        res = requests.get(url, timeout=10).json()
        articles = res.get("articles", [])[:top_n]
        if not articles:
            speak("No news found.")
            return
        for i, art in enumerate(articles, start=1):
            title = art.get("title", "No title")
            speak(f"Headline {i}: {title}")
            time.sleep(0.5)
    except Exception as e:
        print("News error:", e)
        speak("Failed to fetch news.")

#   Memory mode (simple file store)
MEMORY_FILE = "memory.json"

def remember_text(text):
    data = {"memory": text, "timestamp": datetime.datetime.now().isoformat()}
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        speak("Okay, I will remember that.")
    except Exception as e:
        print("remember error:", e)
        speak("I couldn't save that to memory.")

def recall_memory():
    if not os.path.exists(MEMORY_FILE):
        speak("I don't have anything saved in memory.")
        return
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        mem = data.get("memory", "")
        ts = data.get("timestamp", "")
        speak(f"You asked me to remember: {mem}. I saved it on {ts}.")
    except Exception as e:
        print("recall error:", e)
        speak("I couldn't read the memory file.")

#   PDF Reader
def read_pdf(path, page_num=None):
    if PyPDF2 is None:
        speak("PyPDF2 is not installed. Please install it to read PDFs.")
        return
    if not os.path.exists(path):
        speak("PDF file not found. Check the path.")
        return
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            speak(f"The PDF has {num_pages} pages.")
            if page_num is None:
                speak("Which page should I read?")
                ans = take_command()
                try:
                    page_num = int(ans)
                except:
                    speak("Invalid page number.")
                    return
            if page_num < 1 or page_num > num_pages:
                speak("Page number out of range.")
                return
            text = reader.pages[page_num - 1].extract_text()
            if not text:
                speak("Couldn't extract text from that page.")
                return
            # Limit reading length
            snippet = text.strip()
            if len(snippet) > 2000:
                snippet = snippet[:2000] + " ... (truncated)"
            speak(snippet)
    except Exception as e:
        print("PDF read error:", e)
        speak("Failed to read the PDF.")

#   Helper: wikipedia search
def search_wikipedia(topic):
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(topic, sentences=2)
        speak(result)
    except Exception as e:
        print("wikipedia error:", e)
        speak("I couldn't find that on Wikipedia.")

#   Main loop
def main_loop():
    global current_song_idx

    greet_user()
    load_music_files()

    while True:
        query = take_command()
        if not query or query == "none":
            continue

        # EXIT
        if any(x in query for x in ["stop", "exit", "quit", "shutdown jarvis"]):
            speak("Shutting down Jarvis. Goodbye sir!")
            break

        # TIME
        if "time" in query:
            t = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {t}")
            continue

        # WIKIPEDIA
        if "wikipedia" in query:
            topic = query.replace("wikipedia", "").strip()
            if topic:
                search_wikipedia(topic)
            else:
                speak("What should I search on Wikipedia?")
            continue

        # OPEN WEBSITE
        if "open youtube" in query:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube")
            continue
        if "open google" in query:
            webbrowser.open("https://google.com")
            speak("Opening Google")
            continue
        if "open linkedin" in query:
            # change to your LinkedIn url if needed
            webbrowser.open("https://www.linkedin.com/in/md-mahabub-alam-bishal-097b77286/")
            speak("Opening your LinkedIn")
            continue

        # MUSIC
        if "play music" in query or "play song" in query:
            play_music(current_song_idx)
            continue
        if "next song" in query or "next music" in query:
            next_song()
            continue
        if "previous song" in query or "previous music" in query:
            previous_song()
            continue
        if "stop music" in query or "stop song" in query:
            stop_music()
            continue

        # OPEN APPS
        if "open notepad" in query:
            open_app("notepad")
            continue
        if "open calculator" in query:
            open_app("calculator")
            continue
        if "open chrome" in query:
            open_app("chrome")
            continue
        if "open vs code" in query or "open vscode" in query or "open code" in query:
            open_app("vscode")
            continue

        # SYSTEM CONTROL
        if "shutdown pc" in query or (("shutdown" in query) and ("jarvis" not in query)):
            system_shutdown()
            continue
        if "restart" in query:
            system_restart()
            continue
        if "sleep" in query:
            system_sleep()
            continue

        # NEWS
        if "news" in query or "headlines" in query:
            read_news()
            continue

        # MEMORY
        if query.startswith("remember"):
            # e.g., "remember I have exam on Friday"
            memory_text = query.replace("remember", "").strip()
            if memory_text:
                remember_text(memory_text)
            else:
                speak("What should I remember?")
            continue
        if "what do you remember" in query or "recall" in query:
            recall_memory()
            continue

        # PDF
        if "read pdf" in query or ("read" in query and "pdf" in query):
            speak("Please tell me the full path to the PDF file, or say default.")
            path_cmd = take_command(timeout=8, phrase_time_limit=10)
            if path_cmd and path_cmd != "none":
                if path_cmd.lower() in ["default", "sample", "use default"]:
                    pdf_path = r"C:\Users\mdmah\AppData\Roaming\kingsoft\office6\startpage\documents" 
                else:
                    pdf_path = path_cmd.strip()
                    speak("Spoken file paths might be unreliable. If it fails, please edit the pdf path directly in main.py.")
                read_pdf(pdf_path)
            continue

        # SCREENSHOT
        if "take screenshot" in query or "screenshot" in query:
            if pyautogui:
                img = pyautogui.screenshot()
                filename = f"screenshot_{int(time.time())}.png"
                img.save(filename)
                speak(f"Screenshot saved as {filename}")
            else:
                speak("pyautogui is not installed.")
            continue

        # BATTERY
        if "battery" in query:
            if psutil:
                battery = psutil.sensors_battery()
                if battery:
                    speak(f"Battery is at {battery.percent} percent.")
                else:
                    speak("Couldn't fetch battery information.")
            else:
                speak("psutil not installed.")
            continue

        # THINK / GENERATIVE AI (fallback if not matched)
        # Any other query: ask Gemini / LLM
        speak("Thinking...")
        answer = ai_think(query)
        speak(answer)

#   Entry point
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        speak("Jarvis terminated by user.")
    except Exception as e:
        print("Fatal error:", e)
        speak("A fatal error occurred. Check the console for details.")
