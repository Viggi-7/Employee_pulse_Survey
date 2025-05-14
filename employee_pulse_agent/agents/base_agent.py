# employee_pulse_survey_project/agents/base_agent.py

class BaseAgent:
    """
    A base class for all agents, providing a common structure.
    """
    def __init__(self, name):
        self.name = name
        print(f"[{self.name}] Initialized.")

    def process_message(self, sender_name, message_type, payload):
        """
        A generic way for agents to receive messages.
        Specific agents will override or extend this.
        Note: sender is now sender_name (string) for simplicity in this structure.
        """
        print(f"[{self.name}] Received message from [{sender_name}]: Type='{message_type}', Payload='{payload}'")
        # Default behavior is to acknowledge, specific agents will handle differently
        return {"status": "acknowledged", "original_payload": payload}

