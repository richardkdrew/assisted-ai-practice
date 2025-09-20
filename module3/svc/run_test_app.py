#!/usr/bin/env python3
"""Run the test version of the Configuration Service API."""

import subprocess
import sys
import time
import signal
from pathlib import Path

def run_test_server():
    """Run the test server using the SQLite version."""
    svc_dir = Path(__file__).parent / "svc"

    print("🚀 Starting Configuration Service (Test Mode)")
    print("=" * 50)
    print("Database: SQLite (in-memory)")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("=" * 50)

    # Start the server
    cmd = [
        "uv", "run", "python", "-m", "uvicorn",
        "main_test:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=svc_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        print("⏳ Starting server...")

        # Stream output
        for line in process.stdout:
            print(line.rstrip())
            if "Application startup complete" in line:
                print("\n✅ Server started successfully!")
                print("💡 You can now run: python test_manual.py")
                print("🛑 Press Ctrl+C to stop the server")

    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        process.terminate()
        process.wait()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error running server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test_server()