import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import os
import math
from PIL import Image, ImageTk, ImageDraw

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("P.R.I.S.M")
        
        # Fullscreen setup
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # Animation variables
        self.angle = 0
        self.pulse_radius = 100
        self.pulse_direction = 1
        self.listening = False
        self.is_speaking = False
        
        # File paths
        self.files = {
            'status': 'Frontend/Files/Status.data',
            'mic': 'Frontend/Files/Mic.data',
        }
        
        # Ensure directory exists
        os.makedirs('Frontend/Files', exist_ok=True)
        for file_path in self.files.values():
            if not os.path.exists(file_path):
                open(file_path, 'w').close()
        
        self.setup_ui()
        self.write_file('mic', '1')  # Start listening immediately
        self.start_monitoring()
        self.animate()
        
    def setup_ui(self):
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Main canvas for drawing
        self.canvas = tk.Canvas(
            self.root,
            width=screen_width,
            height=screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        
        # Status text at bottom
        self.status_label = tk.Label(
            self.root,
            text="Initializing...",
            font=('Segoe UI', 14),
            fg='#8000ff',
            bg='black'
        )
        self.status_label.place(relx=0.5, rely=0.9, anchor='center')
        
        # Title at top (optional, can be removed)
        self.title_label = tk.Label(
            self.root,
            text="P.R.I.S.M",
            font=('Orbitron', 28, 'bold'),
            fg='#8000ff',
            bg='black'
        )
        self.title_label.place(relx=0.5, rely=0.05, anchor='center')
        
    def draw_orb(self):
        self.canvas.delete("all")
        
        # Determine color based on state
        if self.is_speaking:
            # Speaking - Green pulsing
            base_color = (0, 255, 100)
            glow_color = '#00ff64'
        elif self.listening:
            # Listening - Purple/Blue pulsing
            base_color = (128, 0, 255)
            glow_color = '#8000ff'
        else:
            # Idle - Dim purple
            base_color = (80, 0, 120)
            glow_color = '#500078'
        
        # Pulsing effect
        pulse_offset = math.sin(self.angle * 2) * 20
        current_radius = self.pulse_radius + pulse_offset
        
        # Draw multiple glowing rings
        for i in range(8, 0, -1):
            radius = current_radius + (i * 15)
            opacity = 255 - (i * 25)
            
            # Calculate color with opacity
            r, g, b = base_color
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            self.canvas.create_oval(
                self.center_x - radius,
                self.center_y - radius,
                self.center_x + radius,
                self.center_y + radius,
                outline=color,
                width=3
            )
        
        # Rotating particles around the orb
        num_particles = 12
        particle_distance = current_radius + 60
        
        for i in range(num_particles):
            angle_offset = (2 * math.pi / num_particles) * i
            particle_angle = self.angle + angle_offset
            
            x = self.center_x + math.cos(particle_angle) * particle_distance
            y = self.center_y + math.sin(particle_angle) * particle_distance
            
            particle_size = 8 + math.sin(self.angle * 3 + i) * 3
            
            self.canvas.create_oval(
                x - particle_size,
                y - particle_size,
                x + particle_size,
                y + particle_size,
                fill=glow_color,
                outline=''
            )
        
        # Center core
        core_radius = 40 + math.sin(self.angle * 3) * 5
        self.canvas.create_oval(
            self.center_x - core_radius,
            self.center_y - core_radius,
            self.center_x + core_radius,
            self.center_y + core_radius,
            fill=glow_color,
            outline=''
        )
        
        # Inner glow
        inner_radius = 30
        self.canvas.create_oval(
            self.center_x - inner_radius,
            self.center_y - inner_radius,
            self.center_x + inner_radius,
            self.center_y + inner_radius,
            fill='#ffffff',
            outline=''
        )
        
    def animate(self):
        self.draw_orb()
        self.angle += 0.05
        
        # Keep angle in reasonable range
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
        
        self.root.after(30, self.animate)
        
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
            
    def start_monitoring(self):
        def monitor():
            last_status = ""
            
            while True:
                try:
                    # Monitor status changes
                    status = self.read_file('status')
                    if status and status != last_status:
                        # Update UI based on status
                        if 'listening' in status.lower() or 'ready' in status.lower():
                            self.listening = True
                            self.is_speaking = False
                            self.status_label.config(text="Listening...", fg='#8000ff')
                        elif 'processing' in status.lower() or 'thinking' in status.lower():
                            self.listening = True
                            self.is_speaking = False
                            self.status_label.config(text="Processing...", fg='#8000ff')
                        elif 'speaking' in status.lower() or 'responding' in status.lower():
                            self.listening = False
                            self.is_speaking = True
                            self.status_label.config(text="Speaking...", fg='#00ff64')
                        else:
                            self.status_label.config(text=status, fg='#8000ff')
                        
                        last_status = status
                    
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()