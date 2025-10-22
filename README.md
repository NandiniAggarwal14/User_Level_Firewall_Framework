# 🧱 User-Level Firewall Simulation

## 📘 Overview
This project demonstrates a **user-level firewall framework** designed to simulate **OS process monitoring**, **network connection tracking**, and **rule-based access control**.  
It allows users to visualize how a firewall interacts with processes, connections, and user-defined security rules in a controlled environment.

The system provides a **Tkinter-based GUI** that manages simulated processes and connections, applies rule-based decisions, and logs every activity for evaluation — making it a powerful educational tool for understanding OS-level firewall operations.

---

## 🚀 Features

- **Process Monitoring:**  
  Simulates running processes, allowing operations such as blocking, terminating, or inspecting them.

- **Connection Tracking:**  
  Tracks simulated network connections and allows the user to view or act upon them.

- **Rule Engine:**  
  Uses a JSON-based rule set (`rules.json`) to determine which actions to take (allow, block, alert) for specific processes or connections.

- **Action Simulation:**  
  Emulates firewall responses — such as blocking a process, closing a connection, or alerting the user — without modifying the real system.

- **Logging System:**  
  Every decision, event, and simulated action is logged in `firewall_log.jsonl` for performance evaluation and analysis.

- **User-Friendly GUI:**  
  Built with Tkinter (`ui.py`), the interface allows intuitive management of all components — from process control to log viewing.

---

## 🧩 Project Structure

| File | Description |
|------|--------------|
| `main.py` | Entry point of the project; initializes and runs the GUI application. |
| `ui.py` | Implements the Tkinter-based graphical interface for user interaction. |
| `process_manager.py` | Handles simulated process creation, blocking, and termination. |
| `connection_tracker.py` | Manages simulated network connections and tracks their states. |
| `rule_engine.py` | Loads and evaluates security rules from `rules.json`. |
| `action_simulator.py` | Simulates real-world firewall actions based on rule outcomes. |
| `logger.py` | Defines the `FirewallLogger` class for structured event logging. |
| `rules.json` | JSON configuration file containing firewall rules and permissions. |
| `firewall_log.jsonl` | Line-by-line JSON log file storing all actions, events, and alerts. |
| `.gitignore` | Excludes unnecessary files and directories from version control. |

---

## ⚙️ How It Works (Simulation Flow)

1. **Process and Connection Simulation:**  
   The `ProcessManager` and `ConnectionTracker` generate mock process and connection data for simulation.

2. **Rule Evaluation:**  
   The `RuleEngine` loads and checks the rules defined in `rules.json` against each simulated event.

3. **Action Execution:**  
   The `ActionSimulator` enforces the firewall decision (allow/block/alert).

4. **Logging:**  
   The `FirewallLogger` records all firewall actions and user interactions in `firewall_log.jsonl`.

5. **GUI Interaction:**  
   The `FirewallGUI` (from `ui.py`) provides controls for viewing processes, connections, logs, and applying manual rules.

---

## 🖥️ Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. Interact with the GUI to:
   - View running processes and connections.
   - Apply or modify firewall rules.
   - View simulated logs and actions.
   - Test blocking or allowing simulated processes.

---

## 📊 Future Enhancements (Planned)

In future versions, this simulation will evolve into a **real-time firewall system** that:
- Monitors **actual OS processes** using `psutil` and `socket`.
- Performs **live network tracking** and system-level rule enforcement.
- Integrates **performance evaluation metrics** for assessing firewall efficiency.
- Supports **real-time alerts and adaptive rule learning**.
