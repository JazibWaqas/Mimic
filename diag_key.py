import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / "backend" / ".env"
print(f"Loading from: {env_path}")

# Clear existing env var to be sure
if "GEMINI_API_KEY" in os.environ:
    del os.environ["GEMINI_API_KEY"]

load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"Loaded Key: {api_key[:10]}...{api_key[-5:]}")
    
    # Check if this matches any commented lines
    with open(env_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if api_key in line:
                status = "ACTIVE" if not line.strip().startswith("#") else "COMMENTED (ERROR!)"
                print(f"Found in .env line {i}: {status}")
else:
    print("No GEMINI_API_KEY found!")
