# employee_pulse_survey_project/agents/questionnaire_agent.py

from .base_agent import BaseAgent

class PulseQuestionnaireAgent(BaseAgent):
    """
    Manages survey questions.
    """
    def __init__(self, name="QuestionnaireAgent"):
        super().__init__(name)
        self.question_bank = {
            "engagement": [
                {"id": "eng1", "text": "How motivated are you at work?"},
                {"id": "eng2", "text": "Do you feel your contributions are valued?"},
            ],
            "wellness": [
                {"id": "wel1", "text": "How would you rate your current work-life balance?"},
                {"id": "wel2", "text": "Do you have access to resources that support your well-being?"},
            ],
            "default": [
                {"id": "def1", "text": "Any other feedback you would like to share?"}
            ]
        }

    def get_survey_questions(self, topic="default", num_questions=2):
        """
        Retrieves a list of questions for a given topic.
        """
        print(f"[{self.name}] Received request for questions on topic: {topic}")
        questions = self.question_bank.get(topic, [])
        if not questions:
            questions = self.question_bank["default"]
        
        selected_questions = questions[:num_questions]
        print(f"[{self.name}] Providing {len(selected_questions)} questions: {selected_questions}")
        return selected_questions

