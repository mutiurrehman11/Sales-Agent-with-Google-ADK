import csv
import os
from datetime import datetime
from faker import Faker

def validate_lead_data(data):
    required_fields = ["lead_id", "name", "status"]
    return all(field in data for field in required_fields)


def generate_sample_leads(file_path, num_leads=5):
    fake = Faker()

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=["lead_id", "name", "age",
                                            "country", "interest", "status", "last_updated"])
        writer.writeheader()

        for i in range(1, num_leads + 1):
            writer.writerow({
                "lead_id": str(i),
                "name": fake.name(),
                "age": str(fake.random_int(min=18, max=70)),
                "country": fake.country(),
                "interest": fake.bs(),
                "status": fake.random_element(elements=("new", "active", "secured", "declined")),
                "last_updated": datetime.now().isoformat()
            })