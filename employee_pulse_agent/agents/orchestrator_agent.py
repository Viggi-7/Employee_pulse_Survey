# employee_pulse_survey_project/agents/orchestrator_agent.py

from .base_agent import BaseAgent
# We will pass instances of other agents to the constructor, so direct import of classes here is not strictly necessary
# unless type hinting is desired more explicitly for the constructor.

class OrchestratingAgent(BaseAgent):
    """
    Coordinates the workflow between other agents.
    """
    def __init__(self, questionnaire_agent, approval_agent, communication_agent, name="OrchestratorAgent"):
        super().__init__(name)
        self.questionnaire_agent = questionnaire_agent
        self.approval_agent = approval_agent
        self.communication_agent = communication_agent
        self.active_surveys = {} # Stores survey_id: survey_details

    def initiate_pulse_survey(self, survey_params):
        """
        Starts the process for a new pulse survey.
        survey_params = {
            "survey_id": "unique_survey_id",
            "title": "Q3 Wellness Check",
            "topic": "wellness",
            "num_questions": 3,
            "target_audience_emails": ["employee1@example.com", "employee2@example.com"],
            "approver_contact": "hr_manager@example.com"
        }
        """
        print(f"\n[{self.name}] Initiating new pulse survey: '{survey_params.get('title')}'")

        # 1. Get Questions
        print(f"[{self.name}] Requesting questions from {self.questionnaire_agent.name}...")
        questions = self.questionnaire_agent.get_survey_questions(
            topic=survey_params.get("topic", "default"),
            num_questions=survey_params.get("num_questions", 2)
        )
        if not questions:
            print(f"[{self.name}] Failed to retrieve questions. Aborting survey initiation.")
            return {"status": "error", "message": "Failed to get questions", "survey_id": survey_params["survey_id"]}

        current_survey_details = {
            **survey_params,
            "questions": questions,
            "status": "pending_approval", # Initial status
            "approval_request_id": None,
            "approval_status": None
        }
        self.active_surveys[survey_params["survey_id"]] = current_survey_details
        
        # 2. Request Approval
        print(f"[{self.name}] Requesting approval from {self.approval_agent.name}...")
        approval_request_id, initial_status = self.approval_agent.request_approval(
            survey_details=current_survey_details,
            approver_contact=survey_params["approver_contact"]
        )
        current_survey_details["approval_request_id"] = approval_request_id
        current_survey_details["approval_status"] = initial_status # Should be 'pending'
        
        print(f"[{self.name}] Survey '{current_survey_details['title']}' is now pending approval (Request ID: {approval_request_id}).")
        return {"status": "pending_approval", "survey_id": survey_params["survey_id"], "approval_request_id": approval_request_id}

    def handle_approval_response(self, approval_request_id, approval_decision): # Renamed for clarity
        """
        Process the response from the approval agent (or simulated user approval).
        approval_decision should be 'approved' or 'rejected'.
        """
        print(f"\n[{self.name}] Handling approval response for Request ID: {approval_request_id}, Decision: {approval_decision}")
        
        # Record the approval status with the Approval Agent
        # This ensures the ApprovalAgent's internal state is also updated.
        if not self.approval_agent.record_approval_response(approval_request_id, approval_decision):
            print(f"[{self.name}] Could not record approval response in Approval Agent for {approval_request_id}. Aborting.")
            return {"status": "error", "message": f"Approval request ID {approval_request_id} not found in Approval Agent."}

        # Find the survey associated with this approval request in the orchestrator's active surveys
        survey_to_update = None
        survey_id_for_approval = None
        for sid, details in self.active_surveys.items():
            if details.get("approval_request_id") == approval_request_id:
                survey_to_update = details
                survey_id_for_approval = sid
                break
        
        if not survey_to_update:
            print(f"[{self.name}] No active survey found in Orchestrator for approval request ID '{approval_request_id}'. This might indicate an inconsistency.")
            # Even if not in active_surveys (should not happen if flow is correct), the approval_agent has recorded it.
            return {"status": "error", "message": f"Survey not found in Orchestrator for approval ID {approval_request_id}"}

        survey_to_update["approval_status"] = approval_decision # Update orchestrator's copy

        if approval_decision == "approved":
            survey_to_update["status"] = "approved_ready_to_send"
            print(f"[{self.name}] Survey '{survey_to_update['title']}' (ID: {survey_id_for_approval}) approved.")
            
            # 3. Send Survey Invitations
            print(f"[{self.name}] Instructing {self.communication_agent.name} to send survey invitations...")
            send_success = self.communication_agent.send_survey_invitations(
                employee_emails=survey_to_update["target_audience_emails"],
                survey_details=survey_to_update
            )
            if send_success:
                survey_to_update["status"] = "sent"
                print(f"[{self.name}] Survey '{survey_to_update['title']}' invitations have been sent.")
                return {"status": "sent", "survey_id": survey_id_for_approval}
            else:
                survey_to_update["status"] = "send_failed"
                print(f"[{self.name}] Failed to send all invitations for survey '{survey_to_update['title']}'.")
                return {"status": "send_failed", "survey_id": survey_id_for_approval}
        else: # 'rejected' or any other non-approved status
            survey_to_update["status"] = "rejected"
            print(f"[{self.name}] Survey '{survey_to_update['title']}' (ID: {survey_id_for_approval}) was '{approval_decision}'. No emails will be sent.")
            return {"status": "rejected", "survey_id": survey_id_for_approval}

    def get_survey_status(self, survey_id):
        """Gets the status of a specific survey."""
        survey = self.active_surveys.get(survey_id)
        if survey:
            return survey
        return {"status": "error", "message": "Survey ID not found"}

    def list_active_surveys(self):
        """Lists all active surveys and their current status."""
        if not self.active_surveys:
            print(f"[{self.name}] No active surveys.")
            return {}
        print(f"[{self.name}] Current Active Surveys:")
        for sid, details in self.active_surveys.items():
            print(f"  ID: {sid}, Title: {details['title']}, Status: {details['status']}, Approval: {details.get('approval_status', 'N/A')}")
        return self.active_surveys
