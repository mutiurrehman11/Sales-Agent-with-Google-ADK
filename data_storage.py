import csv
import os
import threading
from datetime import datetime
from config import Config


class DataStorage:
    def __init__(self):
        self.data_file = Config.DATA_FILE
        self.lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        with self.lock:
            if not os.path.exists(self.data_file):
                with open(self.data_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=self._headers)
                    writer.writeheader()

    @property
    def _headers(self):
        return ["lead_id", "name", "age", "country", "interest", "status", "last_updated"]

    def update_lead(self, lead_data):
        """Update or create a lead record"""
        if "lead_id" not in lead_data or "name" not in lead_data:
            raise ValueError("Lead data must contain lead_id and name")

        with self.lock:
            # Read all existing data
            existing_data = self._read_all()

            # Update or add new record
            lead_id = str(lead_data["lead_id"])
            updated = False
            lead_data["last_updated"] = datetime.now().isoformat()

            for i, record in enumerate(existing_data):
                if record["lead_id"] == lead_id:
                    existing_data[i] = {**record, **lead_data}
                    updated = True
                    break

            if not updated:
                existing_data.append(lead_data)

            # Write back to file
            self._write_all(existing_data)

    def get_lead(self, lead_id):
        """Get a single lead's data"""
        with self.lock:
            leads = self._read_all()
            return next((lead for lead in leads if lead["lead_id"] == str(lead_id)), None)

    def _read_all(self):
        """Read all lead data from CSV"""
        if not os.path.exists(self.data_file):
            return []

        with open(self.data_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _write_all(self, data):
        """Write all lead data to CSV"""
        with open(self.data_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self._headers)
            writer.writeheader()
            writer.writerows(data)