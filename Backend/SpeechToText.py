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

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")

# Optimized HTML with faster recognition
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
        let finalTranscript = '';

        function startRecognition() {
            if (isRecognizing) return;

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) return;

            recognition = new SpeechRecognition();
            recognition.lang = LANGUAGE_PLACEHOLDER;
            recognition.continuous = false;  // Changed for faster response
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;

            recognition.onresult = (event) => {
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const trans = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += trans + ' ';
                    } else {
                        interim = trans;
                    }
                }
                output.textContent = finalTranscript + interim;
            };

            recognition.onerror = (event) => {
                if (['no-speech', 'audio-capture'].includes(event.error)) {
                    setTimeout(() => { if (isRecognizing) recognition.start(); }, 500);
                }
            };

            recognition.onend = () => {
                if (isRecognizing) {
                    setTimeout(() => recognition.start(), 100);  // Faster restart
                }
            };

            recognition.start();
            isRecognizing = true;
        }

        function stopRecognition() {
            isRecognizing = false;
            if (recognition) recognition.stop();
        }
        
        function clearOutput() {
            finalTranscript = '';
            output.textContent = '';
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
            pass
    
    httpd = socketserver.TCPServer(("", PORT), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

start_server()

# Optimized Chrome options
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
options.add_argument("--headless")
options.add_argument("--disable-extensions")
options.add_argument("--disable-logging")

service = Service(local_driver)
driver = webdriver.Chrome(service=service, options=options)

# Load and start
driver.get(Link)
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "output")))
driver.execute_script("startRecognition();")

output_element = driver.find_element(By.ID, "output")

VOICE_OUTPUT_FILE = "Data/VoiceInput.txt"

if not os.path.exists(VOICE_OUTPUT_FILE):
    with open(VOICE_OUTPUT_FILE, 'w') as f:
        f.write("")

def query_modifier(query):
    """Quick query formatting"""
    if not query or not query.strip():
        return ""
    q = query.strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "can", "could", "would", "should", "will", "is", "are", "do", "does", "did"]
    is_question = q.split()[0].lower() in question_words if q.split() else False
    while q and q[-1] in '.?!,':
        q = q[:-1]
    q = q + ("?" if is_question else ".")
    return q[0].upper() + q[1:]

print("Prism Speech Recognition listening...")

last_text = ""
silence_counter = 0
max_silence = 2  # Faster trigger (was 3)

try:
    while True:
        current_text = output_element.text.strip()

        if current_text != last_text and current_text:
            last_text = current_text
            silence_counter = 0
        else:
            silence_counter += 0.2  # Faster polling
            
            if silence_counter >= max_silence and last_text:
                # Process command
                final = query_modifier(last_text)
                
                if final and len(final) > 2:  # Only process valid commands
                    print(f"[VOICE]: {final}")
                    
                    # Write to file
                    with open(VOICE_OUTPUT_FILE, 'w') as f:
                        f.write(final)
                
                # Clear
                driver.execute_script("clearOutput();")
                last_text = ""
                silence_counter = 0

        time.sleep(0.2)  # Faster polling

except KeyboardInterrupt:
    print("\nShutting down speech recognition...")
finally:
    driver.execute_script("stopRecognition();")
    driver.quit()