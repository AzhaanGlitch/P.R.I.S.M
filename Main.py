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
    def __init__(self, gui_mode='tray'):
        self.running = True
        self.gui_mode = gui_mode  # 'tray', 'full', or 'none'
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
        self.write_file('mic', '1')  # Start listening by default
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
        voice_file = "Data/VoiceInput.txt"
        
        while self.running:
            try:
                # Check mic status
                mic_status = self.read_file('mic')
                if mic_status != '1':
                    time.sleep(0.5)
                    continue
                
                # Check if there's text from voice recognition
                if os.path.exists(voice_file):
                    with open(voice_file, 'r') as f:
                        query = f.read().strip()
                    
                    if query and query != last_query:
                        # 1. Update last_query immediately so we don't repeat
                        last_query = query
                        
                        # 2. Clear the file immediately
                        with open(voice_file, 'w') as f:
                            f.write("")
                        
                        # 3. Process DIRECTLY (No Threading)
                        # This blocks the loop so we don't process new inputs while speaking
                        self.process_query(query)
                        
                        # 4. CRITICAL: Clear the file AGAIN after speaking
                        # This deletes the "Echo" (the assistant hearing itself)
                        # so the loop is fresh for your next command.
                        with open(voice_file, 'w') as f:
                            f.write("")
                            
                        silence_time = 0
                    else:
                        silence_time += 0.5
                else:
                    silence_time += 0.5
                
                # Reset after long silence to allow repeating commands
                if silence_time > 5: # Reduced to 5 seconds for snappier response
                    last_query = ""
                    silence_time = 0
                
                time.sleep(0.2) # Reduced sleep for faster response
                
            except Exception as e:
                print(f"Voice monitoring error: {e}")
                time.sleep(1)
    
    def run_speech_to_text(self):
        """Run the speech to text module"""
        try:
            from Backend import SpeechToText
            print("[SPEECH-TO-TEXT]: Module loaded and running...")
        except Exception as e:
            print(f"[ERROR]: Could not start speech recognition: {e}")
            print("[INFO]: You can still type commands in the console.")
    
    def console_input_monitor(self):
        """Monitor console for text commands (backup method)"""
        if self.gui_mode == 'tray':
            # In tray mode, just keep the thread alive
            while self.running:
                time.sleep(1)
            return
        
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
        print("[SYSTEM]: Speak your commands or use system tray.")
        print("[SYSTEM]: Press Ctrl+C in console to exit.\n")
        
        # Start voice input monitor
        voice_thread = threading.Thread(target=self.monitor_voice_input, daemon=True)
        voice_thread.start()
        
        # Initialize status
        self.write_file('status', 'Listening...')
        
        # Greeting
        Speak("P.R.I.S.M is online and ready, sir.")
        
        print("[SYSTEM]: P.R.I.S.M is listening...\n")
        
        # Console input as backup (or just wait in tray mode)
        self.console_input_monitor()
        
        # Shutdown
        print("\n[SYSTEM]: Shutting down P.R.I.S.M...")
        self.write_file('status', 'Shutting down...')
        Speak("Goodbye sir.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='P.R.I.S.M Voice Assistant')
    parser.add_argument('--mode', choices=['tray', 'full', 'console'], default='tray',
                       help='GUI mode: tray (system tray), full (fullscreen), console (no GUI)')
    args = parser.parse_args()
    
    # Start the core system
    core = PrismVoiceCore(gui_mode=args.mode)
    
    # Start GUI based on mode
    try:
        if args.mode == 'tray':
            from Frontend.SystemTrayGUI import main as tray_main
            # Pass core instance to GUI
            gui_thread = threading.Thread(target=lambda: tray_main(core), daemon=False)
            gui_thread.start()
            print("[SYSTEM]: System tray interface launched.")
            
        elif args.mode == 'full':
            from Frontend.GUI import main as gui_main
            gui_thread = threading.Thread(target=gui_main, daemon=False)
            gui_thread.start()
            print("[SYSTEM]: Full visual interface launched.")
        
        else:  # console mode
            print("[SYSTEM]: Running in console-only mode.")
        
        time.sleep(2)  # Give GUI time to initialize
        
    except Exception as e:
        print(f"[WARNING]: Could not launch GUI: {e}")
        print("[SYSTEM]: Running in console-only mode.")
    
    # Run the core
    core.run()

if __name__ == "__main__":
    main()