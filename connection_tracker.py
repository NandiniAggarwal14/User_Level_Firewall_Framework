import psutil
import socket

DRY_RUN = True  # safety flag: ensures we never modify or kill connections

class Connection:
    """Represents a real network connection (safe read-only)."""
    def __init__(self, pid, laddr, raddr, status):
        self.pid = pid
        self.local_ip = laddr.ip if laddr else None
        self.local_port = laddr.port if laddr else None
        self.remote_ip = raddr.ip if raddr else None
        self.remote_port = raddr.port if raddr else None
        self.status = status

    def __str__(self):
        return (f"PID:{self.pid} | Local:{self.local_ip}:{self.local_port} | "
                f"Remote:{self.remote_ip}:{self.remote_port} | Status:{self.status}")


class ConnectionTracker:
    """Tracks *real* network connections, safely (no destructive actions)."""
    def __init__(self):
        self.connections = []

    def fetch_connections(self):
        """Fetch active and listening sockets from the system."""
        self.connections.clear()
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr:  # skip sockets without local address
                    self.connections.append(Connection(
                        conn.pid,
                        conn.laddr,
                        conn.raddr if conn.raddr else None,
                        conn.status
                    ))
        except psutil.AccessDenied:
            print("⚠️ Some system connections are hidden (access denied).")
        except Exception as e:
            print(f"⚠️ Error while fetching connections: {e}")

    def list_connections(self, limit=25):
        """Display both LISTENING and ESTABLISHED connections."""
        if not self.connections:
            print("No connections found.")
            return

        # Separate inbound vs outbound
        listening = [c for c in self.connections if c.status == 'LISTEN']
        active = [c for c in self.connections if c.status == 'ESTABLISHED']

        # --- LISTENING PORTS TABLE ---
        if listening:
            print(f"\n🔵 --- Listening Ports (waiting for incoming connections) ---")
            print(f"{'PID':<6}{'Process':<25}{'Local Address':<25}{'Status':<12}")
            print("-" * 70)
            for conn in listening[:limit]:
                local = f"{conn.local_ip}:{conn.local_port}" if conn.local_ip else "-"
                try:
                    pname = psutil.Process(conn.pid).name() if conn.pid else "System"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pname = "Unknown"
                print(f"{conn.pid or '-':<6}{pname[:23]:<25}{local:<25}{conn.status:<12}")
            print(f"[Showing {min(limit, len(listening))}/{len(listening)} listening sockets]\n")
        else:
            print("\n🔵 No LISTENING sockets detected.\n")

        # --- ESTABLISHED CONNECTIONS TABLE ---
        if active:
            print(f"\n🟢 --- Established Connections (active data flow) ---")
            print(f"{'PID':<6}{'Process':<25}{'Local → Remote':<45}{'Status':<12}")
            print("-" * 90)
            for conn in active[:limit]:
                local = f"{conn.local_ip}:{conn.local_port}" if conn.local_ip else "-"
                remote = f"{conn.remote_ip}:{conn.remote_port}" if conn.remote_ip else "-"
                try:
                    pname = psutil.Process(conn.pid).name() if conn.pid else "System"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pname = "Unknown"
                print(f"{conn.pid or '-':<6}{pname[:23]:<25}{(local + ' → ' + remote):<45}{conn.status:<12}")
            print(f"[Showing {min(limit, len(active))}/{len(active)} active connections]\n")
        else:
            print("\n🟢 No ESTABLISHED connections detected.\n")

    def find_owner_of_port(self, port):
        """Find process that owns a given local port (if any)."""
        matches = [c for c in self.connections if c.local_port == port]
        if not matches:
            print(f"No process is currently using port {port}.")
            return

        print(f"\nPort {port} is used by:")
        for conn in matches:
            try:
                p = psutil.Process(conn.pid)
                print(f"PID {conn.pid:<6} → {p.name()} (User: {p.username()}) | Status: {conn.status}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"PID {conn.pid} → [Access Denied or Process Ended] | Status: {conn.status}")

# --- Demo Execution ---
if __name__ == "__main__":
    tracker = ConnectionTracker()

    while True:
        print("\n--- Connection Tracker ---")
        print("1: Refresh connections")
        print("2: Show connections (Listening + Active)")
        print("3: Find owner of a port")
        print("0: Exit")
        choice = input("Select action: ")

        if choice == '1':
            tracker.fetch_connections()
            print("✅ Connections updated.")
        elif choice == '2':
            tracker.list_connections()
        elif choice == '3':
            port = int(input("Enter port number: "))
            tracker.find_owner_of_port(port)
        elif choice == '0':
            print("Exiting Connection Tracker safely.")
            break
        else:
            print("Invalid choice. Try again.")
