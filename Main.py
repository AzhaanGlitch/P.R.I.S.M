import os
import sys
import threading
import time
from datetime import datetime

# Add Backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

# Import backend modules
from Backend.Chatbot import ChatBot
from Backend.Model import FirstLayerDMM
from Backend.Automation import *
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.ImageGeneration import GenerateImageWithRetry
from Backend.TextToSpeech import Speak

class PrismVoiceCore:
    def __init__(self):
        self.running = True
        self.files = {
            'status': 'Frontend/Files/Status.data',
            'mic': 'Frontend/Files/Mic.data',
        }
        
        # Ensure directories exist
        os.makedirs('Frontend/Files', exist_ok=True)
        os.makedirs('Data', exist_ok=True)
        
        # Initialize files
        for file_path in self.files.values():
            if not os.path.exists(file_path):
                open(file_path, 'w').close()
        
        self.write_file('status', 'Initializing...')
        print("P.R.I.S.M Voice Core initialized.")
        
    def write_file(self, file_key, content):
        try:
            with open(self.files[file_key], 'w') as f:
                f.write(str(content))
        except Exception as e:
            print(f"Error writing to {file_key}: {e}")
            
    def read_file(self, file_key):
        try:
            with open(self.files[file_key], 'r') as f:
                return f.read().strip()
        except:
            return ""
    
    def process_query(self, query):
        """Main query processing logic"""
        if not query or len(query.strip()) < 2:
            return
        
        print(f"\n[USER SAID]: {query}")
        self.write_file('status', 'Processing...')
        
        try:
            # Get decision from Model
            tasks = FirstLayerDMM(query)
            print(f"[TASKS IDENTIFIED]: {tasks}")
            
            response = ""
            
            for task in tasks:
                task = task.strip()
                
                # Exit command
                if task == "exit":
                    response = "Goodbye sir. Shutting down P.R.I.S.M."
                    self.running = False
                    
                # General conversation
                elif task.startswith("general"):
                    q = task.replace("general", "").strip()
                    response = ChatBot(q if q else query)
                    
                # Real-time search
                elif task.startswith("realtime"):
                    q = task.replace("realtime", "").strip()
                    response = RealtimeSearchEngine(q if q else query)
                    
                # Open application/website
                elif task.startswith("open"):
                    target = task.replace("open", "").strip()
                    if target:
                        response = OpenApplication(target) if not target.startswith("http") else OpenWebsite(target)
                    
                # Close application
                elif task.startswith("close"):
                    app = task.replace("close", "").strip()
                    if app:
                        response = CloseApplication(app)
                    
                # Play music
                elif task.startswith("play"):
                    song = task.replace("play", "").strip()
                    if song:
                        response = PlayMusic(song)
                    
                # Google search
                elif task.startswith("google search"):
                    q = task.replace("google search", "").strip()
                    if q:
                        response = GoogleSearch(q)
                    
                # YouTube search
                elif task.startswith("youtube search"):
                    q = task.replace("youtube search", "").strip()
                    if q:
                        response = YoutubeSearch(q)
                    
                # Image generation
                elif task.startswith("generate image"):
                    prompt = task.replace("generate image", "").strip()
                    if prompt:
                        response = GenerateImageWithRetry(prompt)
                    
                # System controls
                elif task.startswith("system"):
                    cmd = task.replace("system", "").strip().lower()
                    if "volume up" in cmd:
                        response = VolumeUp()
                    elif "volume down" in cmd:
                        response = VolumeDown()
                    elif "mute" in cmd:
                        response = Mute()
                    elif "unmute" in cmd:
                        response = Unmute()
                    elif "screenshot" in cmd:
                        response = Screenshot()
                
                # Speak response
                if response:
                    print(f"[P.R.I.S.M RESPONDS]: {response}")
                    self.write_file('status', 'Speaking...')
                    Speak(response)
                    time.sleep(0.3)
            
            self.write_file('status', 'Listening...')
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"[ERROR]: {error_msg}")
            self.write_file('status', 'Error - Ready')
    
    def monitor_voice_input(self):
        """Monitor for voice input from SpeechToText"""
        print("[VOICE MONITOR]: Starting voice input monitoring...")
        
        # Import and start SpeechToText in a separate process
        voice_thread = threading.Thread(target=self.run_speech_to_text, daemon=True)
        voice_thread.start()
        
        # Monitor the output
        last_query = ""
        silence_time = 0
        
        while self.running:
            try:
                # Check if there's text from voice recognition
                # This will be written to a temp file by SpeechToText
                voice_file = "Data/VoiceInput.txt"
                
                if os.path.exists(voice_file):
                    with open(voice_file, 'r') as f:
                        query = f.read().strip()
                    
                    if query and query != last_query:
                        last_query = query
                        
                        # Clear the file
                        with open(voice_file, 'w') as f:
                            f.write("")
                        
                        # Process the query
                        self.process_query(query)
                        silence_time = 0
                    else:
                        silence_time += 0.5
                else:
                    silence_time += 0.5
                
                # Reset after long silence
                if silence_time > 10:
                    last_query = ""
                    silence_time = 0
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Voice monitoring error: {e}")
                time.sleep(1)
    
    def run_speech_to_text(self):
        """Run the speech to text module"""
        try:
            # Import the speech to text module
            from Backend import SpeechToText
            
            print("[SPEECH-TO-TEXT]: Module loaded and running...")
            
        except Exception as e:
            print(f"[ERROR]: Could not start speech recognition: {e}")
            print("[INFO]: You can still type commands in the console.")
    
    def console_input_monitor(self):
        """Monitor console for text commands (backup method)"""
        print("[CONSOLE INPUT]: Type 'help' for commands, 'exit' to quit")
        
        while self.running:
            try:
                user_input = input("\n[COMMAND]: ").strip()
                
                if user_input:
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        self.process_query("exit")
                        break
                    elif user_input.lower() == 'help':
                        print("\nAvailable commands:")
                        print("- General questions: 'how are you', 'what is AI'")
                        print("- Real-time: 'what's the weather', 'latest news'")
                        print("- Automation: 'open chrome', 'play music', 'take screenshot'")
                        print("- Search: 'search for python', 'youtube search cats'")
                        print("- Exit: 'exit', 'quit', 'bye'")
                    else:
                        self.process_query(user_input)
                        
            except KeyboardInterrupt:
                print("\n[SYSTEM]: Shutting down...")
                self.running = False
                break
            except Exception as e:
                print(f"[ERROR]: {e}")
    
    def run(self):
        """Main run loop"""
        print("\n" + "="*70)
        print("P.R.I.S.M - Personal Responsive Intelligence System Manager")
        print("="*70)
        print("\n[SYSTEM]: Starting voice-controlled assistant...")
        print("[SYSTEM]: Speak your commands or type in the console.")
        print("[SYSTEM]: Press Ctrl+C to exit.\n")
        
        # Start voice input monitor
        voice_thread = threading.Thread(target=self.monitor_voice_input, daemon=True)
        voice_thread.start()
        
        # Initialize status
        self.write_file('status', 'Listening...')
        
        # Greeting
        Speak("P.R.I.S.M is online and ready, sir.")
        
        print("[SYSTEM]: P.R.I.S.M is listening...\n")
        
        # Console input as backup
        self.console_input_monitor()
        
        # Shutdown
        print("\n[SYSTEM]: Shutting down P.R.I.S.M...")
        self.write_file('status', 'Shutting down...')
        Speak("Goodbye sir.")

def main():
    # Start the core system
    core = PrismVoiceCore()
    
    # Start GUI in separate thread
    try:
        from Frontend.GUI import main as gui_main
        gui_thread = threading.Thread(target=gui_main, daemon=False)
        gui_thread.start()
        
        print("[SYSTEM]: Visual interface launched.")
        time.sleep(2)  # Give GUI time to initialize
        
    except Exception as e:
        print(f"[WARNING]: Could not launch GUI: {e}")
        print("[SYSTEM]: Running in console-only mode.")
    
    # Run the core
    core.run()

if __name__ == "__main__":
    main()