import pyttsx3
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
VoiceRate = int(env_vars.get("VoiceRate", "160"))  # Calmer rate for JARVIS-like feel
VoiceVolume = float(env_vars.get("VoiceVolume", "1.0"))

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

# Only try to select George (British male voice - closest to JARVIS)
george_voices = [voice for voice in voices if 'george' in voice.name.lower()]
if george_voices:
    engine.setProperty('voice', george_voices[0].id)
    print(f"Selected voice: {george_voices[0].name}")
else:
    engine.setProperty('voice', voices[0].id)
    print(f"George not found - using default voice: {voices[0].name}")

engine.setProperty('rate', VoiceRate)
engine.setProperty('volume', VoiceVolume)

def Speak(Text):
    try:
        if Text and Text.strip():
            print(f"Speaking: {Text}")
            engine.say(Text)
            engine.runAndWait()
            return True
        return False
    except Exception as e:
        print(f"TTS Error: {e}")
        return False

def SpeakWithoutPrint(Text):
    try:
        if Text and Text.strip():
            engine.say(Text)
            engine.runAndWait()
            return True
        return False
    except Exception as e:
        print(f"TTS Error: {e}")
        return False

if __name__ == "__main__":
    Speak("Hello sir, I am Prism, your personal AI assistant. All systems are online and ready.")
    
    while True:
        text = input("\nEnter text to speak (or 'exit' to quit): ")
        if text.lower() in ['exit', 'quit', 'bye']:
            Speak("Goodbye sir. Shutting down systems.")
            break
        Speak(text)