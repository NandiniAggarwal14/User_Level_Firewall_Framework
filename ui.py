import tkinter as tk
from tkinter import ttk, messagebox
from process_manager import ProcessManager
from connection_tracker import ConnectionTracker
from rule_engine import RuleEngine
from action_simulator import ActionSimulator
from logger import FirewallLogger

class FirewallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("User-Level Firewall Simulation")
        self.root.geometry("950x650")

        # --- Initialize modules ---
        self.pm = ProcessManager()
        self.ct = ConnectionTracker()
        self.re = RuleEngine()
        self.act = ActionSimulator()
        self.logger = FirewallLogger()

        # --- Setup demo ---
        self.setup_demo()

        # --- Tabs ---
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

        # --- Populate tabs ---
        self.create_proc_tab()
        self.create_conn_tab()
        self.create_rule_tab()
        self.create_log_tab()

        # --- Add sections for dynamic addition ---
        self.create_add_process_section()
        self.create_add_rule_section()

    # --- Demo setup ---
    def setup_demo(self):
        demo_processes = [("Chrome",3),("Spotify",2),("VSCode",1),("Slack",4)]
        for name, priority in demo_processes:
            self.pm.add_process(name, priority)
        self.ct.generate_connections(self.pm.process_list)
        self.re.load_rules()

    # --- Processes Tab ---
    def create_proc_tab(self):
        self.proc_tree = ttk.Treeview(self.proc_tab, columns=("PID","Name","Priority","State"), show="headings")
        for col in ("PID","Name","Priority","State"):
            self.proc_tree.heading(col, text=col)
            self.proc_tree.column(col, width=120)
        self.proc_tree.pack(expand=1, fill="both")
        refresh_btn = tk.Button(self.proc_tab, text="Refresh", command=self.refresh_proc_tab)
        refresh_btn.pack(pady=5)
        self.refresh_proc_tab()

    def refresh_proc_tab(self):
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        for p in self.pm.process_list:
            self.proc_tree.insert("", "end", values=(p.pid, p.name, p.priority, p.state))

    # --- Add Process Section ---
    def create_add_process_section(self):
        frame = tk.Frame(self.proc_tab)
        frame.pack(pady=5)
        tk.Label(frame, text="Process Name:").grid(row=0, column=0)
        self.proc_name_entry = tk.Entry(frame)
        self.proc_name_entry.grid(row=0, column=1)
        tk.Label(frame, text="Priority:").grid(row=0, column=2)
        self.proc_priority_entry = tk.Entry(frame, width=5)
        self.proc_priority_entry.grid(row=0, column=3)
        add_btn = tk.Button(frame, text="Add Process", command=self.add_process_gui)
        add_btn.grid(row=0, column=4, padx=5)

    def add_process_gui(self):
        name = self.proc_name_entry.get()
        try:
            priority = int(self.proc_priority_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Priority must be an integer")
            return
        if name:
            self.pm.add_process(name, priority)
            self.refresh_proc_tab()
            self.proc_name_entry.delete(0, tk.END)
            self.proc_priority_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Process '{name}' added!")
        else:
            messagebox.showerror("Error", "Process name cannot be empty")

    # --- Connections Tab ---
    def create_conn_tab(self):
        self.conn_tree = ttk.Treeview(self.conn_tab, columns=("PID","Local Port","Remote Address","Status"), show="headings")
        for col in ("PID","Local Port","Remote Address","Status"):
            self.conn_tree.heading(col, text=col)
            self.conn_tree.column(col, width=150)
        self.conn_tree.pack(expand=1, fill="both")
        refresh_btn = tk.Button(self.conn_tab, text="Refresh", command=self.refresh_conn_tab)
        refresh_btn.pack(pady=5)
        self.refresh_conn_tab()

    def refresh_conn_tab(self):
        for i in self.conn_tree.get_children():
            self.conn_tree.delete(i)
        for c in self.ct.connections:
            remote = f"{getattr(c,'remote_ip','')}:{getattr(c,'remote_port','')}"
            self.conn_tree.insert("", "end", values=(c.pid, getattr(c,"local_port",None), remote, getattr(c,"status","")))

    # --- Rules Tab ---
    def create_rule_tab(self):
        self.rule_tree = ttk.Treeview(self.rule_tab, columns=("ID","Type","Value","Action"), show="headings")
        for col in ("ID","Type","Value","Action"):
            self.rule_tree.heading(col, text=col)
            self.rule_tree.column(col, width=150)
        self.rule_tree.pack(expand=1, fill="both")
        refresh_btn = tk.Button(self.rule_tab, text="Refresh", command=self.refresh_rule_tab)
        refresh_btn.pack(pady=5)
        self.refresh_rule_tab()

    def refresh_rule_tab(self):
        for i in self.rule_tree.get_children():
            self.rule_tree.delete(i)
        for r in self.re.rules:
            self.rule_tree.insert("", "end", values=(r["id"], r["type"], r["value"], r["action"]))

    # --- Add Rule Section ---
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
        messagebox.showinfo("Success", f"Rule '{rule_id}' added!")
        self.rule_id_entry.delete(0, tk.END)
        self.rule_type_entry.delete(0, tk.END)
        self.rule_value_entry.delete(0, tk.END)
        self.rule_action_entry.delete(0, tk.END)

    # --- Logs Tab ---
    def create_log_tab(self):
        self.log_tree = ttk.Treeview(self.log_tab, columns=("Timestamp","PID","Rule","Action","Result"), show="headings")
        for col in ("Timestamp","PID","Rule","Action","Result"):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)
        self.log_tree.pack(expand=1, fill="both")

        refresh_btn = tk.Button(self.log_tab, text="Refresh Logs", command=self.refresh_log_tab)
        refresh_btn.pack(pady=5)

        action_btn = tk.Button(self.log_tab, text="Apply Rules to All", command=self.apply_rules_to_all)
        action_btn.pack(pady=5)

        self.refresh_log_tab()

    def refresh_log_tab(self):
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
        records = self.logger.query_logs()
        for rec in records:
            self.log_tree.insert("", "end", values=(rec["timestamp"], rec["pid"], rec["rule_id"], rec["action"], rec["result"]))

    # --- Apply all rules simulation ---
    def apply_rules_to_all(self):
        # Processes
        for proc in self.pm.process_list:
            matched_rules = self.re.match_process({"pid": proc.pid, "name": proc.name})
            for rule in matched_rules:
                result = self.act.apply_action(proc, rule)
                self.logger.log_decision(proc.pid, rule=rule, result=result["result"])

        # Connections
        for conn in self.ct.connections:
            matched_rules = self.re.match_connection(conn)
            for rule in matched_rules:
                result = self.act.apply_action(conn, rule)
                self.logger.log_decision(getattr(conn,"pid",None),
                                         port=getattr(conn,"local_port",None),
                                         rule=rule,
                                         result=result["result"])

        self.refresh_proc_tab()
        self.refresh_conn_tab()
        self.refresh_rule_tab()
        self.refresh_log_tab()
        messagebox.showinfo("Simulation", "Rules applied and logs updated!")

# --- Run GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FirewallGUI(root)
    root.mainloop()
