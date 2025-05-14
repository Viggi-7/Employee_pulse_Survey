# employee_pulse_survey_project/agents/communication_agent.py

from .base_agent import BaseAgent

class CommunicationAgent(BaseAgent):
    """
    Handles sending emails and other communications.
    """
    def __init__(self, name="CommunicationAgent"):
        super().__init__(name)

    def send_email(self, recipient_email, subject, body):
        """
        Simulates sending an email.
        Replace with actual email sending logic (e.g., smtplib, Gmail API).
        """
        print(f"[{self.name}] SIMULATING EMAIL SEND:")
        print(f"  To: {recipient_email}")
        print(f"  Subject: {subject}")
        print(f"  Body:\n{body}\n")
        print(f"[{self.name}] Email to {recipient_email} sent successfully (simulated).")
        return True

    def send_survey_invitations(self, employee_emails, survey_details):
        """
        Sends survey invitation emails to a list of employees.
        """
        print(f"[{self.name}] Preparing to send survey invitations for '{survey_details.get('title', 'Survey')}'")
        survey_link = f"http://survey.example.com/s/{survey_details.get('survey_id', 'default_survey')}"
        subject = f"Invitation: Please participate in the {survey_details.get('title', 'Employee Survey')}"
        
        success_count = 0
        for email in employee_emails:
            body = (f"Dear Employee,\n\nPlease take a few moments to complete our pulse survey: {survey_details.get('title', '')}.\n"
                    f"Your feedback is valuable.\n\n"
                    f"Access the survey here: {survey_link}\n\n"
                    f"Thank you,\nHR Department")
            if self.send_email(email, subject, body):
                success_count +=1
        
        print(f"[{self.name}] {success_count}/{len(employee_emails)} survey invitations sent for '{survey_details.get('title', 'Survey')}'.")
        return success_count == len(employee_emails)

    def handle_incoming_email(self, email_data):
        """
        Simulates handling an incoming email (e.g., an out-of-office reply).
        """
        print(f"[{self.name}] Received incoming email: From='{email_data.get('from')}', Subject='{email_data.get('subject')}'")
        # Basic logic: if "out of office" in subject, log it.
        if "out of office" in email_data.get('subject', '').lower():
            print(f"[{self.name}] Detected Out Of Office reply from {email_data.get('from')}.")
            # Potentially update employee status or notify admin
        return {"status": "processed"}
