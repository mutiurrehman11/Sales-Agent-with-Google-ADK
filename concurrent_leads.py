import threading
import time
import random
from datetime import datetime, timedelta
from agent import SalesAgent
from config import Config


class LeadSimulator:
    def __init__(self, agent):
        self.agent = agent
        self.results = {}
        self.lock = threading.Lock()

    def simulate_lead(self, lead_id, name, behavior="normal"):
        """Simulate a lead's interaction pattern"""
        start_time = datetime.now()

        # Define behavior patterns
        if behavior == "fast":
            responses = ["yes", "30", "USA", "SaaS"]
            delays = [0, 0, 0, 0]
        elif behavior == "slow":
            responses = ["yes", "45", "Canada", "AI tools"]
            delays = [0, 25, 0, 0]  # Will trigger follow-up
        elif behavior == "decliner":
            responses = ["no thanks"]
            delays = [0]
        elif behavior == "abandoner":
            responses = ["yes", "28"]
            delays = [0, 0]
        else:  # normal
            responses = ["yes", "35", "UK", "Consulting"]
            delays = [1, 2, 1, 0]

        # Start conversation
        reply = self.agent.handle_trigger(lead_id, name)
        self._log(lead_id, "Agent", reply)

        # Process responses
        for i, (response, delay) in enumerate(zip(responses, delays)):
            time.sleep(delay)

            self._log(lead_id, name, response)
            reply = self.agent.handle_response(lead_id, response)

            if not reply:
                break

            self._log(lead_id, "Agent", reply)

        # Record results
        duration = (datetime.now() - start_time).total_seconds()
        completed = reply == Config.COMPLETION_MESSAGE if reply else False

        with self.lock:
            self.results[lead_id] = {
                "name": name,
                "behavior": behavior,
                "duration": duration,
                "completed": completed,
                "timestamp": start_time
            }

    def _log(self, lead_id, sender, message):
        """Thread-safe logging"""
        with self.lock:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Lead {lead_id}: {sender}: {message}")

    def run_concurrent_simulation(self, num_leads=10):
        """Run simulation with multiple concurrent leads"""
        threads = []
        behaviors = ["fast", "slow", "decliner", "abandoner", "normal"]

        for lead_id in range(1, num_leads + 1):
            name = f"Lead-{lead_id}"
            behavior = random.choice(behaviors)

            t = threading.Thread(
                target=self.simulate_lead,
                args=(lead_id, name, behavior),
                name=f"LeadThread-{lead_id}"
            )
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        return self.results


def run_simulation():
    print("=== Starting Concurrent Lead Simulation ===")
    print(f"Config: {Config.MAX_THREADS} max threads, follow-up after {Config.FOLLOW_UP_DELAY}")

    agent = SalesAgent()
    simulator = LeadSimulator(agent)

    # Speed up follow-up checks for demo
    original_follow_up = Config.FOLLOW_UP_DELAY
    Config.FOLLOW_UP_DELAY = timedelta(seconds=1)  # 10 seconds for demo

    try:
        # Run simulation in background
        sim_thread = threading.Thread(
            target=simulator.run_concurrent_simulation,
            args=(35,),  # 8 leads
            name="SimulationThread"
        )
        sim_thread.start()

        # Let simulation run
        try:
            while sim_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping simulation...")

        sim_thread.join()

        # Print results
        print("\n=== Simulation Results ===")
        for lead_id, result in simulator.results.items():
            print(f"Lead {lead_id} ({result['name']}): "
                  f"{result['behavior']} behavior, "
                  f"{'Completed' if result['completed'] else 'Incomplete'}, "
                  f"Duration: {result['duration']:.2f}s")

    finally:
        Config.FOLLOW_UP_DELAY = original_follow_up
        agent.shutdown()


if __name__ == "__main__":
    run_simulation()