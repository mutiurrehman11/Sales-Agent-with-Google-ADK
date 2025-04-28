import threading
from config import Config
from session_manager import SessionManager
from data_storage import DataStorage
from follow_up import FollowUpScheduler


class SalesAgent:
    def __init__(self):
        self.session_manager = SessionManager()
        self.data_storage = DataStorage()
        self.follow_up_scheduler = FollowUpScheduler(self.session_manager, self.data_storage)
        self.follow_up_scheduler.start()
        self.lock = threading.Lock()

    def handle_trigger(self, lead_id, lead_name):
        """Handle a new lead trigger (form submission)"""
        with self.lock:
            # Check if lead already exists
            existing_lead = self.data_storage.get_lead(lead_id)
            if existing_lead and existing_lead["status"] in ("secured", "declined"):
                return None

            # Create new session
            session = self.session_manager.create_session(lead_id, lead_name)

            # Initial data storage
            self.data_storage.update_lead({
                "lead_id": lead_id,
                "name": lead_name,
                "status": "pending_consent"
            })

            return Config.INITIAL_MESSAGE.format(name=lead_name)

    def handle_response(self, lead_id, response_text):
        """Handle a lead's response to a message"""
        with self.lock:
            session = self.session_manager.get_session(lead_id)
            if not session:
                return None

            response_text = response_text.lower().strip()

            if session["status"] == "pending_consent":
                return self._handle_consent(lead_id, response_text, session)
            elif session["status"] == "active":
                return self._handle_question(lead_id, response_text, session)
            elif session["status"] == "follow_up":
                return self._handle_follow_up(lead_id, response_text, session)

            return None

    def _handle_consent(self, lead_id, response_text, session):
        """Handle the initial consent response"""
        if any(word in response_text for word in ["yes", "ok", "sure", "agree"]):
            # Consent given - start questions
            updates = {
                "status": "active",
                "current_question": 0,
                "follow_up_sent": False
            }
            self.session_manager.update_session(lead_id, updates)

            self.data_storage.update_lead({
                "lead_id": lead_id,
                "name": session["name"],
                "status": "active"
            })

            return Config.QUESTIONS[0][1]  # First question
        else:
            # Consent declined
            self.session_manager.update_session(lead_id, {"status": "declined"})
            self.data_storage.update_lead({
                "lead_id": lead_id,
                "name": session["name"],
                "status": "declined"
            })
            return Config.CONSENT_DECLINED_MESSAGE

    def _handle_question(self, lead_id, response_text, session):
        """Handle response to a question"""
        current_q = session["current_question"]
        if current_q >= len(Config.QUESTIONS):
            return None

        # Store answer
        field_name, _ = Config.QUESTIONS[current_q]
        answers = {**session["answers"], field_name: response_text}

        # Prepare updates
        updates = {
            "answers": answers,
            "follow_up_sent": False
        }

        # Move to next question or complete
        if current_q + 1 < len(Config.QUESTIONS):
            updates["current_question"] = current_q + 1
            next_question = Config.QUESTIONS[current_q + 1][1]
        else:
            updates["status"] = "secured"
            next_question = Config.COMPLETION_MESSAGE

        self.session_manager.update_session(lead_id, updates)

        # Update storage
        storage_data = {
            "lead_id": lead_id,
            "name": session["name"],
            "status": "active" if current_q + 1 < len(Config.QUESTIONS) else "secured",
            **answers
        }
        self.data_storage.update_lead(storage_data)

        return next_question

    def _handle_follow_up(self, lead_id, response_text, session):
        """Handle response after follow-up"""
        if any(word in response_text for word in ["yes", "ok", "ready"]):
            # Continue conversation
            updates = {
                "status": "active",
                "follow_up_sent": False
            }
            self.session_manager.update_session(lead_id, updates)

            current_q = session["current_question"] or 0
            if current_q < len(Config.QUESTIONS):
                return Config.QUESTIONS[current_q][1]

        return None

    def shutdown(self):
        """Clean up resources"""
        self.follow_up_scheduler.stop()