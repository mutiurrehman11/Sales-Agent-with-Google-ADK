import threading
import time
from datetime import datetime
from config import Config


class FollowUpScheduler:
    def __init__(self, session_manager, data_storage):
        self.session_manager = session_manager
        self.data_storage = data_storage
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        """Start the follow-up scheduler thread"""
        self.thread.start()

    def stop(self):
        """Stop the follow-up scheduler"""
        self._stop_event.set()
        self.thread.join()

    def _run(self):
        """Main follow-up check loop"""
        while not self._stop_event.is_set():
            self._check_follow_ups()
            time.sleep(Config.CHECK_INTERVAL.total_seconds())

    def _check_follow_ups(self):
        """Check for leads needing follow-up and send messages"""
        lead_ids = self.session_manager.get_sessions_needing_followup()

        for lead_id in lead_ids:
            session = self.session_manager.get_session(lead_id)
            if session:
                # In a real implementation, this would send the message
                print(f"Sending follow-up to lead {lead_id} ({session['name']})")

                # Update session and storage
                self.session_manager.mark_follow_up_sent(lead_id)

                # Update data storage
                lead_data = {
                    "lead_id": lead_id,
                    "name": session["name"],
                    "status": "follow_up_sent",
                    **session["answers"]
                }
                self.data_storage.update_lead(lead_data)