# employee_pulse_agent/agent.py

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

# Import your custom agent classes and orchestrator
from .agents import (
    PulseQuestionnaireAgent,
    ApprovalAgent,
    CommunicationAgent,
    OrchestratingAgent
)

# --- Load Environment Variables ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Loaded .env file from: {dotenv_path} in agent.py")
else:
    print(f".env file not found at {dotenv_path} in agent.py. Relying on ADK's .env loading or environment variables.")

# --- Initialize Backend Services (Your Custom Agents) ---
print("Initializing backend services for Employee Pulse Agent...")
questionnaire_service = PulseQuestionnaireAgent()
approval_service = ApprovalAgent()
communication_service = CommunicationAgent()

# The OrchestratingAgent now acts as a central service layer
pulse_orchestrator_service = OrchestratingAgent(
    questionnaire_agent=questionnaire_service,
    approval_agent=approval_service,
    communication_agent=communication_service,
    name="PulseSurveyServiceOrchestrator"
)
print(f"'{pulse_orchestrator_service.name}' initialized.")

# --- Tool Definitions for LlmAgent ---
# These functions will wrap calls to your pulse_orchestrator_service methods.

def initiate_survey_tool(survey_id: str, title: str, topic: str, num_questions: int, target_audience_emails: list[str], approver_contact: str) -> dict:
    """
    Initiates a new employee pulse survey.
    Requires survey_id, title, topic, num_questions, a list of target_audience_emails, and an approver_contact email.
    """
    print(f"[Tool: initiate_survey_tool] Called with id: {survey_id}, title: {title}")
    params = {
        "survey_id": survey_id,
        "title": title,
        "topic": topic,
        "num_questions": num_questions,
        "target_audience_emails": target_audience_emails,
        "approver_contact": approver_contact
    }
    return pulse_orchestrator_service.initiate_pulse_survey(params)

def handle_survey_approval_tool(approval_request_id: str, approval_decision: str) -> dict:
    """
    Handles the approval decision for a pending survey.
    Requires approval_request_id and approval_decision ('approved' or 'rejected').
    """
    print(f"[Tool: handle_survey_approval_tool] Called with request_id: {approval_request_id}, decision: {approval_decision}")
    return pulse_orchestrator_service.handle_approval_response(approval_request_id, approval_decision)

def get_survey_status_tool(survey_id: str) -> dict:
    """Gets the current status and details of a specific survey by its ID."""
    print(f"[Tool: get_survey_status_tool] Called for survey_id: {survey_id}")
    return pulse_orchestrator_service.get_survey_status(survey_id)

def list_all_surveys_tool() -> dict:
    """Lists all currently active surveys and their statuses."""
    print(f"[Tool: list_all_surveys_tool] Called.")
    return pulse_orchestrator_service.list_active_surveys()


# --- MCP Descriptions for Tools (Primarily for documentation or external use if needed) ---
# These are NOT passed to LlmAgent constructor directly.
# The ADK framework generates schemas from the function signatures and docstrings.
# Keeping them here can be useful for your own reference or if you need to expose these schemas elsewhere.

initiate_survey_tool_mcp = {
    "name": "initiate_survey_tool",
    "description": "Initiates a new employee pulse survey. Requires survey_id, title, topic, num_questions, target_audience_emails (list), and approver_contact email.",
    "parameters": {
        "type": "object",
        "properties": {
            "survey_id": {"type": "string", "description": "A unique identifier for the survey."},
            "title": {"type": "string", "description": "The title of the survey."},
            "topic": {"type": "string", "description": "The main topic of the survey (e.g., 'wellness', 'engagement')."},
            "num_questions": {"type": "integer", "description": "The number of questions to include from the topic."},
            "target_audience_emails": {
                "type": "array",
                "items": {"type": "string"},
                "description": "A list of email addresses for the target audience."
            },
            "approver_contact": {"type": "string", "description": "Email address of the person who needs to approve the survey."}
        },
        "required": ["survey_id", "title", "topic", "num_questions", "target_audience_emails", "approver_contact"]
    },
    "returns": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Status of the initiation ('pending_approval', 'error')."},
            "survey_id": {"type": "string", "description": "The ID of the survey."},
            "approval_request_id": {"type": "string", "description": "ID for the approval request, if successful."},
            "message": {"type": "string", "description": "Error message, if any."}
        },
        "required": ["status", "survey_id"]
    }
}

handle_survey_approval_tool_mcp = {
    "name": "handle_survey_approval_tool",
    "description": "Handles the approval decision for a pending survey. Requires approval_request_id and approval_decision ('approved' or 'rejected').",
    "parameters": {
        "type": "object",
        "properties": {
            "approval_request_id": {"type": "string", "description": "The ID of the approval request."},
            "approval_decision": {"type": "string", "enum": ["approved", "rejected"], "description": "The decision for the approval."}
        },
        "required": ["approval_request_id", "approval_decision"]
    },
    "returns": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Final status after handling approval ('sent', 'rejected', 'send_failed', 'error')."},
            "survey_id": {"type": "string", "description": "The ID of the survey affected."},
            "message": {"type": "string", "description": "Error message, if any."}
        },
        "required": ["status"]
    }
}

get_survey_status_tool_mcp = {
    "name": "get_survey_status_tool",
    "description": "Gets the current status and details of a specific survey by its ID.",
    "parameters": {
        "type": "object",
        "properties": {"survey_id": {"type": "string", "description": "The unique identifier of the survey to query."}},
        "required": ["survey_id"]
    },
    "returns": {
        "type": "object",
        "description": "Contains survey details if found, or an error message."
    }
}

list_all_surveys_tool_mcp = {
    "name": "list_all_surveys_tool",
    "description": "Lists all currently active surveys and their statuses.",
    "parameters": {"type": "object", "properties": {}},
    "returns": {
        "type": "object",
        "description": "A dictionary where keys are survey_ids and values are survey detail objects. Returns empty object if no surveys."
    }
}

# --- Define the Root LlmAgent ---
root_agent = LlmAgent(
    name="employee_pulse_survey_llm_agent",
    model=os.getenv("ADK_MODEL", "gemini-1.5-flash"),
    description="An agent that manages employee pulse surveys, including initiation, approvals, and status tracking.",
    instruction=(
        "You are an AI assistant managing employee pulse surveys. "
        "Use the available tools to initiate surveys, handle approvals, and check survey statuses. "
        "When initiating a survey, ensure you have all required parameters: survey_id, title, topic, num_questions, target_audience_emails (as a list), and approver_contact. "
        "For approvals, you need an approval_request_id and a decision ('approved' or 'rejected')."
        "The target_audience_emails parameter should be a list of strings."
    ),
    tools=[ # Provide the actual function objects
        initiate_survey_tool,
        handle_survey_approval_tool,
        get_survey_status_tool,
        list_all_surveys_tool
    ]
    # DO NOT pass tool_descriptions as a constructor argument.
    # The ADK infers schemas from the Python functions (docstrings, type hints).
)

# If you need to access the generated schemas by ADK (for inspection or other purposes),
# LlmAgent might expose them through an attribute after initialization, e.g., root_agent.tools_mcp_generated
# or similar. Check ADK documentation for how to access auto-generated schemas if needed.
# For now, the MCP description dicts (e.g., initiate_survey_tool_mcp) are just for your reference.

#print(f"Root LlmAgent '{root_agent.name}' initialized with tools in agent.py.")
