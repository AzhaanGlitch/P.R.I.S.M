import os
import sys
import threading
import time
from datetime import datetime
import queue

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
        self.gui_mode = gui_mode
        self.files = {
            'status': 'Frontend/Files/Status.data',
            'mic': 'Frontend/Files/Mic.data',
        }
        
        # Command queue for async processing
        self.command_queue = queue.Queue()
        self.is_processing = False
        self.processing_lock = threading.Lock()
        
        # Ensure directories exist
        os.makedirs('Frontend/Files', exist_ok=True)
        os.makedirs('Data', exist_ok=True)
        
        # Initialize files
        for file_path in self.files.values():
            if not os.path.exists(file_path):
                open(file_path, 'w').close()
        
        self.write_file('status', 'Initializing...')
        self.write_file('mic', '1')
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
        """Main query processing logic - now with faster execution"""
        if not query or len(query.strip()) < 2:
            return
        
        with self.processing_lock:
            if self.is_processing:
                print("[BUSY]: Already processing a command, queuing...")
                return
            self.is_processing = True
        
        try:
            print(f"\n[USER SAID]: {query}")
            self.write_file('status', 'Processing...')
            
            # Get decision from Model
            tasks = FirstLayerDMM(query)
            print(f"[TASKS]: {tasks}")
            
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
                    print(f"[PRISM]: {response}")
                    self.write_file('status', 'Speaking...')
                    
                    # CRITICAL: Disable mic BEFORE speaking
                    self.write_file('mic', '0')
                    time.sleep(0.1)  # Let mic disable
                    
                    Speak(response)
                    
                    # Re-enable mic AFTER speaking
                    time.sleep(0.3)
                    self.write_file('mic', '1')
                    
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[ERROR]: {error_msg}")
            self.write_file('status', 'Error - Ready')
        
        finally:
            with self.processing_lock:
                self.is_processing = False
            self.write_file('status', 'Listening...')
    
    def command_processor_thread(self):
        """Background thread to process commands from queue"""
        while self.running:
            try:
                # Get command with timeout
                query = self.command_queue.get(timeout=1)
                if query:
                    self.process_query(query)
                self.command_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processor error: {e}")
    
    def monitor_voice_input(self):
        """Monitor for voice input - OPTIMIZED"""
        print("[VOICE MONITOR]: Starting...")
        
        # Start SpeechToText in separate process
        voice_thread = threading.Thread(target=self.run_speech_to_text, daemon=True)
        voice_thread.start()
        
        # Start command processor
        processor = threading.Thread(target=self.command_processor_thread, daemon=True)
        processor.start()
        
        voice_file = "Data/VoiceInput.txt"
        last_query = ""
        last_process_time = 0
        
        while self.running:
            try:
                # Check mic status
                mic_status = self.read_file('mic')
                if mic_status != '1':
                    time.sleep(0.3)
                    continue
                
                # Don't check if currently processing
                if self.is_processing:
                    time.sleep(0.2)
                    continue
                
                # Read voice input
                if os.path.exists(voice_file):
                    with open(voice_file, 'r') as f:
                        query = f.read().strip()
                    
                    current_time = time.time()
                    
                    # Process if: new query AND not duplicate AND sufficient time passed
                    if (query and 
                        query != last_query and 
                        len(query) > 2 and
                        (current_time - last_process_time) > 2):  # 2 second cooldown
                        
                        print(f"[DETECTED]: {query}")
                        
                        # Clear file immediately
                        with open(voice_file, 'w') as f:
                            f.write("")
                        
                        # Queue command for processing
                        self.command_queue.put(query)
                        
                        last_query = query
                        last_process_time = current_time
                
                time.sleep(0.15)  # Fast polling
                
            except Exception as e:
                print(f"Voice monitoring error: {e}")
                time.sleep(1)
    
    def run_speech_to_text(self):
        """Run the speech to text module"""
        try:
            from Backend import SpeechToText
            print("[SPEECH-TO-TEXT]: Running...")
        except Exception as e:
            print(f"[ERROR]: Could not start speech recognition: {e}")
    
    def console_input_monitor(self):
        """Monitor console for text commands"""
        if self.gui_mode == 'tray':
            while self.running:
                time.sleep(1)
            return
        
        print("[CONSOLE]: Type commands or 'exit' to quit")
        
        while self.running:
            try:
                user_input = input("\n[CMD]: ").strip()
                
                if user_input:
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        self.process_query("exit")
                        break
                    elif user_input.lower() == 'help':
                        print("\nCommands:")
                        print("- Questions: 'how are you', 'what is AI'")
                        print("- Real-time: 'weather', 'latest news'")
                        print("- Automation: 'open chrome', 'play music'")
                        print("- Search: 'search python', 'youtube cats'")
                        print("- Exit: 'exit', 'quit'")
                    else:
                        self.command_queue.put(user_input)
                        
            except KeyboardInterrupt:
                print("\n[SHUTDOWN]...")
                self.running = False
                break
            except Exception as e:
                print(f"[ERROR]: {e}")
    
    def run(self):
        """Main run loop"""
        print("\n" + "="*70)
        print("P.R.I.S.M - Personal Responsive Intelligence System Manager")
        print("="*70)
        print("\n[SYSTEM]: Starting voice assistant...")
        print("[SYSTEM]: Speak commands or use system tray.")
        print("[SYSTEM]: Press Ctrl+C to exit.\n")
        
        # Start voice monitor
        voice_thread = threading.Thread(target=self.monitor_voice_input, daemon=True)
        voice_thread.start()
        
        # Set status
        self.write_file('status', 'Listening...')
        
        # Greeting
        Speak("P.R.I.S.M is online and ready, sir.")
        time.sleep(0.5)
        self.write_file('mic', '1')  # Ensure mic is on after greeting
        
        print("[SYSTEM]: Listening...\n")
        
        # Console input
        self.console_input_monitor()
        
        # Shutdown
        print("\n[SHUTDOWN]: Closing P.R.I.S.M...")
        self.write_file('status', 'Shutting down...')
        self.write_file('mic', '0')
        Speak("Goodbye sir.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='P.R.I.S.M Voice Assistant')
    parser.add_argument('--mode', choices=['tray', 'full', 'console'], default='tray',
                       help='GUI mode: tray (system tray), full (fullscreen), console (no GUI)')
    args = parser.parse_args()
    
    # Start core
    core = PrismVoiceCore(gui_mode=args.mode)
    
    # Start GUI
    try:
        if args.mode == 'tray':
            from Frontend.SystemTrayGUI import main as tray_main
            gui_thread = threading.Thread(target=lambda: tray_main(core), daemon=False)
            gui_thread.start()
            print("[GUI]: System tray launched.")
            
        elif args.mode == 'full':
            from Frontend.GUI import main as gui_main
            gui_thread = threading.Thread(target=gui_main, daemon=False)
            gui_thread.start()
            print("[GUI]: Full interface launched.")
        
        else:
            print("[MODE]: Console only.")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"[WARNING]: GUI error: {e}")
        print("[MODE]: Console fallback.")
    
    # Run core
    core.run()

if __name__ == "__main__":
    main()