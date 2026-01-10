"""
Auto-start Configuration Script for P.R.I.S.M
This script sets up P.R.I.S.M to start automatically with Windows
"""

import os
import sys
import winreg
import ctypes

def is_admin():
    """Check if script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_to_startup_registry():
    """Add P.R.I.S.M to Windows startup registry"""
    try:
        # Get the path to the Python executable and Main.py
        python_exe = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, "Main.py")
        
        # Create the command with --mode tray for background operation
        startup_command = f'"{python_exe}" "{main_script}" --mode tray'
        
        # Open registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Set the value
        winreg.SetValueEx(key, "PRISM", 0, winreg.REG_SZ, startup_command)
        winreg.CloseKey(key)
        
        print("✅ P.R.I.S.M successfully added to Windows startup!")
        print(f"   Command: {startup_command}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding to startup: {e}")
        return False

def remove_from_startup_registry():
    """Remove P.R.I.S.M from Windows startup"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        try:
            winreg.DeleteValue(key, "PRISM")
            print("✅ P.R.I.S.M removed from Windows startup!")
        except FileNotFoundError:
            print("ℹ️  P.R.I.S.M was not found in startup registry")
        
        winreg.CloseKey(key)
        return True
        
    except Exception as e:
        print(f"❌ Error removing from startup: {e}")
        return False

def create_startup_shortcut():
    """Alternative method: Create shortcut in Startup folder"""
    try:
        import win32com.client
        
        shell = win32com.client.Dispatch("WScript.Shell")
        startup_folder = shell.SpecialFolders("Startup")
        
        shortcut_path = os.path.join(startup_folder, "PRISM.lnk")
        shortcut = shell.CreateShortcut(shortcut_path)
        
        # Set shortcut properties
        python_exe = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, "Main.py")
        
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{main_script}" --mode tray'
        shortcut.WorkingDirectory = script_dir
        shortcut.IconLocation = python_exe
        shortcut.Description = "P.R.I.S.M Voice Assistant"
        
        shortcut.Save()
        
        print("✅ Startup shortcut created successfully!")
        print(f"   Location: {shortcut_path}")
        return True
        
    except ImportError:
        print("⚠️  pywin32 not installed. Using registry method instead.")
        print("   Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        return False

def check_startup_status():
    """Check if P.R.I.S.M is in startup"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        
        try:
            value, _ = winreg.QueryValueEx(key, "PRISM")
            print("✅ P.R.I.S.M is currently enabled in startup")
            print(f"   Command: {value}")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            print("ℹ️  P.R.I.S.M is NOT in startup")
            winreg.CloseKey(key)
            return False
            
    except Exception as e:
        print(f"❌ Error checking startup: {e}")
        return False

def create_vbs_launcher():
    """Create VBS launcher for silent startup"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        vbs_path = os.path.join(script_dir, "start_prism_silent.vbs")
        
        python_exe = sys.executable
        main_script = os.path.join(script_dir, "Main.py")
        
        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{python_exe}" & chr(34) & " " & chr(34) & "{main_script}" & chr(34) & " --mode tray", 0
Set WshShell = Nothing
'''
        
        with open(vbs_path, 'w') as f:
            f.write(vbs_content)
        
        print(f"✅ Silent launcher created: {vbs_path}")
        print("   This will start P.R.I.S.M without showing a console window")
        return vbs_path
        
    except Exception as e:
        print(f"❌ Error creating VBS launcher: {e}")
        return None

def add_vbs_to_startup():
    """Add VBS launcher to startup"""
    try:
        vbs_path = create_vbs_launcher()
        if not vbs_path:
            return False
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "PRISM", 0, winreg.REG_SZ, vbs_path)
        winreg.CloseKey(key)
        
        print("✅ VBS launcher added to startup!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main_menu():
    """Interactive menu for startup configuration"""
    print("\n" + "="*70)
    print("P.R.I.S.M - Auto-Start Configuration Tool")
    print("="*70)
    print("\nThis tool helps you configure P.R.I.S.M to start automatically with Windows.")
    print("\nOptions:")
    print("1. Enable auto-start (Registry method)")
    print("2. Enable auto-start (Silent VBS launcher - RECOMMENDED)")
    print("3. Enable auto-start (Startup folder shortcut)")
    print("4. Disable auto-start")
    print("5. Check current startup status")
    print("6. Exit")
    print("\n" + "="*70)
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            print("\n[Registry Method]")
            add_to_startup_registry()
            
        elif choice == '2':
            print("\n[VBS Silent Launcher Method - RECOMMENDED]")
            add_vbs_to_startup()
            
        elif choice == '3':
            print("\n[Startup Folder Shortcut Method]")
            result = create_startup_shortcut()
            if not result:
                print("\nFalling back to registry method...")
                add_to_startup_registry()
                
        elif choice == '4':
            print("\n[Removing from Startup]")
            remove_from_startup_registry()
            
        elif choice == '5':
            print("\n[Checking Startup Status]")
            check_startup_status()
            
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    print("\n🔒 Security Note:")
    print("   - This script only modifies YOUR user's startup settings")
    print("   - No admin privileges required")
    print("   - You can disable auto-start anytime using this tool")
    print("   - P.R.I.S.M will run in the background with a system tray icon")
    
    main_menu()