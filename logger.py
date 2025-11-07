import json
import os
from datetime import datetime
import psutil

LOG_FILE = "firewall_log.jsonl"
MAX_LOG_SIZE_MB = 5  # Auto-rotate if exceeds this size
DRY_RUN = True       # Reflects system-wide safe mode


class FirewallLogger:
    """Structured, safe logging of all firewall-like actions and rule decisions."""

    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        # Ensure the log file exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("")
        self._rotate_if_needed()

    # ----------------------------
    # Core Logging
    # ----------------------------
    def log_decision(self, target=None, rule=None, result=None):
        """
        Log an action/decision taken on a target (process or connection).
        Includes process name, connection info, and DRY_RUN mode awareness.
        """
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dry_run": DRY_RUN,
            "pid": getattr(target, "pid", None),
            "process_name": self._get_process_name(target),
            "local_ip": getattr(target, "local_ip", None),
            "local_port": getattr(target, "local_port", None),
            "remote_ip": getattr(target, "remote_ip", None),
            "remote_port": getattr(target, "remote_port", None),
            "rule_id": rule.get("id") if rule else None,
            "rule_type": rule.get("type") if rule else None,
            "rule_value": rule.get("value") if rule else None,
            "action": rule.get("action") if rule else None,
            "result": result or "simulated_action"
        }

        # Write JSONL entry
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write log: {e}")

    # ----------------------------
    # Query Utilities
    # ----------------------------
    def query_logs(self, pid=None, rule_id=None, action=None):
        """Return a filtered list of log records."""
        records = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        if pid and rec.get("pid") != pid:
                            continue
                        if rule_id and rec.get("rule_id") != rule_id:
                            continue
                        if action and rec.get("action") != action:
                            continue
                        records.append(rec)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            return []
        return records

    def show_recent_logs(self, limit=10):
        """Display the most recent 'limit' logs."""
        records = self.query_logs()
        print("\n--- Recent Firewall Logs ---")
        for rec in records[-limit:]:
            dry = "(DRY RUN)" if rec.get("dry_run") else ""
            pname = rec.get("process_name") or "Unknown"
            print(f"{rec['timestamp']} | {pname} (PID {rec['pid']}) | "
                  f"Rule {rec['rule_id']} | Action: {rec['action']} | Result: {rec['result']} {dry}")

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _get_process_name(self, target):
        """Safely extract process name."""
        try:
            if isinstance(target, psutil.Process):
                return target.name()
            elif hasattr(target, "process_name"):
                return target.process_name
            elif isinstance(target, dict):
                return target.get("name", None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        return None

    def _rotate_if_needed(self):
        """Auto-rotate log file if it exceeds max size."""
        if os.path.exists(self.log_file):
            size_mb = os.path.getsize(self.log_file) / (1024 * 1024)
            if size_mb > MAX_LOG_SIZE_MB:
                rotated_name = f"{self.log_file}.old"
                os.replace(self.log_file, rotated_name)
                with open(self.log_file, "w") as f:
                    f.write(f"--- Log rotated on {datetime.now()} ---\n")


# --- Safe Demo ---
if __name__ == "__main__":
    from types import SimpleNamespace
    fake_rule = {"id": 1, "type": "process_name", "value": "chrome", "action": "block"}
    fake_target = SimpleNamespace(pid=17428, process_name="chrome.exe", local_ip=None)

    logger = FirewallLogger()
    logger.log_decision(fake_target, fake_rule, "chrome.exe would be blocked (simulated)")
    logger.show_recent_logs()
