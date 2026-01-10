import tkinter as tk
import threading
import time
import os
import math
import random

class JarvisStyleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Prism")
        
        # Fullscreen setup
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.close_app())
        
        # Get screen dimensions FIRST
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Calculate center BEFORE using it
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Animation variables
        self.angle = 0
        self.rotation_speed = 0.015  # Reduced from 0.03 (slower rotation)
        self.base_radius = 80  # Reduced from 150 (smaller orb)
        self.current_radius = self.base_radius
        self.target_radius = self.base_radius
        self.listening = False
        self.running = True
        
        # Particle system
        self.particles = []
        
        # Hexagon grid
        self.hexagons = []
        
        # Ripple effects
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
        
        # Setup UI first
        self.setup_ui()
        
        # Now initialize particles and hexagons
        self.init_particles()
        self.init_hexagons()
        
        self.write_file('mic', '1')
        self.start_monitoring()
        self.animate()
        
    def setup_ui(self):
        """Setup the main canvas"""
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def init_particles(self):
        """Initialize floating particles"""
        for _ in range(40):
            self.particles.append({
                'angle': random.uniform(0, math.pi * 2),
                'distance': random.uniform(200, 400),
                'speed': random.uniform(0.005, 0.02),
                'size': random.uniform(1, 3),
                'orbit_offset': random.uniform(0, math.pi * 2)
            })
    
    def init_hexagons(self):
        """Initialize hexagon grid pattern"""
        hex_size = 40
        for i in range(-3, 4):
            for j in range(-3, 4):
                x = self.center_x + i * hex_size * 1.5
                y = self.center_y + j * hex_size * math.sqrt(3)
                if j % 2 != 0:
                    x += hex_size * 0.75
                
                distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
                if distance < 350:
                    self.hexagons.append({
                        'x': x,
                        'y': y,
                        'size': hex_size * 0.5,
                        'phase': random.uniform(0, math.pi * 2)
                    })
    
    def draw_hexagon(self, x, y, size, alpha=1.0):
        """Draw a single hexagon"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend([px, py])
        
        # Calculate opacity - ensure valid range
        opacity = max(0, min(255, int(255 * alpha)))
        color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
        
        if len(points) >= 4:
            self.canvas.create_polygon(points, outline=color, fill='', width=1)
    
    def draw_rotating_rings(self):
        """Draw multiple rotating rings like JARVIS"""
        num_rings = 8
        
        for i in range(num_rings):
            ring_offset = i * 25
            ring_radius = self.current_radius + ring_offset
            
            # Rotating segments
            num_segments = 32
            segment_angle = (math.pi * 2) / num_segments
            
            for j in range(num_segments):
                # Calculate rotation with offset per ring
                angle_start = self.angle * (1 + i * 0.2) + j * segment_angle
                angle_end = angle_start + segment_angle * 0.7
                
                # Only draw some segments (broken ring effect)
                if (j + i) % 3 == 0 or (j + i) % 5 == 0:
                    x1 = self.center_x + ring_radius * math.cos(angle_start)
                    y1 = self.center_y + ring_radius * math.sin(angle_start)
                    x2 = self.center_x + ring_radius * math.cos(angle_end)
                    y2 = self.center_y + ring_radius * math.sin(angle_end)
                    
                    # Fade based on distance - ensure valid range
                    fade = max(0, min(1, 1 - (i / num_rings)))
                    opacity = max(0, min(255, int(100 + 155 * fade)))
                    
                    # Cyan color with proper bounds
                    r = opacity
                    g = max(0, min(255, opacity + 50))
                    b = 255
                    color = f'#{r:02x}{g:02x}{b:02x}'
                    
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color,
                        width=2,
                        smooth=True
                    )
    
    def draw_orbit_rings(self):
        """Draw orbiting rings at different angles"""
        num_orbits = 5
        
        for i in range(num_orbits):
            orbit_radius = self.current_radius + 50
            tilt = (i / num_orbits) * math.pi
            rotation_offset = self.angle * (1 + i * 0.3)
            
            # Draw elliptical orbit
            points = []
            segments = 60
            
            for j in range(segments + 1):
                angle = (j / segments) * math.pi * 2 + rotation_offset
                
                x = orbit_radius * math.cos(angle)
                y = orbit_radius * math.sin(angle) * math.cos(tilt)
                z = orbit_radius * math.sin(angle) * math.sin(tilt)
                
                # 3D to 2D projection
                scale = 1 / (1 + z / 1000)
                screen_x = self.center_x + x * scale
                screen_y = self.center_y + y * scale
                
                points.append((screen_x, screen_y))
            
            # Draw the orbit
            for j in range(len(points) - 1):
                opacity = max(0, min(255, int(50 + 50 * (1 - i / num_orbits))))
                g_val = opacity
                b_val = max(0, min(255, opacity + 100))
                color = f'#00{g_val:02x}{b_val:02x}'
                
                self.canvas.create_line(
                    points[j][0], points[j][1],
                    points[j+1][0], points[j+1][1],
                    fill=color,
                    width=1,
                    smooth=True
                )
    
    def draw_particles(self):
        """Draw floating particles"""
        for particle in self.particles:
            # Update particle position
            particle['angle'] += particle['speed']
            orbit_angle = particle['angle'] + particle['orbit_offset']
            
            x = self.center_x + particle['distance'] * math.cos(orbit_angle)
            y = self.center_y + particle['distance'] * math.sin(orbit_angle)
            
            # Pulsing effect
            pulse = 0.5 + 0.5 * math.sin(self.angle * 3 + particle['orbit_offset'])
            size = particle['size'] * pulse
            
            # Draw particle
            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill='#00ffff',
                outline=''
            )
            
            # Draw connection line to center (sometimes)
            if random.random() < 0.1:
                opacity = max(0, min(255, int(50 * pulse)))
                color = f'#00{opacity:02x}{opacity:02x}'
                self.canvas.create_line(
                    x, y, self.center_x, self.center_y,
                    fill=color,
                    width=1
                )
    
    def draw_hexagon_grid(self):
        """Draw animated hexagon grid in background"""
        for hex_data in self.hexagons:
            distance = math.sqrt(
                (hex_data['x'] - self.center_x)**2 + 
                (hex_data['y'] - self.center_y)**2
            )
            
            # Pulse based on distance from center
            pulse = math.sin(self.angle * 2 - distance / 50 + hex_data['phase'])
            alpha = max(0, min(1, 0.1 + 0.15 * pulse))
            
            # Only draw if visible
            if alpha > 0.05:
                self.draw_hexagon(hex_data['x'], hex_data['y'], hex_data['size'], alpha)
    
    def draw_core_sphere(self):
        """Draw the central bright sphere"""
        # Multiple layers for depth
        layers = 8
        
        for i in range(layers, 0, -1):
            radius = (self.current_radius * 0.4) * (i / layers)
            opacity = max(0, min(255, int(50 + (205 * (i / layers)))))
            
            # Bright cyan/white gradient
            if i > layers * 0.7:
                color = f'#{opacity:02x}{opacity:02x}{255:02x}'
            else:
                color = f'#00{opacity:02x}{255:02x}'
            
            self.canvas.create_oval(
                self.center_x - radius,
                self.center_y - radius,
                self.center_x + radius,
                self.center_y + radius,
                fill=color,
                outline=''
            )
        
        # Bright center
        core_radius = 20 + 10 * math.sin(self.angle * 3)
        self.canvas.create_oval(
            self.center_x - core_radius,
            self.center_y - core_radius,
            self.center_x + core_radius,
            self.center_y + core_radius,
            fill='#ffffff',
            outline='#00ffff',
            width=2
        )
    
    def draw_ripples(self):
        """Draw expanding ripples when listening"""
        if self.listening and random.random() < 0.1:
            self.ripples.append({'radius': 0, 'alpha': 1.0})
        
        # Update and draw ripples
        for ripple in self.ripples[:]:
            ripple['radius'] += 8
            ripple['alpha'] -= 0.03
            
            if ripple['alpha'] <= 0:
                self.ripples.remove(ripple)
            else:
                opacity = max(0, min(255, int(255 * ripple['alpha'])))
                color = f'#00{opacity:02x}{255:02x}'
                
                self.canvas.create_oval(
                    self.center_x - ripple['radius'],
                    self.center_y - ripple['radius'],
                    self.center_x + ripple['radius'],
                    self.center_y + ripple['radius'],
                    outline=color,
                    width=2,
                    fill=''
                )
    
    def draw_data_streams(self):
        """Draw flowing data streams around the orb"""
        num_streams = 12
        
        for i in range(num_streams):
            angle_offset = (i / num_streams) * math.pi * 2
            stream_angle = self.angle * 2 + angle_offset
            
            # Stream path
            distance = self.current_radius + 100
            x = self.center_x + distance * math.cos(stream_angle)
            y = self.center_y + distance * math.sin(stream_angle)
            
            # Draw small moving dots
            for j in range(3):
                dot_offset = j * 20
                dx = x + dot_offset * math.cos(stream_angle)
                dy = y + dot_offset * math.sin(stream_angle)
                
                size = 3 - j
                opacity = max(0, min(255, int(255 - j * 80)))
                color = f'#00{opacity:02x}{255:02x}'
                
                self.canvas.create_oval(
                    dx - size, dy - size,
                    dx + size, dy + size,
                    fill=color,
                    outline=''
                )
    
    def animate(self):
        """Main animation loop - JARVIS style"""
        if not self.running:
            return
        
        self.canvas.delete("all")
        
        # Smooth radius transition
        self.current_radius += (self.target_radius - self.current_radius) * 0.08
        
        # Layer 1: Background hexagon grid
        self.draw_hexagon_grid()
        
        # Layer 2: Orbiting particles
        self.draw_particles()
        
        # Layer 3: Orbit rings
        self.draw_orbit_rings()
        
        # Layer 4: Rotating segmented rings
        self.draw_rotating_rings()
        
        # Layer 5: Ripple effects
        self.draw_ripples()
        
        # Layer 6: Data streams
        self.draw_data_streams()
        
        # Layer 7: Core sphere (on top)
        self.draw_core_sphere()
        
        # Update rotation
        self.angle += self.rotation_speed
        if self.angle > math.pi * 2:
            self.angle -= math.pi * 2
        
        # 60 FPS
        self.root.after(16, self.animate)
    
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
    
    def close_app(self):
        """Properly close the application"""
        print("[GUI]: Closing...")
        self.running = False
        self.root.quit()
        self.root.destroy()
    
    def start_monitoring(self):
        """Monitor status changes"""
        def monitor():
            last_status = ""
            
            while self.running:
                try:
                    status = self.read_file('status')
                    
                    if status and status != last_status:
                        # Check for shutdown
                        if 'shutdown' in status.lower() or 'goodbye' in status.lower():
                            print("[GUI]: Shutdown signal received")
                            self.root.after(2000, self.close_app)
                            break
                        
                        # Listening = larger orb with ripples
                        if 'listening' in status.lower() or 'processing' in status.lower():
                            self.listening = True
                            self.target_radius = self.base_radius + 100  # Increased expansion (was +80)
                            self.rotation_speed = 0.03  # Faster rotation when listening
                        else:
                            self.listening = False
                            self.target_radius = self.base_radius
                            self.rotation_speed = 0.015  # Normal slow rotation
                        
                        last_status = status
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    if self.running:
                        print(f"Monitoring error: {e}")
                    time.sleep(1)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = JarvisStyleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()