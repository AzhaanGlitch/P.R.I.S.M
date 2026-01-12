import pyttsx3
from dotenv import dotenv_values
import threading
import os

env_vars = dotenv_values(".env")
VoiceRate = int(env_vars.get("VoiceRate", "190"))  # Faster default (was 180)
VoiceVolume = float(env_vars.get("VoiceVolume", "1.0"))

# Initialize engine once globally
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

# Voice selection
selected_voice = None
voice_preferences = ['david', 'zira', 'microsoft david', 'microsoft zira']

for pref in voice_preferences:
    matching_voices = [v for v in voices if pref in v.name.lower()]
    if matching_voices:
        selected_voice = matching_voices[0]
        break

if selected_voice:
    engine.setProperty('voice', selected_voice.id)
    print(f"Voice: {selected_voice.name}")
else:
    engine.setProperty('voice', voices[0].id if voices else None)
    print(f"Voice: {voices[0].name if voices else 'Default'}")

engine.setProperty('rate', VoiceRate)
engine.setProperty('volume', VoiceVolume)

# Thread lock
engine_lock = threading.Lock()

# File paths for mic control
MIC_FILE = "Frontend/Files/Mic.data"

def disable_mic():
    """Disable microphone before speaking"""
    try:
        os.makedirs("Frontend/Files", exist_ok=True)
        with open(MIC_FILE, 'w') as f:
            f.write('0')
    except:
        pass

def enable_mic():
    """Re-enable microphone after speaking"""
    try:
        with open(MIC_FILE, 'w') as f:
            f.write('1')
    except:
        pass

def Speak(Text):
    """Optimized speech with mic control"""
    try:
        if not Text or not Text.strip():
            return False
        
        # Clean text
        Text = Text.replace("P.R.I.S.M", "Prism")
        Text = Text.replace("PRISM", "Prism")
        Text = Text.replace("P.R.I.S.M.", "Prism")
        
        print(f"Speaking: {Text}")
        
        # CRITICAL: Disable mic before speaking
        disable_mic()
        
        with engine_lock:
            engine.say(Text)
            engine.runAndWait()
        
        # Re-enable mic after speaking
        import time
        time.sleep(0.2)  # Small delay for safety
        enable_mic()
        
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        enable_mic()  # Ensure mic is re-enabled on error
        return False

def SpeakWithoutPrint(Text):
    """Silent speech (no console output)"""
    try:
        if not Text or not Text.strip():
            return False
        
        Text = Text.replace("P.R.I.S.M", "Prism")
        Text = Text.replace("PRISM", "Prism")
        Text = Text.replace("P.R.I.S.M.", "Prism")
        
        disable_mic()
        
        with engine_lock:
            engine.say(Text)
            engine.runAndWait()
        
        import time
        time.sleep(0.2)
        enable_mic()
        
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        enable_mic()
        return False

def SpeakAsync(Text):
    """Non-blocking speech"""
    thread = threading.Thread(target=Speak, args=(Text,), daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    Speak("Prism is online and ready, sir.")
    
    while True:
        text = input("\nEnter text to speak (or 'exit'): ")
        if text.lower() in ['exit', 'quit', 'bye']:
            Speak("Goodbye sir.")
            break
        Speak(text)