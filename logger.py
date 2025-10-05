import json
import os
from datetime import datetime

LOG_FILE = "firewall_log.jsonl"  # JSON lines for easy appending

class FirewallLogger:
    """Structured logging of firewall actions and decisions."""

    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        # Ensure the log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                pass

    def log_decision(self, pid, port=None, rule=None, result=None):
        """Log an action or decision."""
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": pid,
            "port": port,
            "rule_id": rule.get("id") if rule else None,
            "rule_type": rule.get("type") if rule else None,
            "rule_value": rule.get("value") if rule else None,
            "action": rule.get("action") if rule else None,
            "result": result
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def query_logs(self, pid=None, rule_id=None, action=None):
        """Return a filtered list of log records."""
        records = []
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if pid and rec["pid"] != pid:
                        continue
                    if rule_id and rec["rule_id"] != rule_id:
                        continue
                    if action and rec["action"] != action:
                        continue
                    records.append(rec)
                except json.JSONDecodeError:
                    continue
        return records

    def show_recent_logs(self, limit=10):
        """Print the last 'limit' log entries."""
        records = self.query_logs()
        print("\n--- Recent Firewall Logs ---")
        for rec in records[-limit:]:
            print(f"{rec['timestamp']} | PID {rec['pid']} | Rule {rec['rule_id']} | "
                  f"Action: {rec['action']} | Result: {rec['result']}")
