import os
import subprocess
import time
from pathlib import Path

# The file we'll use to check if setup is done.
DONE_FILE = Path("/setup/.done")

# Check if the setup has already been completed.
if DONE_FILE.exists():
    print("✅ Setup already completed. Starting Ollama server.")
    # Replace this script with the ollama serve process.
    os.execvp("ollama", ["ollama", "serve"])
else:
    print("🚀 First-time setup. Starting server in the background.")
    # Start the Ollama server as a background process.
    server_process = subprocess.Popen(["ollama", "serve"])

    print("⏳ Waiting for server to initialize...")
    time.sleep(5)  # A simple wait to let the server start.

    print("📥 Pulling model deepseek-r1:7b...")
    # Run the pull command and wait for it to complete.
    # This will stream the download progress to the container's logs.
    subprocess.run(["ollama", "pull", "deepseek-r1:7b"], check=True)

    print("✅ Model downloaded. Creating .done file to prevent re-downloading.")
    # Create the .done file so this block won't run again.
    DONE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DONE_FILE.touch()

    print("🎉 Setup complete. Handing off to main Ollama server process.")
    # Wait for the background server process to finish, which keeps the container alive.
    server_process.wait()