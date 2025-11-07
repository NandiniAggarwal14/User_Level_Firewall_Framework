import json
import os
import psutil

RULES_FILE = "rules.json"
DRY_RUN = True  # Ensures no real blocking or termination

class RuleEngine:
    """Rule Engine to manage and match firewall-like rules safely."""
    def __init__(self, rules_file=RULES_FILE):
        self.rules_file = rules_file
        self.rules = self.load_rules()

    # ----------------------------
    # Rule File Management
    # ----------------------------
    def load_rules(self):
        """Load all rules from a JSON file."""
        if not os.path.exists(self.rules_file):
            return []
        try:
            with open(self.rules_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_rules(self):
        """Save rules to the JSON file."""
        with open(self.rules_file, "w") as f:
            json.dump(self.rules, f, indent=4)

    def add_rule(self, rule):
        """Add a new rule and save."""
        required = {"id", "type", "value", "action"}
        if not required.issubset(rule.keys()):
            print("❌ Invalid rule format. Must include id, type, value, action.")
            return
        self.rules.append(rule)
        self.save_rules()
        print(f"✅ Rule {rule['id']} added successfully.")

    def delete_rule(self, rule_id):
        """Delete a rule by ID."""
        before = len(self.rules)
        self.rules = [r for r in self.rules if r["id"] != rule_id]
        if len(self.rules) < before:
            self.save_rules()
            print(f"🗑️ Rule ID {rule_id} deleted successfully.")
        else:
            print(f"⚠️ Rule ID {rule_id} not found.")

    def list_rules(self):
        """Print all current rules."""
        if not self.rules:
            print("No rules currently defined.")
            return
        print("\n📜 Current Rules:")
        for r in self.rules:
            print(f"  • ID: {r['id']} | Type: {r['type']} | Value: {r['value']} | Action: {r['action']}")
        print()

    # ----------------------------
    # Matching Logic
    # ----------------------------
    def match_process(self, proc_info):
        """
        Match live or simulated process against rules.
        proc_info can be:
          - dict (from simulation)
          - psutil.Process object
        """
        matched = []

        try:
            # Normalize input
            if isinstance(proc_info, psutil.Process):
                name = proc_info.name().lower()
                username = proc_info.username().lower() if proc_info.username() else ""
            elif isinstance(proc_info, dict):
                name = proc_info.get("name", "").lower()
                username = proc_info.get("username", "").lower()
            else:
                return matched

            for rule in self.rules:
                rule_type = rule["type"]
                value = str(rule["value"]).lower()

                if rule_type == "process_name" and value in name:
                    matched.append(rule)
                elif rule_type == "username" and value in username:
                    matched.append(rule)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        return matched

    def match_connection(self, conn_info):
        """
        Match real or simulated connection objects against rules.
        conn_info can be:
          - dict (simulation)
          - Connection object (from ConnectionTracker)
        """
        matched = []
        # Extract safely
        local_port = getattr(conn_info, "local_port", conn_info.get("local_port", None))
        remote_ip = getattr(conn_info, "remote_ip", conn_info.get("remote_ip", None))

        for rule in self.rules:
            rule_type = rule["type"]
            value = str(rule["value"]).lower()

            if rule_type == "port" and str(local_port) == value:
                matched.append(rule)
            elif rule_type == "ip" and value in str(remote_ip).lower():
                matched.append(rule)

        return matched

    # ----------------------------
    # Enforcement Simulation
    # ----------------------------
    def apply_rules_to_processes(self, processes):
        """Simulate rule checks against a list of live processes."""
        for proc in processes:
            matches = self.match_process(proc)
            if matches:
                for rule in matches:
                    self.simulate_action(rule, proc)

    def apply_rules_to_connections(self, connections):
        """Simulate rule checks against active connections."""
        for conn in connections:
            matches = self.match_connection(conn)
            if matches:
                for rule in matches:
                    self.simulate_action(rule, conn)

    def simulate_action(self, rule, target):
        """Simulate taking an action on a matched target (safe dry-run)."""
        if DRY_RUN:
            print(f"[DRY RUN] Rule {rule['id']} matched → would perform '{rule['action']}' on {target}")
        else:
            # Future real enforcement could go here
            pass


# --- Demo Execution ---
if __name__ == "__main__":
    engine = RuleEngine()

    print("\n--- Current Rules ---")
    engine.list_rules()

    # Test using live process snapshot
    print("\n--- Testing Live Process Matching ---")
    for proc in psutil.process_iter(['name', 'username']):
        matches = engine.match_process(proc)
        if matches:
            print(f"Process: {proc.name()} (PID {proc.pid}) matched: {matches}")

    # Example test connection dict
    sample_conn = {"local_port": 8080, "remote_ip": "192.168.1.10"}
    print("\n--- Testing Connection Matching ---")
    print("Matches:", engine.match_connection(sample_conn))
