import subprocess
import sys
import platform
import time
import os
import keyboard
import threading
from datetime import datetime

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.system = platform.system().lower()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def clear_screen(self):
        os.system('cls' if self.system == 'windows' else 'clear')
        
    def display_header(self):
        self.clear_screen()
        print("=" * 50)
        print("       Multi-Logger Process Manager")
        print("=" * 50)
        print("\nControls:")
        print("  S - Start all loggers")
        print("  E - End all loggers")
        print("  Q - Quit program")
        print("\nStatus:")
        
    def launch_script(self, script_path):
        try:
            full_path = os.path.join(self.script_dir, script_path)
            if not os.path.exists(full_path):
                print(f"Error: Script not found at {full_path}")
                return False
                
            if self.system == 'windows':
                process = subprocess.Popen(['python', full_path], 
                                        creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif self.system in ['linux', 'darwin']:
                if self.system == 'darwin':  # macOS
                    terminal_script = os.path.join(self.script_dir, f'run_{script_path}.command')
                    with open(terminal_script, 'w') as f:
                        f.write(f'#!/bin/bash\ncd "{self.script_dir}"\npython3 "{script_path}"\n')
                    os.chmod(terminal_script, 0o755)
                    process = subprocess.Popen(['open', terminal_script])
                else:  # Linux
                    process = subprocess.Popen(['gnome-terminal', '--', 'python3', full_path])
            
            self.processes[script_path] = {
                'process': process,
                'start_time': datetime.now(),
                'status': 'Running'
            }
            return True
            
        except Exception as e:
            print(f"Error launching {script_path}: {e}")
            return False

    def stop_script(self, script_path):
        if script_path in self.processes:
            try:
                if self.system == 'windows':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', 
                                 str(self.processes[script_path]['process'].pid)])
                else:
                    self.processes[script_path]['process'].terminate()
                    
                if self.system == 'darwin':
                    # Clean up temporary script
                    temp_script = os.path.join(self.script_dir, f'run_{script_path}.command')
                    if os.path.exists(temp_script):
                        os.remove(temp_script)
                
                self.processes[script_path]['status'] = 'Stopped'
                return True
            except Exception as e:
                print(f"Error stopping {script_path}: {e}")
                return False
    
    def display_status(self):
        for script, info in self.processes.items():
            status = info['status']
            if status == 'Running':
                runtime = datetime.now() - info['start_time']
                runtime_str = str(runtime).split('.')[0]  # Remove microseconds
            else:
                runtime_str = "Not running"
            
            print(f"\n{os.path.basename(script)}:")
            print(f"  Status: {status}")
            print(f"  Runtime: {runtime_str}")
    
    def update_display(self):
        while self.running:
            self.display_header()
            self.display_status()
            time.sleep(1)
    
    def start_all(self):
        scripts = [
            # Change the name of the script to match the actual script name
            'PC_data_logger_MAC_dev_id_{Dev_1}.py', 
            'PC_data_logger_MAC_dev_id_{Dev_2}.py',
            'PC_data_logger_MAC_dev_id_{Dev_3}.py'
        ]
        
        for script in scripts:
            if script not in self.processes or \
               self.processes[script]['status'] != 'Running':
                if self.launch_script(script):
                    print(f"\nStarted {script}")
                    time.sleep(2)  # Increased delay to prevent terminal conflicts
    
    def stop_all(self):
        for script in list(self.processes.keys()):
            if self.processes[script]['status'] == 'Running':
                if self.stop_script(script):
                    print(f"\nStopped {script}")
                    time.sleep(1)

def main():
    manager = ProcessManager()
    
    # Start display update thread
    display_thread = threading.Thread(target=manager.update_display)
    display_thread.daemon = True
    display_thread.start()
    
    try:
        while True:
            if keyboard.is_pressed('s'):
                manager.start_all()
                time.sleep(0.5)  # Debounce
            elif keyboard.is_pressed('e'):
                manager.stop_all()
                time.sleep(0.5)  # Debounce
            elif keyboard.is_pressed('q'):
                break
            
            time.sleep(0.1)  # Reduce CPU usage
            
    except KeyboardInterrupt:
        pass
    finally:
        manager.running = False
        manager.stop_all()
        print("\nShutting down...")
        time.sleep(1)

if __name__ == "__main__":
    # Check if keyboard module is installed
    try:
        import keyboard
    except ImportError:
        print("Please install the required package:")
        print("pip install keyboard")
        sys.exit(1)
        
    main()