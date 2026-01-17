import os
import pyautogui
import webbrowser
import subprocess
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

# Common application paths 
APP_PATHS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "vscode": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
    "spotify": r"C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe".format(os.getenv('USERNAME')),
    "discord": r"C:\Users\{}\AppData\Local\Discord\Update.exe".format(os.getenv('USERNAME')),
}

# Common websites
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "twitter": "https://twitter.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "stackoverflow": "https://stackoverflow.com",
}

def OpenApplication(app_name):
    """Open an application by name"""
    try:
        app_name_lower = app_name.lower().strip()
        if app_name_lower in APP_PATHS:
            app_path = APP_PATHS[app_name_lower]
            if os.path.exists(app_path):
                subprocess.Popen(app_path)
                return f"Opening {app_name}..."
            else:
                return f"Application path not found: {app_path}"
        
        try:
            subprocess.Popen(app_name_lower)
            return f"Opening {app_name}..."
        except:
            return f"Could not find application: {app_name}"
            
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def CloseApplication(app_name):
    """Close an application by name"""
    try:
        app_name_lower = app_name.lower().strip()
        
        if os.name == 'nt':
            process_names = {
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "notepad": "notepad.exe",
                "calculator": "calculator.exe",
                "vscode": "Code.exe",
                "spotify": "Spotify.exe",
                "discord": "Discord.exe",
            }
            
            process_name = process_names.get(app_name_lower, f"{app_name_lower}.exe")
            os.system(f'taskkill /F /IM {process_name}')
            return f"Closed {app_name}"
        else:
            # For Linux/Mac (optional)
            os.system(f'pkill -f {app_name_lower}')
            return f"Closed {app_name}"
            
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def OpenWebsite(website_name):
    """Open a website in the default browser"""
    try:
        website_lower = website_name.lower().strip()
        
        if website_lower in WEBSITES:
            url = WEBSITES[website_lower]
        elif website_lower.startswith("http"):
            url = website_lower
        else:
            url = f"https://www.{website_lower}.com"
        
        webbrowser.open(url)
        return f"Opening {website_name}..."
        
    except Exception as e:
        return f"Error opening website: {str(e)}"

def GoogleSearch(query):
    """Search Google for a query"""
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searching Google for: {query}"
    except Exception as e:
        return f"Error performing Google search: {str(e)}"

def YoutubeSearch(query):
    """Search YouTube for a query"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searching YouTube for: {query}"
    except Exception as e:
        return f"Error performing YouTube search: {str(e)}"

def PlayMusic(song_name):
    """Play music on YouTube"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}+song"
        webbrowser.open(search_url)
        return f"Playing: {song_name}"
    except Exception as e:
        return f"Error playing music: {str(e)}"

def VolumeUp():
    """Increase system volume"""
    try:
        if os.name == 'nt':  # Windows
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = min(current_volume + 0.1, 1.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            return f"Volume increased to {int(new_volume * 100)}%"
        else:
            os.system("amixer -D pulse sset Master 10%+")
            return "Volume increased"
    except Exception as e:
        return f"Error adjusting volume: {str(e)}"

def VolumeDown():
    """Decrease system volume"""
    try:
        if os.name == 'nt':  # Windows
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = max(current_volume - 0.1, 0.0)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            return f"Volume decreased to {int(new_volume * 100)}%"
        else:
            os.system("amixer -D pulse sset Master 10%-")
            return "Volume decreased"
    except Exception as e:
        return f"Error adjusting volume: {str(e)}"

def Mute():
    """Mute system volume"""
    try:
        if os.name == 'nt':  # Windows
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)
            return "System muted"
        else:
            os.system("amixer -D pulse sset Master mute")
            return "System muted"
    except Exception as e:
        return f"Error muting: {str(e)}"

def Unmute():
    """Unmute system volume"""
    try:
        if os.name == 'nt':  # Windows
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)
            return "System unmuted"
        else:
            os.system("amixer -D pulse sset Master unmute")
            return "System unmuted"
    except Exception as e:
        return f"Error unmuting: {str(e)}"

def Screenshot(filename="screenshot.png"):
    """Take a screenshot"""
    try:
        screenshot = pyautogui.screenshot()
        if not os.path.exists("Screenshots"):
            os.makedirs("Screenshots")
        filepath = os.path.join("Screenshots", filename)
        screenshot.save(filepath)
        return f"Screenshot saved to {filepath}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

if __name__ == "__main__":
    print("=" * 50)
    print("Automation System Test")
    print("=" * 50)
    print("\nAvailable commands:")
    print("1. open <app/website>")
    print("2. close <app>")
    print("3. search <query>")
    print("4. play <song>")
    print("5. volume up/down")
    print("6. mute/unmute")
    print("7. screenshot")
    print("8. exit")
    print("=" * 50)
    
    while True:
        command = input("\nEnter command: ").strip().lower()
        
        if command == "exit":
            break
        elif command.startswith("open "):
            app = command.replace("open ", "")
            print(OpenApplication(app))
        elif command.startswith("close "):
            app = command.replace("close ", "")
            print(CloseApplication(app))
        elif command.startswith("search "):
            query = command.replace("search ", "")
            print(GoogleSearch(query))
        elif command.startswith("play "):
            song = command.replace("play ", "")
            print(PlayMusic(song))
        elif command == "volume up":
            print(VolumeUp())
        elif command == "volume down":
            print(VolumeDown())
        elif command == "mute":
            print(Mute())
        elif command == "unmute":
            print(Unmute())
        elif command == "screenshot":
            print(Screenshot())
        else:
            print("Unknown command")