from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import dotenv_values
import os
import time
import threading
import socketserver
from http.server import SimpleHTTPRequestHandler

try:
    from mtranslate import translate as mt_translate
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Speech Recognition</title>
</head>
<body>
    <div id="output"></div>
    <script>
        const output = document.getElementById('output');
        let recognition;
        let isRecognizing = false;

        function startRecognition() {
            if (isRecognizing) return;

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return;

            recognition = new SpeechRecognition();
            recognition.lang = LANGUAGE_PLACEHOLDER;
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onresult = (event) => {
                let final = '';
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const trans = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        final += trans + ' ';
                    } else {
                        interim = trans;
                    }
                }
                output.textContent = final + interim;
            };

            recognition.onerror = (event) => {
                if (['no-speech', 'audio-capture', 'network'].includes(event.error)) {
                    setTimeout(() => { if (isRecognizing) recognition.start(); }, 1000);
                }
            };

            recognition.onend = () => {
                if (isRecognizing) recognition.start();
            };

            recognition.start();
            isRecognizing = true;
        }

        function stopRecognition() {
            isRecognizing = false;
            if (recognition) recognition.stop();
        }
    </script>
</body>
</html>'''

HtmlCode = HtmlCode.replace('LANGUAGE_PLACEHOLDER', f"'{InputLanguage}'")

# Write HTML
os.makedirs("Data", exist_ok=True)
with open(os.path.join("Data", "Voice.html"), "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Local server
PORT = 8000
Link = f"http://localhost:{PORT}/Voice.html"

def start_server():
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="Data", **kwargs)
        
        def log_message(self, format, *args):
            pass  # Suppress server logs
    
    httpd = socketserver.TCPServer(("", PORT), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

start_server()

# Driver setup
script_dir = os.path.dirname(os.path.abspath(__file__))
local_driver = os.path.join(script_dir, "chromedriver.exe")

options = Options()
prefs = {"profile.default_content_setting_values.media_stream_mic": 1}
options.add_experimental_option("prefs", prefs)
options.add_argument("--use-fake-ui-for-media-stream") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")
options.add_argument("--headless")  # Run in background

service = Service(local_driver)
driver = webdriver.Chrome(service=service, options=options)

# Load page and start
driver.get(Link)
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "output")))
driver.execute_script("startRecognition();")

output_element = driver.find_element(By.ID, "output")

# Output file for Main.py to read
VOICE_OUTPUT_FILE = "Data/VoiceInput.txt"

# Ensure file exists
if not os.path.exists(VOICE_OUTPUT_FILE):
    with open(VOICE_OUTPUT_FILE, 'w') as f:
        f.write("")

def query_modifier(query):
    if not query or not query.strip():
        return ""
    q = query.strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can", "could", "would", "should", "will", "is", "are", "do", "does", "did"]
    is_question = q.split()[0].lower() in question_words if q.split() else False
    while q and q[-1] in '.?!,':
        q = q[:-1]
    q = q + ("?" if is_question else ".")
    return q[0].upper() + q[1:]

def universal_translator(text):
    if not TRANSLATION_AVAILABLE or not text.strip() or text.isascii():
        return text
    try:
        return mt_translate(text, "en", "auto") or text
    except:
        return text

# Main loop
print("P.R.I.S.M Speech Recognition is listening...")

last_text = ""
silence_counter = 0
max_silence = 3  # Reduced for faster response

try:
    while True:
        current_text = output_element.text.strip()

        if current_text != last_text and current_text:
            last_text = current_text
            silence_counter = 0
        else:
            silence_counter += 0.3
            
            if silence_counter >= max_silence and last_text:
                # Process the command
                translated = universal_translator(last_text) if InputLanguage.split('-')[0].lower() != 'en' else last_text
                final = query_modifier(translated)
                
                print(f"[VOICE INPUT]: {final}")
                
                # Write to file for Main.py to process
                with open(VOICE_OUTPUT_FILE, 'w') as f:
                    f.write(final)
                
                # Clear for next command
                driver.execute_script("document.getElementById('output').textContent = '';")
                last_text = ""
                silence_counter = 0

        time.sleep(0.3)

except KeyboardInterrupt:
    print("\n\nShutting down speech recognition...")
finally:
    driver.execute_script("stopRecognition();")
    driver.quit()