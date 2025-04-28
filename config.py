from datetime import timedelta


class Config:
    # Conversation Flow
    QUESTIONS = [
        ("age", "What is your age?"),
        ("country", "Which country are you from?"),
        ("interest", "What product or service are you interested in?")
    ]

    # Messages
    INITIAL_MESSAGE = "Hey {name}, thank you for filling out the form. I'd like to gather some information from you. Is that okay?"
    CONSENT_DECLINED_MESSAGE = "Alright, no problem. Have a great day!"
    FOLLOW_UP_MESSAGE = "Just checking in to see if you're still interested. Let me know when you're ready to continue."
    COMPLETION_MESSAGE = "Thank you for the information! We'll be in touch soon."

    # Timing
    FOLLOW_UP_DELAY = timedelta(hours=24)  # 24 hours
    CHECK_INTERVAL = timedelta(minutes=30)  # Check every 30 minutes

    # Data Storage
    DATA_FILE = "leads.csv"
    MAX_THREADS = 50  # Maximum concurrent conversations