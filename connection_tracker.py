import random

class Connection:
    """Represents a simulated network connection."""
    def __init__(self, pid, local_port, remote_ip, remote_port, status):
        self.pid = pid
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.status = status  # e.g. 'LISTENING', 'ESTABLISHED', 'CLOSED'

    def __str__(self):
        return f"PID:{self.pid} | Local:{self.local_port} | Remote:{self.remote_ip}:{self.remote_port} | Status:{self.status}"


class ConnectionTracker:
    """Simulates tracking of network connections per process."""
    def __init__(self):
        self.connections = []  # List of Connection objects

    def generate_connections(self, processes):
        """Randomly assign simulated connections to existing processes."""
        self.connections.clear()
        possible_status = ['LISTENING', 'ESTABLISHED', 'CLOSED']
        for p in processes:
            num_conns = random.randint(1, 3)  # Each process gets 1–3 connections
            for _ in range(num_conns):
                local_port = random.randint(1000, 9999)
                remote_ip = f"192.168.1.{random.randint(2, 255)}"
                remote_port = random.randint(1000, 9999)
                status = random.choice(possible_status)
                conn = Connection(p.pid, local_port, remote_ip, remote_port, status)
                self.connections.append(conn)

    def list_connections(self):
        """Return all simulated connections."""
        if not self.connections:
            print("No active simulated connections found.")
            return
        print("\n--- Simulated Connection Table ---")
        print(f"{'PID':<6}{'Local Port':<12}{'Remote Address':<22}{'Status':<12}")
        print("-" * 55)
        for conn in self.connections:
            print(f"{conn.pid:<6}{conn.local_port:<12}{conn.remote_ip + ':' + str(conn.remote_port):<22}{conn.status:<12}")

    def find_owner_of_port(self, port):
        """Find which process owns a given local port."""
        owners = [c.pid for c in self.connections if c.local_port == port]
        if not owners:
            print(f"No simulated process is using port {port}.")
        else:
            print(f"Port {port} is owned by PID(s): {owners}")
        return owners


# --- Demo Execution ---
if __name__ == "__main__":
    from process_manager import ProcessManager  # Import your simulated process manager

    pm = ProcessManager()
    demo_names = ['Chrome', 'Spotify', 'VSCode', 'Slack', 'Discord', 'Notepad', 'Telegram']
    for name in demo_names:
        pm.add_process(name, random.randint(1, 5))

    pm.show_processes()

    ct = ConnectionTracker()
    ct.generate_connections(pm.process_list)
    ct.list_connections()

    while True:
        print("\n--- Connection Tracker Actions ---")
        print("1: Refresh simulated connections")
        print("2: Show all connections")
        print("3: Find owner of a port")
        print("0: Exit")
        choice = input("Select action: ")

        if choice == '1':
            ct.generate_connections(pm.process_list)
            print("Connections refreshed.")
        elif choice == '2':
            ct.list_connections()
        elif choice == '3':
            port = int(input("Enter port number: "))
            ct.find_owner_of_port(port)
        elif choice == '0':
            print("Exiting Connection Tracker Demo.")
            break
        else:
            print("Invalid choice. Try again.")
