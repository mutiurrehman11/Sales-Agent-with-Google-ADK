import threading
from datetime import datetime
from config import Config


class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()

    def create_session(self, lead_id, lead_name):
        """Create a new conversation session for a lead"""
        with self.lock:
            self.sessions[lead_id] = {
                "name": lead_name,
                "status": "pending_consent",
                "current_question": None,
                "answers": {},
                "last_interaction": datetime.now(),
                "follow_up_sent": False
            }
        return self.sessions[lead_id]

    def get_session(self, lead_id):
        """Get a session by lead ID"""
        with self.lock:
            return self.sessions.get(lead_id)

    def update_session(self, lead_id, updates):
        """Update session data"""
        with self.lock:
            if lead_id in self.sessions:
                self.sessions[lead_id].update(updates)
                self.sessions[lead_id]["last_interaction"] = datetime.now()
                return True
        return False

    def get_sessions_needing_followup(self):
        """Get list of lead IDs needing follow-up"""
        with self.lock:
            now = datetime.now()
            return [
                lead_id for lead_id, session in self.sessions.items()
                if session["status"] in ("active", "follow_up") and
                   not session["follow_up_sent"] and
                   (now - session["last_interaction"]) > Config.FOLLOW_UP_DELAY
            ]

    def mark_follow_up_sent(self, lead_id):
        """Mark that a follow-up was sent"""
        with self.lock:
            if lead_id in self.sessions:
                self.sessions[lead_id]["follow_up_sent"] = True
                self.sessions[lead_id]["status"] = "follow_up"
                return True
        return False