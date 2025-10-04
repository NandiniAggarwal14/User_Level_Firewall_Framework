import random
import time

# --- Process Class ---
class Process:
    """Represents a single simulated process."""
    def __init__(self, pid, name, priority):
        self.pid = pid
        self.name = name
        self.priority = priority
        self.state = 'Ready'  # States: Ready, Running, Blocked, Terminated

    def __str__(self):
        return f"PID:{self.pid}, Name:{self.name}, Priority:{self.priority}, State:{self.state}"

# --- Process Manager ---
class ProcessManager:
    """Manages the lifecycle of all simulated processes."""
    def __init__(self):
        self.process_list = []
        self.pid_counter = 1

    # Add a process
    def add_process(self, name, priority):
        process = Process(self.pid_counter, name, priority)
        self.process_list.append(process)
        print(f"Added: {process}")
        self.pid_counter += 1

    # Show processes in a table
    def show_processes(self):
        print("\n--- Current Process Table ---")
        active_processes = [p for p in self.process_list if p.state != 'Terminated']
        if not active_processes:
            print("No active processes.")
            return
        # Sort by priority (lower number = higher priority)
        active_processes.sort(key=lambda x: x.priority)
        print(f"{'PID':<5} {'Name':<15} {'Priority':<10} {'State':<10}")
        print("-" * 42)
        for p in active_processes:
            print(f"{p.pid:<5} {p.name:<15} {p.priority:<10} {p.state:<10}")

    # Run processes by priority
    def run_processes(self):
        print("\n--- Running Processes by Priority ---")
        for process in sorted(self.process_list, key=lambda x: x.priority):
            if process.state in ['Ready', 'Blocked']:
                process.state = 'Running'
                print(f"Running: {process}")
                time.sleep(0.5)  # Simulate time slice
                if process.state != 'Blocked':
                    process.state = 'Ready'
                print(f"State Updated: {process}")

    # Terminate a process
    def terminate_process(self, pid):
        for p in self.process_list:
            if p.pid == pid:
                p.state = 'Terminated'
                print(f"Action: Process {pid} ({p.name}) was Terminated.")
                return
        print(f"Action: Process with PID {pid} not found.")

    # Block a process
    def block_process(self, pid):
        for p in self.process_list:
            if p.pid == pid:
                p.state = 'Blocked'
                print(f"Action: Process {pid} ({p.name}) was Blocked.")
                return
        print(f"Action: Process with PID {pid} not found.")

# --- Demo Execution ---
if __name__ == "__main__":
    pm = ProcessManager()

    # Auto-generate random demo processes
    demo_names = ['Chrome', 'Spotify', 'VSCode', 'Slack', 'Discord', 'Notepad', 'Telegram']
    for name in demo_names:
        pm.add_process(name, random.randint(1, 5))

    # Show initial table
    pm.show_processes()

    # --- Interactive Firewall Actions ---
    while True:
        print("\n--- Firewall Actions ---")
        print("1: Block a process")
        print("2: Terminate a process")
        print("3: Run processes")
        print("4: Show processes")
        print("5: Add a process")
        print("0: Exit")
        choice = input("Select action: ")

        if choice == '1':
            pid = int(input("Enter PID to block: "))
            pm.block_process(pid)
        elif choice == '2':
            pid = int(input("Enter PID to terminate: "))
            pm.terminate_process(pid)
        elif choice == '3':
            pm.run_processes()
        elif choice == '4':
            pm.show_processes()
        elif choice == '5':
            name = input("Enter process name: ")
            priority = int(input("Enter priority (1-5): "))
            pm.add_process(name, priority)
        elif choice == '0':
            print("Exiting Process Manager Demo.")
            break
        else:
            print("Invalid choice. Try again.")
