##created by scavengerrr to help users track changes live
#python3 and watchdog utilized. can be used on mac or pc, includes cli.

import os
import shutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse

# Directory where file history will be stored
HISTORY_DIR = ".history"

# Step 1: File Change Handler
class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            save_version(event.src_path)

# Step 2: Saving a version of the file
def save_version(file_path):
    # Create a history directory if it doesn't exist
    history_dir = os.path.join(os.path.dirname(file_path), HISTORY_DIR)
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    # Generate a timestamped copy of the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_file = os.path.join(history_dir, f"{os.path.basename(file_path)}_{timestamp}")
    
    shutil.copy2(file_path, version_file)  # Copies the file with metadata
    print(f"Version saved: {version_file}")

# Step 3: Listing available versions
def list_versions(file_path):
    history_dir = os.path.join(os.path.dirname(file_path), HISTORY_DIR)
    if os.path.exists(history_dir):
        versions = [f for f in os.listdir(history_dir) if f.startswith(os.path.basename(file_path))]
        return versions
    return []

# Step 4: Reverting to a specific version
def revert_to_version(file_path, version):
    history_dir = os.path.join(os.path.dirname(file_path), HISTORY_DIR)
    version_path = os.path.join(history_dir, version)
    
    if os.path.exists(version_path):
        shutil.copy2(version_path, file_path)
        print(f"Reverted {file_path} to {version}")
    else:
        print(f"Version {version} not found.")

# Step 5: CLI Interface
def cli():
    parser = argparse.ArgumentParser(description="File History and Reversion System")
    parser.add_argument("command", choices=["list", "revert", "watch"], help="Command to run")
    parser.add_argument("file", help="The file to operate on")
    parser.add_argument("--version", help="The version to revert to (used with revert command)")

    args = parser.parse_args()

    if args.command == "list":
        versions = list_versions(args.file)
        if versions:
            print(f"Available versions for {args.file}:")
            for i, version in enumerate(versions):
                print(f"Version {i+1}: {version}")
        else:
            print("No versions found.")
    
    elif args.command == "revert":
        if args.version:
            revert_to_version(args.file, args.version)
        else:
            print("Please provide a version to revert to using --version.")
    
    elif args.command == "watch":
        print(f"Watching {args.file} for changes...")
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, os.path.dirname(args.file), recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

# Start the CLI
if __name__ == "__main__":
    cli()
