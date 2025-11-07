import tkinter as tk
from tkinter import ttk, messagebox
import psutil

from process_manager import ProcessManager
from connection_tracker import ConnectionTracker
from rule_engine import RuleEngine
from action_simulator import ActionSimulator
from logger import FirewallLogger


class FirewallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("User-Level Firewall Demonstration")
        self.root.geometry("950x650")

        self.pm = ProcessManager()
        self.ct = ConnectionTracker()
        self.re = RuleEngine()
        self.logger = FirewallLogger()
        self.act = ActionSimulator(self.logger) 

        self.tab_control = ttk.Notebook(root)
        self.proc_tab = ttk.Frame(self.tab_control)
        self.conn_tab = ttk.Frame(self.tab_control)
        self.rule_tab = ttk.Frame(self.tab_control)
        self.log_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.proc_tab, text="Processes")
        self.tab_control.add(self.conn_tab, text="Connections")
        self.tab_control.add(self.rule_tab, text="Rules")
        self.tab_control.add(self.log_tab, text="Logs")
        self.tab_control.pack(expand=1, fill="both")

        # Create GUI sections
        self.create_proc_tab()
        self.create_conn_tab()
        self.create_rule_tab()
        self.create_log_tab()
        self.create_add_rule_section()

    # ----------------------------
    # PROCESS TAB
    # ----------------------------
    def create_proc_tab(self):
        self.proc_tree = ttk.Treeview(self.proc_tab, columns=("PID", "Name", "User", "Status"), show="headings")
        for col in ("PID", "Name", "User", "Status"):
            self.proc_tree.heading(col, text=col)
            self.proc_tree.column(col, width=180)
        self.proc_tree.pack(expand=1, fill="both")

        refresh_btn = tk.Button(self.proc_tab, text="Refresh", command=self.refresh_proc_tab)
        refresh_btn.pack(pady=5)
        self.refresh_proc_tab()

    def refresh_proc_tab(self):
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                self.proc_tree.insert("", "end", values=(proc.pid, proc.name(), proc.username(), proc.status()))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # ----------------------------
    # CONNECTION TAB
    # ----------------------------
    def create_conn_tab(self):
        self.conn_tree = ttk.Treeview(self.conn_tab, columns=("PID", "Process", "Local", "Remote", "Status"), show="headings")
        for col in ("PID", "Process", "Local", "Remote", "Status"):
            self.conn_tree.heading(col, text=col)
            self.conn_tree.column(col, width=160)
        self.conn_tree.pack(expand=1, fill="both")

        refresh_btn = tk.Button(self.conn_tab, text="Refresh Connections", command=self.refresh_conn_tab)
        refresh_btn.pack(pady=5)
        self.refresh_conn_tab()

    def refresh_conn_tab(self):
        for i in self.conn_tree.get_children():
            self.conn_tree.delete(i)
        self.ct.fetch_connections()  # Real-time update
        for conn in self.ct.connections:
            try:
                pname = psutil.Process(conn.pid).name() if conn.pid else "System"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pname = "Unknown"
            local = f"{conn.local_ip}:{conn.local_port}" if conn.local_ip else "-"
            remote = f"{conn.remote_ip}:{conn.remote_port}" if conn.remote_ip else "-"
            self.conn_tree.insert("", "end", values=(conn.pid, pname, local, remote, conn.status))

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
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
