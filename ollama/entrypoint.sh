#!/bin/sh
set -e

# This is the file we'll use to check if setup is done.
DONE_FILE="/setup/.done"

# Check if the setup has already been completed.
if [ -f "$DONE_FILE" ]; then
    echo "✅ Setup has already been completed. Starting Ollama."
    # Just start the main Ollama server.
    exec ollama serve
else
    echo "🚀 First time setup. Starting server in background to pull model."
    # Start the server in the background.
    ollama serve &
    # Store the process ID.
    pid=$!

    # Wait for the server to be ready.
    echo "⏳ Waiting for Ollama server to be ready..."
    sleep 5 # A simple wait is often enough.

    # Pull the model.
    echo "📥 Pulling model deepseek-r1:7b..."
    ollama pull deepseek-r1:7b

    # Create the .done file to prevent this from running again.
    echo "✅ Model downloaded. Creating .done file."
    mkdir -p /setup && touch "$DONE_FILE"

    echo "🎉 Setup complete. Ollama is now running."
    # Wait for the background server process to finish.
    wait $pid
fi