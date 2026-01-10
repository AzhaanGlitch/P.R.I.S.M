import pyttsx3
from dotenv import dotenv_values
import threading

env_vars = dotenv_values(".env")
VoiceRate = int(env_vars.get("VoiceRate", "180"))  # Faster default
VoiceVolume = float(env_vars.get("VoiceVolume", "1.0"))

# Initialize engine once globally for faster performance
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

# Voice selection priority: David (UK) > Zira (US Female) > Default
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
    # Use first available voice
    engine.setProperty('voice', voices[0].id if voices else None)
    print(f"Voice: {voices[0].name if voices else 'Default'}")

engine.setProperty('rate', VoiceRate)
engine.setProperty('volume', VoiceVolume)

# Thread lock for engine access
engine_lock = threading.Lock()

def Speak(Text):
    """Optimized speech function with threading support"""
    try:
        if not Text or not Text.strip():
            return False
        
        # Remove "P.R.I.S.M" and replace with "Prism"
        Text = Text.replace("P.R.I.S.M", "Prism")
        Text = Text.replace("PRISM", "Prism")
        Text = Text.replace("P.R.I.S.M.", "Prism")
        
        print(f"Speaking: {Text}")
        
        with engine_lock:
            engine.say(Text)
            engine.runAndWait()
        
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        return False

def SpeakWithoutPrint(Text):
    """Silent speech (no console output)"""
    try:
        if not Text or not Text.strip():
            return False
        
        # Replace PRISM variations
        Text = Text.replace("P.R.I.S.M", "Prism")
        Text = Text.replace("PRISM", "Prism")
        Text = Text.replace("P.R.I.S.M.", "Prism")
        
        with engine_lock:
            engine.say(Text)
            engine.runAndWait()
        
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
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