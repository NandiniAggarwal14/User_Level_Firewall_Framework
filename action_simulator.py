import psutil
from datetime import datetime
from logger import FirewallLogger

# Global safety switch — True means NO real termination or blocking.
DRY_RUN = True


class ActionSimulator:
    """Simulates (and optionally enforces) actions like block, allow, terminate."""

    def __init__(self, logger=None):
        self.action_log = []
        self.logger = logger or FirewallLogger()  # integrate with global firewall logger

    # ----------------------------
    # Main Action Dispatcher
    # ----------------------------
    def apply_action(self, target, rule):
        """
        Apply a rule to a process or connection.
        - target: psutil.Process, Connection object, or dict
        - rule: dict with keys (id, type, value, action)
        """
        action = rule.get("action", "allow").lower()
        pid = getattr(target, "pid", None)
        rule_id = rule.get("id", "N/A")

        # Determine simulated or real execution
        if action == "terminate":
            result = self._terminate(target)
        elif action == "block":
            result = self._block(target)
        elif action == "allow":
            result = self._allow(target)
        else:
            result = f"❓ Unknown action '{action}'"

        # Log locally
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pid": pid,
            "rule_id": rule_id,
            "action": action,
            "result": result,
        }
        self.action_log.append(log_entry)

        # Print to console
        print(f"PID {pid} | Rule {rule_id} | Action: {action.upper()} | Result: {result}")

        # Log using FirewallLogger (structured)
        if self.logger:
            self.logger.log_decision(target, rule, result)

        return result

    # ----------------------------
    # Internal Safe Simulations
    # ----------------------------
    def _terminate(self, target):
        """Terminate a process (simulated or real based on DRY_RUN)."""
        if DRY_RUN:
            return self._describe_target(target, "would be TERMINATED (simulated)")
        else:
            try:
                if isinstance(target, psutil.Process):
                    target.terminate()
                    return f"terminated process {target.pid}"
                else:
                    return self._describe_target(target, "terminated (non-process target)")
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                return f"termination failed (access denied or process ended)"

    def _block(self, target):
        """Block a process or connection (simulated)."""
        if DRY_RUN:
            return self._describe_target(target, "would be BLOCKED (simulated)")
        else:
            # Placeholder for future firewall-level enforcement
            return self._describe_target(target, "blocked (real)")

    def _allow(self, target):
        """Allow the process/connection (safe no-op)."""
        return self._describe_target(target, "allowed")

    # ----------------------------
    # Log Utilities
    # ----------------------------
    def show_action_log(self, limit=10):
        """Print the most recent actions."""
        if not self.action_log:
            print("No actions taken yet.")
            return
        print("\n--- Recent Action Log ---")
        for entry in self.action_log[-limit:]:
            print(f"[{entry['timestamp']}] PID {entry['pid']} | Rule {entry['rule_id']} | "
                  f"Action: {entry['action']} | Result: {entry['result']}")

    # ----------------------------
    # Helper Methods
    # ----------------------------
    def _describe_target(self, target, msg):
        """Create a descriptive string for the target."""
        try:
            if isinstance(target, psutil.Process):
                return f"{target.name()} (PID {target.pid}) {msg}"
            elif hasattr(target, "local_ip"):
                return f"Connection {target.local_ip}:{target.local_port} {msg}"
            elif isinstance(target, dict):
                pid = target.get("pid", "?")
                return f"Target PID {pid} {msg}"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return f"Process ended {msg}"
        return f"Unknown target {msg}"
