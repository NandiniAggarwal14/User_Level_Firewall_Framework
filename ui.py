import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
from datetime import datetime
from collections import deque

from process_manager import ProcessManager
from connection_tracker import ConnectionTracker
from rule_engine import RuleEngine
from action_simulator import ActionSimulator
from logger import FirewallLogger


class FirewallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("User-Level Firewall - Performance Monitor")
        self.root.geometry("1100x700")
        
        # Configure root window
        self.root.configure(bg='#f0f0f0')

        self.pm = ProcessManager()
        self.ct = ConnectionTracker()
        self.re = RuleEngine()
        self.logger = FirewallLogger()
        self.act = ActionSimulator(self.logger)
        
        # Track connection start times
        self.connection_start_times = {}
        
        # Data for live graphs
        self.cpu_data = deque(maxlen=60)  # Last 60 data points
        self.memory_data = deque(maxlen=60)
        self.time_labels = deque(maxlen=60)
        
        # Monitoring flags
        self.monitoring_active = False
        
        # Initialize with some data
        self.cpu_data.append(0)
        self.memory_data.append(0)

        self.tab_control = ttk.Notebook(root)
        self.proc_tab = ttk.Frame(self.tab_control)
        self.conn_tab = ttk.Frame(self.tab_control)
        self.rule_tab = ttk.Frame(self.tab_control)
        self.log_tab = ttk.Frame(self.tab_control)
        self.perf_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.proc_tab, text="📊 Processes")
        self.tab_control.add(self.conn_tab, text="🌐 Connections")
        self.tab_control.add(self.rule_tab, text="📜 Rules")
        self.tab_control.add(self.log_tab, text="📝 Logs")
        self.tab_control.add(self.perf_tab, text="⚡ Performance Monitor")
        self.tab_control.pack(expand=1, fill="both")

        self.create_proc_tab()
        self.create_conn_tab()
        self.create_rule_tab()
        self.create_log_tab()
        self.create_add_rule_section()
        self.create_perf_tab()
        
        # Start monitoring thread after UI is ready
        self.root.after(1000, self.start_monitoring)

    # ----------------------------
    # PROCESS TAB
    # ----------------------------
    def create_proc_tab(self):
        self.proc_tree = ttk.Treeview(self.proc_tab, columns=("PID", "Name", "User", "Status"), show="headings")
        self.proc_tree.heading("PID", text="PID")
        self.proc_tree.heading("Name", text="Name")
        self.proc_tree.heading("User", text="User")
        self.proc_tree.heading("Status", text="Status")
        
        self.proc_tree.column("PID", width=100)
        self.proc_tree.column("Name", width=250)
        self.proc_tree.column("User", width=200)
        self.proc_tree.column("Status", width=150)
        self.proc_tree.pack(expand=1, fill="both")

        refresh_btn = tk.Button(self.proc_tab, text="Refresh", command=self.refresh_proc_tab)
        refresh_btn.pack(pady=5)
        self.refresh_proc_tab()

    def refresh_proc_tab(self):
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        
        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                self.proc_tree.insert("", "end", values=(
                    proc.pid, 
                    proc.name()[:40] if proc.name() else "N/A", 
                    proc.username()[:25] if proc.username() else "N/A", 
                    proc.status() if proc.status() else "N/A"
                ))
                count += 1
                if count >= 100:  # Limit to first 100 processes
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    # ----------------------------
    # CONNECTION TAB
    # ----------------------------
    def create_conn_tab(self):
        self.conn_tree = ttk.Treeview(self.conn_tab, columns=("PID", "Process", "Local", "Remote", "Status"), show="headings")
        self.conn_tree.heading("PID", text="PID")
        self.conn_tree.heading("Process", text="Process")
        self.conn_tree.heading("Local", text="Local")
        self.conn_tree.heading("Remote", text="Remote")
        self.conn_tree.heading("Status", text="Status")
        
        self.conn_tree.column("PID", width=80)
        self.conn_tree.column("Process", width=180)
        self.conn_tree.column("Local", width=180)
        self.conn_tree.column("Remote", width=180)
        self.conn_tree.column("Status", width=120)
        self.conn_tree.pack(expand=1, fill="both")

        refresh_btn = tk.Button(self.conn_tab, text="Refresh Connections", command=self.refresh_conn_tab)
        refresh_btn.pack(pady=5)
        self.refresh_conn_tab()

    def refresh_conn_tab(self):
        for i in self.conn_tree.get_children():
            self.conn_tree.delete(i)
        
        try:
            self.ct.fetch_connections()
        except Exception as e:
            print(f"Error fetching connections: {e}")
            return
        
        count = 0
        for conn in self.ct.connections:
            try:
                pname = psutil.Process(conn.pid).name() if conn.pid else "System"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pname = "Unknown"
            
            local = f"{conn.local_ip}:{conn.local_port}" if conn.local_ip else "-"
            remote = f"{conn.remote_ip}:{conn.remote_port}" if conn.remote_ip else "-"
            
            self.conn_tree.insert("", "end", values=(conn.pid, pname[:25], local[:25], remote[:25], conn.status))
            
            count += 1
            if count >= 50:  # Limit to 50 connections
                break

    # ----------------------------
    # RULE TAB
    # ----------------------------
    def create_rule_tab(self):
        self.rule_tree = ttk.Treeview(self.rule_tab, columns=("ID", "Type", "Value", "Action"), show="headings")
        for col in ("ID", "Type", "Value", "Action"):
            self.rule_tree.heading(col, text=col)
            self.rule_tree.column(col, width=180)
        self.rule_tree.pack(expand=1, fill="both")

        refresh_btn = tk.Button(self.rule_tab, text="Refresh Rules", command=self.refresh_rule_tab)
        refresh_btn.pack(pady=5)
        self.refresh_rule_tab()

    def refresh_rule_tab(self):
        for i in self.rule_tree.get_children():
            self.rule_tree.delete(i)
        for r in self.re.rules:
            self.rule_tree.insert("", "end", values=(r["id"], r["type"], r["value"], r["action"]))

    def create_add_rule_section(self):
        frame = tk.Frame(self.rule_tab)
        frame.pack(pady=5)
        tk.Label(frame, text="Rule ID:").grid(row=0, column=0)
        self.rule_id_entry = tk.Entry(frame)
        self.rule_id_entry.grid(row=0, column=1)
        tk.Label(frame, text="Type:").grid(row=0, column=2)
        self.rule_type_entry = tk.Entry(frame)
        self.rule_type_entry.grid(row=0, column=3)
        tk.Label(frame, text="Value:").grid(row=1, column=0)
        self.rule_value_entry = tk.Entry(frame)
        self.rule_value_entry.grid(row=1, column=1)
        tk.Label(frame, text="Action:").grid(row=1, column=2)
        self.rule_action_entry = tk.Entry(frame)
        self.rule_action_entry.grid(row=1, column=3)
        add_btn = tk.Button(frame, text="Add Rule", command=self.add_rule_gui)
        add_btn.grid(row=1, column=4, padx=5)

    def add_rule_gui(self):
        rule_id = self.rule_id_entry.get()
        rule_type = self.rule_type_entry.get()
        rule_value = self.rule_value_entry.get()
        rule_action = self.rule_action_entry.get()
        if not all([rule_id, rule_type, rule_value, rule_action]):
            messagebox.showerror("Error", "All fields are required")
            return
        new_rule = {"id": rule_id, "type": rule_type, "value": rule_value, "action": rule_action}
        self.re.rules.append(new_rule)
        self.re.save_rules()
        self.refresh_rule_tab()
        messagebox.showinfo("Success", f"Rule '{rule_id}' added successfully!")
        self.rule_id_entry.delete(0, tk.END)
        self.rule_type_entry.delete(0, tk.END)
        self.rule_value_entry.delete(0, tk.END)
        self.rule_action_entry.delete(0, tk.END)

    # ----------------------------
    # LOG TAB
    # ----------------------------
    def create_log_tab(self):
        self.log_tree = ttk.Treeview(self.log_tab, columns=("Timestamp", "PID", "Process", "Rule", "Action", "Result"), show="headings")
        for col in ("Timestamp", "PID", "Process", "Rule", "Action", "Result"):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=140)
        self.log_tree.pack(expand=1, fill="both")

        tk.Button(self.log_tab, text="Refresh Logs", command=self.refresh_log_tab).pack(pady=5)
        tk.Button(self.log_tab, text="Apply Rules to All", command=self.apply_rules_to_all).pack(pady=5)

        self.refresh_log_tab()

    def refresh_log_tab(self):
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
        records = self.logger.query_logs()
        for rec in records[-25:]:
            pname = rec.get("process_name", "Unknown")
            self.log_tree.insert("", "end", values=(rec["timestamp"], rec["pid"], pname, rec["rule_id"], rec["action"], rec["result"]))

    # ----------------------------
    # PERFORMANCE MONITOR TAB
    # ----------------------------
    def create_perf_tab(self):
        # Main container with two sections
        top_frame = tk.Frame(self.perf_tab)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CPU Graph
        cpu_frame = tk.LabelFrame(top_frame, text="CPU Usage (%)", font=('Arial', 10, 'bold'))
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.cpu_canvas = tk.Canvas(cpu_frame, bg='white', height=200)
        self.cpu_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory Graph
        mem_frame = tk.LabelFrame(top_frame, text="Memory Usage (%)", font=('Arial', 10, 'bold'))
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.mem_canvas = tk.Canvas(mem_frame, bg='white', height=200)
        self.mem_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistics section
        stats_frame = tk.LabelFrame(self.perf_tab, text="System Statistics", font=('Arial', 10, 'bold'))
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Create stats labels
        stats_inner = tk.Frame(stats_frame)
        stats_inner.pack(padx=10, pady=10)
        
        self.cpu_label = tk.Label(stats_inner, text="Current CPU: 0.0%", font=('Arial', 10))
        self.cpu_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        self.mem_label = tk.Label(stats_inner, text="Current Memory: 0.0%", font=('Arial', 10))
        self.mem_label.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        
        self.proc_count_label = tk.Label(stats_inner, text="Active Processes: 0", font=('Arial', 10))
        self.proc_count_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        
        self.conn_count_label = tk.Label(stats_inner, text="Active Connections: 0", font=('Arial', 10))
        self.conn_count_label.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        self.uptime_label = tk.Label(stats_inner, text="Monitoring Time: 0s", font=('Arial', 10))
        self.uptime_label.grid(row=2, column=0, padx=20, pady=5, sticky='w')
        
        self.firewall_cpu_label = tk.Label(stats_inner, text="Firewall CPU: 0.0%", font=('Arial', 10))
        self.firewall_cpu_label.grid(row=2, column=1, padx=20, pady=5, sticky='w')
    
    def start_monitoring(self):
        """Start the monitoring thread after UI is initialized"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitor_thread.start()
        print("✅ Performance monitoring started!")
    
    def monitor_system(self):
        """Background thread to collect system metrics"""
        start_time = time.time()
        
        try:
            firewall_proc = psutil.Process()  # Current process (firewall)
        except:
            firewall_proc = None
        
        while self.monitoring_active:
            try:
                # Collect metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                mem_percent = psutil.virtual_memory().percent
                
                current_time = datetime.now().strftime("%H:%M:%S")
                
                self.cpu_data.append(cpu_percent)
                self.memory_data.append(mem_percent)
                self.time_labels.append(current_time)
                
                # Get process and connection counts
                try:
                    proc_count = len(list(psutil.process_iter()))
                except:
                    proc_count = 0
                
                try:
                    self.ct.fetch_connections()
                    conn_count = len(self.ct.connections)
                except:
                    conn_count = 0
                
                # Get firewall's own CPU usage
                if firewall_proc:
                    try:
                        firewall_cpu = firewall_proc.cpu_percent(interval=0.1)
                    except:
                        firewall_cpu = 0.0
                else:
                    firewall_cpu = 0.0
                
                # Calculate uptime
                uptime_seconds = int(time.time() - start_time)
                if uptime_seconds < 60:
                    uptime_str = f"{uptime_seconds}s"
                elif uptime_seconds < 3600:
                    uptime_str = f"{uptime_seconds//60}m {uptime_seconds%60}s"
                else:
                    uptime_str = f"{uptime_seconds//3600}h {(uptime_seconds%3600)//60}m"
                
                # Update UI (thread-safe)
                try:
                    self.root.after(0, self.update_perf_display, cpu_percent, mem_percent, 
                                   proc_count, conn_count, uptime_str, firewall_cpu)
                except:
                    pass
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)
    
    def update_perf_display(self, cpu, mem, proc_count, conn_count, uptime, fw_cpu):
        """Update performance graphs and statistics (called from main thread)"""
        # Update statistics labels
        self.cpu_label.config(text=f"Current CPU: {cpu:.1f}%")
        self.mem_label.config(text=f"Current Memory: {mem:.1f}%")
        self.proc_count_label.config(text=f"Active Processes: {proc_count}")
        self.conn_count_label.config(text=f"Active Connections: {conn_count}")
        self.uptime_label.config(text=f"Monitoring Time: {uptime}")
        self.firewall_cpu_label.config(text=f"Firewall CPU: {fw_cpu:.1f}%")
        
        # Draw graphs
        self.draw_graph(self.cpu_canvas, self.cpu_data, "CPU", "#FF6B6B", max_val=100)
        self.draw_graph(self.mem_canvas, self.memory_data, "Memory", "#4ECDC4", max_val=100)
    
    def draw_graph(self, canvas, data, label, color, max_val=100):
        """Draw a line graph on the canvas"""
        canvas.delete("all")
        
        if len(data) < 2:
            return
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Margins
        margin_left = 40
        margin_right = 10
        margin_top = 20
        margin_bottom = 30
        
        graph_width = width - margin_left - margin_right
        graph_height = height - margin_top - margin_bottom
        
        if graph_width <= 0 or graph_height <= 0:
            return
        
        # Draw axes
        canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom, width=2)
        canvas.create_line(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom, width=2)
        
        # Draw grid lines and Y-axis labels
        for i in range(0, 101, 25):
            y = height - margin_bottom - (i / max_val) * graph_height
            canvas.create_line(margin_left, y, width - margin_right, y, fill='#E0E0E0', dash=(2, 2))
            canvas.create_text(margin_left - 5, y, text=f"{i}", anchor='e', font=('Arial', 8))
        
        # Draw data line
        points = []
        data_list = list(data)
        for i, value in enumerate(data_list):
            x = margin_left + (i / (len(data_list) - 1)) * graph_width
            y = height - margin_bottom - (value / max_val) * graph_height
            points.extend([x, y])
        
        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=2, smooth=True)
            
            # Draw points
            for i in range(0, len(points), 2):
                canvas.create_oval(points[i]-2, points[i+1]-2, points[i]+2, points[i+1]+2, 
                                  fill=color, outline=color)
        
        # Draw current value
        if data_list:
            current_val = data_list[-1]
            canvas.create_text(width // 2, 10, text=f"{label}: {current_val:.1f}%", 
                             font=('Arial', 10, 'bold'), fill=color)

    # ----------------------------
    # APPLY RULES (CORE)
    # ----------------------------
    def apply_rules_to_all(self):
        # Apply to all live processes
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            matched_rules = self.re.match_process(proc)
            for rule in matched_rules:
                self.act.apply_action(proc, rule)

        # Apply to all active connections
        self.ct.fetch_connections()
        for conn in self.ct.connections:
            matched_rules = self.re.match_connection(conn)
            for rule in matched_rules:
                self.act.apply_action(conn, rule)

        self.refresh_proc_tab()
        self.refresh_conn_tab()
        self.refresh_rule_tab()
        self.refresh_log_tab()
        messagebox.showinfo("Simulation Complete", "Rules applied (safe simulation). Logs updated!")


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 USER-LEVEL FIREWALL - PERFORMANCE MONITOR 🔥")
    print("=" * 60)
    print("Starting GUI application...")
    print("✅ Loading components...")
    
    try:
        root = tk.Tk()
        print("✅ Tkinter initialized")
        
        app = FirewallGUI(root)
        print("✅ GUI created successfully!")
        print("=" * 60)
        print("📊 Features:")
        print("  • Process monitoring with CPU & Memory metrics")
        print("  • Connection tracking with duration")
        print("  • Live performance graphs")
        print("  • Real-time system statistics")
        print("=" * 60)
        print("🚀 Application running... Close window to exit.\n")
        
        root.mainloop()
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
