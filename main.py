# main.py
from process_manager import ProcessManager
from connection_tracker import ConnectionTracker
from rule_engine import RuleEngine
from action_simulator import ActionSimulator
from logger import FirewallLogger

def main():
    print("\n=== USER-LEVEL FIREWALL DEMONSTRATION===")

    # --- Step 1: Initialize managers ---
    pm = ProcessManager()
    ct = ConnectionTracker()
    re = RuleEngine()
    act = ActionSimulator()
    logger = FirewallLogger()

    # --- Step 2: Setup demo processes ---
    demo_processes = [
        ("Chrome", 3),
        ("Spotify", 2),
        ("VSCode", 1),
        ("Slack", 4)
    ]
    for name, priority in demo_processes:
        pm.add_process(name, priority)

    # --- Step 3: Generate simulated connections ---
    ct.generate_connections(pm.process_list)
    print("\n--- Simulated Connections ---")
    ct.list_connections()

    # --- Step 4: Load rules ---
    re.load_rules()
    print("\n--- Loaded Rules ---")
    re.list_rules()

    # --- Step 5: Apply rules to processes ---
    print("\n--- Applying Rules ---")
    for proc in pm.process_list:
        matched_rules = re.match_process({"pid": proc.pid, "name": proc.name})
        for rule in matched_rules:
            result = act.apply_action(proc, rule)
            logger.log_decision(proc.pid, port=None, rule=rule, result=result["result"])

    # --- Step 6: Apply rules to connections ---
    for conn in ct.connections:
        matched_rules = re.match_connection(conn)
        for rule in matched_rules:
            result = act.apply_action(conn, rule)
            logger.log_decision(getattr(conn, "pid", None),
                                port=getattr(conn, "local_port", None),
                                rule=rule,
                                result=result["result"])

    # --- Step 7: Show final process states ---
    print("\n--- Final Process Table ---")
    pm.show_processes()

    # --- Step 8: Show action log ---
    act.show_action_log()

    # --- Step 9: Show recent logger records ---
    logger.show_recent_logs()

    print("\n=== DEMONSTARTION COMPLETE ===\n")


if __name__ == "__main__":
    main()
