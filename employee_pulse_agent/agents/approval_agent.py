# employee_pulse_survey_project/agents/approval_agent.py

from .base_agent import BaseAgent

class ApprovalAgent(BaseAgent):
    """
    Manages the approval process for surveys.
    """
    def __init__(self, name="ApprovalAgent"):
        super().__init__(name)
        self.approval_requests = {} # Stores approval_request_id: details

    def request_approval(self, survey_details, approver_contact):
        """
        Simulates requesting approval.
        """
        request_id = f"approval_{len(self.approval_requests) + 1:03d}" # Padded ID
        self.approval_requests[request_id] = {
            "survey_title": survey_details.get("title", "N/A"),
            "approver": approver_contact,
            "status": "pending", # In a real scenario, this would be updated externally
            "survey_details": survey_details # Store details for context
        }
        print(f"[{self.name}] Approval requested for survey '{survey_details.get('title', 'N/A')}' from '{approver_contact}'. Request ID: {request_id}")
        print(f"[{self.name}] To simulate approval, call orchestrator.handle_approval_response('{request_id}', 'approved') or 'rejected'")
        return request_id, "pending"

    def get_approval_status(self, request_id):
        """
        Checks the status of an approval request.
        """
        status = self.approval_requests.get(request_id, {}).get("status", "not_found")
        print(f"[{self.name}] Status for request ID '{request_id}': {status}")
        return status

    def record_approval_response(self, request_id, status):
        """
        Records the response from an approver.
        """
        if request_id in self.approval_requests:
            self.approval_requests[request_id]["status"] = status
            print(f"[{self.name}] Approval status for '{request_id}' ('{self.approval_requests[request_id]['survey_title']}') updated to '{status}'.")
            return True
        else:
            print(f"[{self.name}] Approval request ID '{request_id}' not found.")
            return False
