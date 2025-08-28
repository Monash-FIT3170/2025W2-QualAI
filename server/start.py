# ./server/start.py

import os
import subprocess
import sys

def run_ingestion():
    """Runs the data ingestion and setup scripts."""
    print("--- 🚀 Checking vector database collection... ---")
    
    # Run the setup script
    setup_process = subprocess.run([sys.executable, "/app/scripts/setup_db.py"])
    
    # setup_db.py exits with 0 if ingestion should run, 1 if it should be skipped.
    if setup_process.returncode == 0:
        print("--- 🚀 Running initial data ingestion... ---")
        ingest_process = subprocess.run([sys.executable, "/app/scripts/ingest.py"])
        if ingest_process.returncode != 0:
            print("--- ❌ Ingestion failed. ---")
            sys.exit(1) # Exit if ingestion fails
    else:
        print("--- 👍 Collection is already populated. Skipping ingestion. ---")

def start_server():
    """Starts the Uvicorn server."""
    print("--- 🚀 Starting FastAPI server... ---")
    # Use os.execvp to replace the current process with Uvicorn
    # This is important for correct signal handling in Docker
    os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

if __name__ == "__main__":
    run_ingestion()
    start_server()