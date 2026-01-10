import tkinter as tk
from tkinter import Menu
import threading
import time
import os
import math
import random
from PIL import Image, ImageTk, ImageDraw
import sys

class PrismSystemTray:
    def __init__(self, root, core_instance=None):
        self.root = root
        self.core = core_instance
        self.root.title("P.R.I.S.M")
        
        # Make window frameless and always on top
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 1.0)
        
        # Smaller orb with more padding from corners/taskbar
        self.orb_size = 160
        padding_right = 60
        padding_bottom = 120
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x_pos = screen_width - self.orb_size - padding_right
        y_pos = screen_height - self.orb_size - padding_bottom
        
        self.root.geometry(f'{self.orb_size}x{self.orb_size}+{x_pos}+{y_pos}')
        self.root.configure(bg='black')
        
        # Make background transparent (Windows)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        # Center for drawing
        self.center_x = self.orb_size // 2
        self.center_y = self.center_x
        self.max_visual_radius = self.orb_size // 2 - 10  # Safety buffer to prevent clipping
        
        # Animation variables (scaled down for smaller orb)
        self.angle = 0
        self.current_radius = 28
        self.base_radius = 28
        self.listening_radius = 45
        self.target_radius = self.base_radius
        self.rotation_speed = 0.015
        self.normal_speed = 0.015
        self.listening_speed = 0.03
        self.listening = False
        self.expanded = False
        
        # Effects
        self.particles = []
        self.ripples = []
        
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
        self.create_context_menu()
        self.init_particles()
        self.start_monitoring()
        self.animate()
        
        # Allow dragging
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag)
        self.root.bind('<Double-Button-1>', self.toggle_expand)
        
    def setup_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=self.orb_size,
            height=self.orb_size,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def init_particles(self):
        for _ in range(20):
            self.particles.append({
                'angle': random.uniform(0, math.pi * 2),
                'distance': random.uniform(35, 75),
                'speed': random.uniform(0.01, 0.03),
                'size': random.uniform(1, 2.5),
                'orbit_offset': random.uniform(0, math.pi * 2)
            })
    
    def create_context_menu(self):
        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="Open Full Interface", command=self.open_full_gui)
        self.menu.add_command(label="Start Listening", command=self.start_listening)
        self.menu.add_command(label="Stop Listening", command=self.stop_listening)
        self.menu.add_separator()
        self.menu.add_command(label="Settings", command=self.open_settings)
        self.menu.add_command(label="Exit P.R.I.S.M", command=self.exit_app)
        
        self.canvas.bind('<Button-3>', self.show_menu)
        
    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def draw_particles(self):
        for particle in self.particles:
            particle['angle'] += particle['speed']
            orbit_angle = particle['angle'] + particle['orbit_offset']
            
            x = self.center_x + particle['distance'] * math.cos(orbit_angle)
            y = self.center_y + particle['distance'] * math.sin(orbit_angle)
            
            pulse = 0.8 + 0.2 * math.sin(self.angle * 5 + particle['orbit_offset'])
            size = particle['size'] * pulse
            
            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill='#00ffff',
                outline=''
            )
            
            if random.random() < 0.08:
                opacity = int(90 * pulse)
                color = f'#00{opacity:02x}ff'
                self.canvas.create_line(
                    self.center_x, self.center_y, x, y,
                    fill=color,
                    width=1
                )
    
    def draw_rotating_rings(self):
        num_rings = 5
        for i in range(num_rings):
            ring_offset = i * 8
            ring_radius = self.current_radius + ring_offset
            
            num_segments = 28
            segment_angle = (math.pi * 2) / num_segments
            rotation = self.angle * (1 + i * 0.18)
            
            fade = 1 - (i / float(num_rings))
            opacity_base = int(80 + 175 * fade)
            
            for j in range(num_segments):
                if (j + i) % 3 == 0 or (j + i) % 5 == 0:
                    angle_start = rotation + j * segment_angle
                    angle_end = angle_start + segment_angle * 0.75
                    
                    x1 = self.center_x + ring_radius * math.cos(angle_start)
                    y1 = self.center_y + ring_radius * math.sin(angle_start)
                    x2 = self.center_x + ring_radius * math.cos(angle_end)
                    y2 = self.center_y + ring_radius * math.sin(angle_end)
                    
                    opacity = max(0, min(255, opacity_base - j * 4))
                    color = f'#00{opacity:02x}ff'
                    
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color,
                        width=1
                    )
    
    def draw_ripples(self):
        if self.listening and random.random() < 0.3:  # More frequent ripples in small orb
            self.ripples.append({'radius': 0, 'alpha': 1.0})
        
        to_remove = []
        for ripple in self.ripples:
            ripple['radius'] += 6
            ripple['alpha'] -= 0.05
            
            if ripple['alpha'] <= 0 or ripple['radius'] > self.max_visual_radius:
                to_remove.append(ripple)
                continue
            
            opacity = int(255 * ripple['alpha'])
            color = f'#00{opacity:02x}ff'
            r = ripple['radius']
            self.canvas.create_oval(
                self.center_x - r, self.center_y - r,
                self.center_x + r, self.center_y + r,
                outline=color,
                width=2
            )
        
        for r in to_remove:
            self.ripples.remove(r)
    
    def draw_core_sphere(self):
        layers = 7
        for i in range(layers, 0, -1):
            rad = self.current_radius * 0.5 * (i / layers)
            opacity = int(40 + 215 * (i / layers))
            opacity = max(0, min(255, opacity))
            
            if i > layers * 0.7:
                color = f'#{opacity:02x}{opacity:02x}ff'
            else:
                color = f'#00{opacity:02x}ff'
            
            self.canvas.create_oval(
                self.center_x - rad, self.center_y - rad,
                self.center_x + rad, self.center_y + rad,
                fill=color,
                outline=''
            )
        
        # Bright pulsing center
        core_radius = 10 + 6 * math.sin(self.angle * 4)
        self.canvas.create_oval(
            self.center_x - core_radius, self.center_y - core_radius,
            self.center_x + core_radius, self.center_y + core_radius,
            fill='#ffffff',
            outline='#00ffff',
            width=2
        )
    
    def animate(self):
        self.canvas.delete("all")
        
        # Smooth radius transition
        self.current_radius += (self.target_radius - self.current_radius) * 0.12
        
        # Draw layers
        self.draw_particles()
        self.draw_rotating_rings()
        self.draw_ripples()
        self.draw_core_sphere()
        
        # Update angle
        self.angle += self.rotation_speed
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
        
        self.root.after(16, self.animate)
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y
        
    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_expand(self, event):
        if self.expanded:
            self.root.geometry(f'{self.orb_size}x{self.orb_size}')
            self.expanded = False
        else:
            self.open_full_gui()
    
    def open_full_gui(self):
        try:
            full_gui_window = tk.Toplevel(self.root)
            from Frontend.GUI import VoiceAssistantGUI
            VoiceAssistantGUI(full_gui_window)
        except Exception as e:
            print(f"Could not open full GUI: {e}")
    
    def start_listening(self):
        self.write_file('mic', '1')
        self.listening = True
        self.target_radius = self.listening_radius
        self.rotation_speed = self.listening_speed
    
    def stop_listening(self):
        self.write_file('mic', '0')
        self.listening = False
        self.target_radius = self.base_radius
        self.rotation_speed = self.normal_speed
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("P.R.I.S.M Settings")
        settings_window.geometry("400x300")
        
        tk.Label(settings_window, text="Settings", font=('Arial', 16, 'bold')).pack(pady=20)
        tk.Label(settings_window, text="Feature coming soon...").pack()
        
        tk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)
    
    def exit_app(self):
        if self.core:
            self.core.running = False
        self.write_file('status', 'Shutting down...')
        self.root.quit()
        sys.exit(0)
    
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
                    status = self.read_file('status')
                    if status != last_status:
                        if status and ('listening' in status.lower() or 'processing' in status.lower()):
                            self.listening = True
                            self.target_radius = self.listening_radius
                            self.rotation_speed = self.listening_speed
                        else:
                            self.listening = False
                            self.target_radius = self.base_radius
                            self.rotation_speed = self.normal_speed
                        
                        last_status = status
                    
                    time.sleep(0.1)
                except Exception as e:
                    time.sleep(1)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

def main(core_instance=None):
    root = tk.Tk()
    app = PrismSystemTray(root, core_instance)
    root.mainloop()

if __name__ == "__main__":
    main()