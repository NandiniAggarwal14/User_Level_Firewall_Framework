import psutil
import time

# Toggle this to False if you ever want real system control (⚠️ risky)
DRY_RUN = True

# --- Process Class ---
class Process:
    """Represents a single real process (read-only)."""
    def __init__(self, pid, name, username, status):
        self.pid = pid
        self.name = name
        self.username = username
        self.status = status  # e.g., running, sleeping, stopped, zombie

    def __str__(self):
        return f"PID:{self.pid}, Name:{self.name}, User:{self.username}, Status:{self.status}"

# --- Process Manager ---
class ProcessManager:
    """Manages real system processes in safe (non-destructive) mode."""
    def __init__(self):
        self.process_list = []

    def update_processes(self):
        """Fetch live process info from system (safe read-only)."""
        self.process_list.clear()
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                info = proc.info
                self.process_list.append(
                    Process(info['pid'], info['name'], info.get('username', 'N/A'), info['status'])
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def show_processes(self):
        """Display active processes in a simple table."""
        if not self.process_list:
            print("No processes available.")
            return

        print(f"\n{'PID':<8} {'Name':<25} {'User':<15} {'Status':<12}")
        print("-" * 65)
        for p in sorted(self.process_list, key=lambda x: x.name.lower() if x.name else "")[:25]:
            print(f"{p.pid:<8} {p.name[:23] if p.name else 'N/A':<25} {p.username[:13] if p.username else 'N/A':<15} {p.status:<12}")
        print(f"\n[Showing top {min(25, len(self.process_list))} processes out of {len(self.process_list)} total]\n")

    def block_process(self, pid):
        """Simulate blocking (dry-run only)."""
        target = next((p for p in self.process_list if p.pid == pid), None)
        if not target:
            print(f"Process with PID {pid} not found.")
            return

        if DRY_RUN:
            print(f"[DRY RUN] Would block process PID {pid} ({target.name})")
        else:
            # Real action placeholder (not executed for safety)
            pass

    def terminate_process(self, pid):
        """Simulate termination (dry-run only)."""
        target = next((p for p in self.process_list if p.pid == pid), None)
        if not target:
            print(f"Process with PID {pid} not found.")
            return

        if DRY_RUN:
            print(f"[DRY RUN] Would terminate process PID {pid} ({target.name})")
        else:
            try:
                proc = psutil.Process(pid)
                proc.terminate()  # ⚠️ Dangerous, only for controlled tests
                print(f"Terminated process PID {pid} ({target.name})")
            except psutil.AccessDenied:
                print(f"Permission denied to terminate PID {pid} ({target.name})")
            except psutil.NoSuchProcess:
                print(f"Process PID {pid} no longer exists.")

# --- Safe Demo Execution ---
if __name__ == "__main__":
    pm = ProcessManager()

    print("🔒 Real-Time Process Monitor (Safe Mode / DRY RUN)\n")

    while True:
        pm.update_processes()
        pm.show_processes()

        print("Options: 1=Block  2=Terminate  3=Refresh  0=Exit")
        choice = input("Select: ")

        if choice == '1':
            pid = int(input("Enter PID to simulate block: "))
            pm.block_process(pid)
        elif choice == '2':
            pid = int(input("Enter PID to simulate terminate: "))
            pm.terminate_process(pid)
        elif choice == '3':
            continue
        elif choice == '0':
            print("Exiting Process Manager safely.")
            break
        else:
            print("Invalid choice. Try again.")

        time.sleep(1)
