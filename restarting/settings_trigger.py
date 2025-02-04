import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import loggs


class Watcher(FileSystemEventHandler):
    def __init__(self, watch_dir, file_to_watch):
        self.watch_dir = watch_dir
        self.file_to_watch = file_to_watch

    def on_created(self, event):
        if event.src_path.endswith(self.file_to_watch):
            self.restart_main()

    def restart_main(self):
        # Terminate the existing main.py process (if running)
        loggs.system_log.info('[] Restarting bot...')
        for proc in os.popen('ps aux'):
            if 'python3 main.py' in proc:
                pid = proc.split()[1]
                os.kill(int(pid), 9)
        # Restart main.py

        subprocess.Popen(['python3', 'main.py'])
        loggs.system_log.info('[√] Bot restarted successfully')

def main():
    watch_dir = '..'  # Directory to watch
    file_to_watch = './tools/is_changed'  # File that triggers the restart
    loggs.system_log.info('Indicators has been changed!')
    event_handler = Watcher(watch_dir, file_to_watch)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    os.remove(file_to_watch)
    loggs.system_log.info('is_changed file removed successfully')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()