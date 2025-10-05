import json
import os

RULES_FILE = "rules.json"


class RuleEngine:
    def __init__(self, rules_file=RULES_FILE):
        self.rules_file = rules_file
        self.rules = self.load_rules()

    def load_rules(self):
        """Load all rules from the JSON file."""
        if not os.path.exists(self.rules_file):
            return []
        try:
            with open(self.rules_file, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
        except json.JSONDecodeError:
            return []

    def save_rules(self):
        """Save the current rules list to JSON file."""
        with open(self.rules_file, "w") as f:
            json.dump(self.rules, f, indent=4)

    def add_rule(self, rule):
        """Add a new rule and save."""
        if not all(k in rule for k in ("id", "type", "value", "action")):
            print("❌ Invalid rule format.")
            return
        self.rules.append(rule)
        self.save_rules()
        print(f"✅ Rule {rule['id']} added successfully.")

    def delete_rule(self, rule_id):
        """Delete a rule by ID."""
        before = len(self.rules)
        self.rules = [r for r in self.rules if r["id"] != rule_id]
        after = len(self.rules)
        if before == after:
            print(f"⚠️ Rule ID {rule_id} not found.")
        else:
            self.save_rules()
            print(f"🗑️ Rule ID {rule_id} deleted successfully.")

    def match_process(self, proc_info):
        """Return rules matching a process dict (simulated)."""
        matched = []
        for rule in self.rules:
            if rule["type"] == "process_name" and rule["value"].lower() in proc_info["name"].lower():
                matched.append(rule)
        return matched

    def match_connection(self, conn_info):
        """Return rules matching a connection object (simulated)."""
        matched = []
        for rule in self.rules:
            if rule["type"] == "port" and rule["value"] == getattr(conn_info, "local_port", None):
                matched.append(rule)
            elif rule["type"] == "ip" and rule["value"] == getattr(conn_info, "remote_ip", None):
                matched.append(rule)
        return matched


    def list_rules(self):
        """Print all current rules."""
        if not self.rules:
            print("No rules currently defined.")
            return
        print("Current Rules:")
        for r in self.rules:
            print(f"  • ID: {r['id']} | Type: {r['type']} | Value: {r['value']} | Action: {r['action']}")


if __name__ == "__main__":
    # Demo simulation
    engine = RuleEngine()

    print("\n--- RULES ---")
    engine.list_rules()

    # Simulated process and connection to test matching
    process = {"pid": 123, "name": "chrome.exe"}
    connection = {"local_port": 8080, "remote_ip": "192.168.1.10"}

    print("\n--- MATCH RESULTS ---")
    print("Process matches:", engine.match_process(process))
    print("Connection matches:", engine.match_connection(connection))
