"""Development script with hot reload capability."""

import sys
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import psutil

class AppReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_restart = 0
        self.restart_app()
    
    def restart_app(self):
        try:
            # Kill the previous instance if it exists
            if self.process is not None:
                try:
                    # Check if process still exists
                    if psutil.pid_exists(self.process.pid):
                        # Kill all child processes to ensure clean restart
                        parent = psutil.Process(self.process.pid)
                        for child in parent.children(recursive=True):
                            try:
                                child.kill()
                            except psutil.NoSuchProcess:
                                pass
                        parent.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process already terminated or access denied
                    pass
                self.process = None
            
            # Start new instance
            print("\nStarting application...")
            self.process = subprocess.Popen([sys.executable, "main.py"])
            self.last_restart = time.time()
        except Exception as e:
            print(f"\nError restarting application: {str(e)}")
    
    def on_modified(self, event):
        # Only handle Python file modifications
        if not event.src_path.endswith('.py'):
            return
            
        # Prevent multiple reloads for the same save
        if time.time() - self.last_restart < 1:  # Debounce for 1 second
            return
            
        print(f"\nChange detected in {os.path.basename(event.src_path)}")
        self.restart_app()

def main():
    # Set up the file system observer
    observer = Observer()
    event_handler = AppReloader()
    
    # Watch both the root directory and the ui directory
    observer.schedule(event_handler, ".", recursive=False)
    observer.schedule(event_handler, "./ui", recursive=False)
    observer.start()
    
    try:
        while True:
            # Check if process is still running
            if event_handler.process is not None:
                if event_handler.process.poll() is not None:
                    # Process has terminated
                    print("\nApplication terminated. Waiting for changes to restart...")
                    event_handler.process = None
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping development server...")
        if event_handler.process is not None:
            try:
                event_handler.process.kill()
            except:
                pass
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main() 