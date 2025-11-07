# main.py
import psutil
from process_manager import ProcessManager
from connection_tracker import ConnectionTracker
from rule_engine import RuleEngine
from action_simulator import ActionSimulator
from logger import FirewallLogger

def main():
    print("\n=== USER-LEVEL FIREWALL (REAL-TIME SAFE DEMONSTRATION) ===")

    # --- Step 1: Initialize components ---
    pm = ProcessManager()        # Uses psutil for real system processes
    ct = ConnectionTracker()     # Uses psutil.net_connections()
    re = RuleEngine()            # Loads JSON-based rules
    logger = FirewallLogger()    # Structured JSONL logger
    act = ActionSimulator(logger)  # Injects logger into ActionSimulator

    # --- Step 2: Fetch real processes ---
    print("\n--- ACTIVE SYSTEM PROCESSES (TOP 25) ---")
    pm.show_processes()  # already implemented with psutil in new ProcessManager

    # --- Step 3: Fetch and show real network connections ---
    print("\n--- ACTIVE NETWORK CONNECTIONS ---")
    ct.fetch_connections()
    ct.list_connections()

    # --- Step 4: Load and list rules ---
    print("\n--- LOADED RULES ---")
    re.list_rules()

    # --- Step 5: Apply rules to real processes ---
    print("\n--- APPLYING RULES TO PROCESSES ---")
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        matched_rules = re.match_process(proc)
        for rule in matched_rules:
            act.apply_action(proc, rule)  # ActionSimulator handles logging now

    # --- Step 6: Apply rules to real connections ---
    print("\n--- APPLYING RULES TO NETWORK CONNECTIONS ---")
    ct.fetch_connections()
    for conn in ct.connections:
        matched_rules = re.match_connection(conn)
        for rule in matched_rules:
            act.apply_action(conn, rule)

    # --- Step 7: Show summary logs ---
    print("\n--- ACTION SUMMARY ---")
    act.show_action_log()

    print("\n--- RECENT FIREWALL LOG ENTRIES ---")
    logger.show_recent_logs()

    print("\n=== DEMONSTRATION COMPLETE (SAFE MODE: DRY_RUN ENABLED) ===\n")


if __name__ == "__main__":
    main()
