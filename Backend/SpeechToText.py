from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <p id="status" style="color: gray;">Ready</p>
    <script>
        const output = document.getElementById('output');
        const status = document.getElementById('status');
        let recognition;
        let isRecognizing = false;

        function startRecognition() {
            if (isRecognizing) return;
            
            recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onstart = function() {
                isRecognizing = true;
                status.textContent = 'Listening...';
                status.style.color = 'green';
            };

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onerror = function(event) {
                status.textContent = 'Error: ' + event.error;
                status.style.color = 'red';
                isRecognizing = false;
            };

            recognition.onend = function() {
                if (isRecognizing) {
                    recognition.start();
                }
            };
            
            recognition.start();
        }

        function stopRecognition() {
            isRecognizing = false;
            if (recognition) {
                recognition.stop();
            }
            status.textContent = 'Stopped';
            status.style.color = 'gray';
        }
    </script>
</body>
</html>'''

HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Create Data directory if it doesn't exist
os.makedirs("Data", exist_ok=True)

with open(r"Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")

# Try to use Chrome without ChromeDriverManager (uses system Chrome)
try:
    # First try: Use Chrome directly without downloading driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✓ Using system ChromeDriver")
except Exception as e:
    try:
        # Second try: Specify common ChromeDriver paths
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            os.path.join(os.path.expanduser("~"), "chromedriver.exe"),
            "chromedriver.exe"
        ]
        
        driver = None
        for path in possible_paths:
            if os.path.exists(path):
                service = Service(path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"✓ Using ChromeDriver from: {path}")
                break
        
        if driver is None:
            raise Exception("ChromeDriver not found")
            
    except Exception as e2:
        # Third try: Use ChromeDriverManager with offline cache
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ Using ChromeDriverManager")
        except Exception as e3:
            print("\n❌ ERROR: Could not initialize ChromeDriver")
            print("\nPossible solutions:")
            print("1. Make sure Chrome is installed")
            print("2. Download ChromeDriver manually from: https://chromedriver.chromium.org/downloads")
            print("3. Place chromedriver.exe in the same folder as this script")
            print("4. Or add chromedriver.exe to your system PATH")
            print(f"\nOriginal error: {e3}")
            exit(1)

TempDirPath = rf"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    """Set the assistant status to a file"""
    try:
        with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
            file.write(Status)
    except Exception as e:
        print(f"Warning: Could not write status: {e}")

def QueryModifier(Query):
    """Modify query to add proper punctuation"""
    new_query = Query.lower().strip()
    if not new_query:
        return ""
    
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can", "could", "would", "should"]

    # Check if it starts with a question word
    is_question = any(new_query.startswith(word + " ") for word in question_words)
    
    if is_question:
        # Remove existing punctuation at the end
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1]
        new_query = new_query + "?"
    else:
        # Add period if no punctuation exists
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query + "."
            
    return new_query.capitalize()

def UniversalTranslator(Text):
    """Translate text to English"""
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return Text

def SpeechRecognition():
    """Capture speech input from the browser"""
    try:
        driver.get("file:///" + Link)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "start"))
        )
        
        # Start recognition
        driver.find_element(By.ID, "start").click()
        print("🎤 Listening... (speak now)")

        last_text = ""
        silence_counter = 0
        max_silence = 3  # seconds of no new text before stopping

        while True:
            try:
                Text = driver.find_element(By.ID, "output").text.strip()

                if Text and Text != last_text:
                    last_text = Text
                    silence_counter = 0
                    print(f"📝 Captured: {Text[:50]}...")
                elif Text:
                    silence_counter += 0.5
                    if silence_counter >= max_silence:
                        break
                
                time.sleep(0.5)
                
            except Exception as e:
                time.sleep(0.5)
                continue

        # Stop recognition
        try:
            driver.find_element(By.ID, "end").click()
        except:
            pass

        if last_text:
            if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                return QueryModifier(last_text)
            else:
                translated = UniversalTranslator(last_text)
                return QueryModifier(translated)
        else:
            return None
            
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Speech Recognition System Started")
    print("=" * 50)
    print(f"Language: {InputLanguage}")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            Text = SpeechRecognition()
            if Text:
                print(f"\n✅ Final Output: {Text}\n")
                print("-" * 50)
            else:
                print("⚠️  No speech detected. Trying again...\n")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        try:
            driver.quit()
        except:
            pass
        print("✓ Browser closed")