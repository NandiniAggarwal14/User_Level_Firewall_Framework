class ActionSimulator:
    """Simulates actions (allow, block, terminate) on processes or connections."""

    def __init__(self):
        # Store a log of actions for later inspection
        self.action_log = []

    def apply_action(self, target, rule, dry_run=True):
        """
        Apply a rule to a target (process or connection).
        dry_run=True -> simulation only, no real termination
        """
        action = rule.get("action", "allow").lower()
        result = {"pid": getattr(target, "pid", None), "action": action, "rule_id": rule["id"]}

        if action == "terminate":
            self.simulate_terminate(target, dry_run)
            result["result"] = "terminated (simulated)" if dry_run else "terminated"
        elif action == "block":
            self.simulate_block(target)
            result["result"] = "blocked"
        elif action == "allow":
            self.simulate_allow(target)
            result["result"] = "allowed"
        else:
            result["result"] = f"unknown action '{action}'"

        # Log the action
        self.action_log.append(result)
        print(f"Action applied: PID {result['pid']} -> {result['action']} ({result['result']})")
        return result

    # --- Simulated actions ---
    def simulate_terminate(self, process, dry_run=True):
        """Simulate terminating a process."""
        if hasattr(process, "state"):
            process.state = "Terminated" if dry_run else "Terminated (real)"
        else:
            # For connections, just log
            pass

    def simulate_block(self, process):
        """Simulate blocking a process."""
        if hasattr(process, "state") and process.state != "Terminated":
            process.state = "Blocked"

    def simulate_allow(self, process):
        """Simulate allowing a process (no-op)."""
        pass

    # --- Utility ---
    def show_action_log(self):
        """Print all actions taken so far."""
        if not self.action_log:
            print("No actions have been taken yet.")
            return
        print("\n--- Action Log ---")
        for log in self.action_log:
            print(f"PID {log['pid']} | Rule {log['rule_id']} | Action: {log['action']} | Result: {log['result']}")
