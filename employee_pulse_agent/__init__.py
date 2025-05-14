# employee_pulse_agent/__init__.py

import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
# ADK's logs show it loads the .env from the app root (employee_pulse_agent/.env).
# This explicit load can be a fallback or ensure it's loaded if this __init__ is processed first.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Loaded .env file from: {dotenv_path} in __init__.py")
else:
    print(f".env file not found at {dotenv_path} in __init__.py. Relying on ADK's .env loading or environment variables.")

# Make the 'agent.py' module's contents, particularly 'root_agent', available
# when the 'employee_pulse_agent' package is imported.
# The ADK framework will look for `employee_pulse_agent.agent.root_agent`.
from . import agent  # This imports employee_pulse_agent/agent.py

print(f"employee_pulse_agent package initialized. 'agent' module (and its 'root_agent') should be available.")

# You can add a check here for debugging if needed:
# if hasattr(agent, 'root_agent'):
#     print(f"Successfully imported 'agent.root_agent': {agent.root_agent.name}")
# else:
#     print("ERROR: 'agent.root_agent' not found after import in __init__.py")

