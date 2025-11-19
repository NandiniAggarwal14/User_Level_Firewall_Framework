# 🧱 User-Level Firewall Framework with Performance Monitoring

## 📘 Overview
This project implements a **user-level firewall framework** with comprehensive **performance evaluation capabilities**. It monitors real OS processes and network connections, applies rule-based access control, and provides detailed performance metrics to evaluate firewall efficiency.

The system features a **Tkinter-based GUI** with live performance monitoring, showing real-time CPU and memory usage, rule processing statistics, and system overhead metrics — making it a powerful tool for understanding and optimizing firewall operations.

---

## 🚀 Key Features

### **Process Monitoring**
- Real-time monitoring of active system processes using `psutil`
- Display process details: PID, Name, User, Status
- Safe read-only mode with DRY_RUN protection

### **Connection Tracking**
- Live network connection monitoring (TCP/UDP)
- Track both LISTENING and ESTABLISHED connections
- Display local/remote addresses, ports, and connection status

### **Rule Engine**
- JSON-based rule configuration system
- Support for multiple rule types:
  - Process name matching
  - Username filtering
  - Port-based rules
  - IP address filtering
- Dynamic rule addition and modification through GUI

### **Performance Monitor (NEW!)** ⚡
- **Live System Graphs:**
  - Real-time CPU usage visualization (60-second rolling window)
  - Real-time Memory usage visualization
  - Smooth animated line charts with grid lines

- **System Statistics:**
  - Current CPU and Memory percentages
  - Active process count
  - Active connection count
  - Monitoring uptime

- **Firewall-Specific Metrics:**
  - **Total Rules Matched:** Cumulative rule matches
  - **Rules/Second:** Rule evaluation throughput
  - **Avg Rule Time:** Average processing time per rule (in milliseconds)
  - **Most Active Rule:** Identifies rules triggering most frequently
  - **Firewall CPU Overhead:** Resource consumption of firewall itself

### **Continuous Rule Evaluation**
- Background thread continuously evaluating rules against active processes/connections
- Simulates real-time firewall behavior
- Measures actual rule processing performance

### **Action Simulation**
- Safe simulation of firewall actions (block, allow, terminate)
- Logging of all decisions and actions
- No actual system modifications (DRY_RUN mode)

### **Structured Logging**
- JSONL format for easy parsing and analysis
- Timestamped records of all firewall decisions
- Query capabilities for filtering logs

---

## 🧩 Project Structure

| File | Description |
|------|--------------|
| `main.py` | CLI entry point demonstrating firewall components |
| `ui.py` | **Main GUI application** with performance monitoring dashboard |
| `process_manager.py` | Real process monitoring using psutil |
| `connection_tracker.py` | Network connection tracking and management |
| `rule_engine.py` | Rule loading, matching, and evaluation engine |
| `action_simulator.py` | Simulates firewall actions with logging |
| `logger.py` | Structured JSONL logging system |
| `rules.json` | Firewall rule configuration file |
| `firewall_log.jsonl` | Event and action log file |
| `requirements.txt` | Python dependencies (psutil>=7.1.0) |

---

## ⚙️ System Architecture

### **Real-Time Monitoring Flow:**
1. **Background Monitoring Thread:**
   - Collects system metrics every second
   - Updates live graphs and statistics
   - Tracks process and connection counts

2. **Continuous Rule Evaluation Thread:**
   - Samples processes and connections every 2 seconds
   - Evaluates rules and measures processing time
   - Updates firewall performance metrics

3. **GUI Main Thread:**
   - Renders visualizations and updates displays
   - Handles user interactions
   - Thread-safe updates via `root.after()`

### **Performance Measurement:**
- **Microsecond-precision timing** for rule evaluations
- **Rolling window statistics** for average calculations
- **Per-rule match counting** to identify hotspots
- **Throughput calculation** (rules processed per second)

---

## 🖥️ Installation & Usage

### **Prerequisites:**
```bash
pip install -r requirements.txt
```

### **Run the GUI Application:**
```bash
python ui.py
```

### **Run CLI Demo:**
```bash
python main.py
```

### **GUI Tabs:**

1. **📊 Processes Tab**
   - View all running system processes
   - Refresh button to update process list
   - Limited to top 100 processes for performance

2. **🌐 Connections Tab**
   - View active network connections
   - Shows both local and remote endpoints
   - Refresh button to update connection list

3. **📜 Rules Tab**
   - View current firewall rules
   - Add new rules dynamically
   - Fields: Rule ID, Type, Value, Action

4. **📝 Logs Tab**
   - View recent firewall action logs
   - **"Apply Rules to All"** button to trigger full evaluation
   - Shows performance report after execution

5. **⚡ Performance Monitor Tab** (Main Feature!)
   - Live CPU and Memory graphs
   - System statistics dashboard
   - Firewall performance metrics
   - All metrics update automatically

---

## 📊 Performance Metrics Explained

### **Why Different from Task Manager?**

| Feature | Task Manager | This Firewall |
|---------|-------------|---------------|
| **Purpose** | Generic system monitoring | Security-focused performance evaluation |
| **Metrics** | Process CPU/Memory only | **Firewall overhead + rule processing stats** |
| **Context** | No security context | **Links performance to specific rules** |
| **Analysis** | What uses resources | **Why and which rules cause overhead** |
| **Optimization** | Not applicable | **Identifies inefficient rules for optimization** |

### **Unique Firewall Metrics:**

1. **Total Rules Matched:** Shows how many times rules have triggered
2. **Rules/Second:** Throughput metric showing rule evaluation capacity
3. **Avg Rule Time:** Latency per rule - helps identify slow rules
4. **Most Active Rule:** Identifies rules that match most frequently
5. **Firewall CPU:** Actual overhead introduced by security monitoring

### **Use Cases:**
- **Rule Optimization:** Identify expensive rules that need optimization
- **Capacity Planning:** Determine maximum rule throughput
- **Performance Analysis:** Measure security vs. performance trade-offs
- **Algorithm Comparison:** Test different rule matching strategies

---

## 🔧 Configuration

### **Adding Custom Rules:**

Edit `rules.json`:
```json
[
  {
    "id": "block_chrome",
    "type": "process_name",
    "value": "chrome.exe",
    "action": "block"
  },
  {
    "id": "block_port_8080",
    "type": "port",
    "value": "8080",
    "action": "block"
  }
]
```

**Rule Types:**
- `process_name`: Match process executable name
- `username`: Match user running the process
- `port`: Match local port number
- `ip`: Match remote IP address

**Actions:**
- `allow`: Permit the connection/process
- `block`: Block the connection/process
- `terminate`: Terminate the process (simulated)

---

## 🛡️ Safety Features

- **DRY_RUN Mode:** All actions are simulated, no real system modifications
- **Read-Only Monitoring:** Process and connection data is only read, never modified
- **Safe Termination:** Actual process termination is disabled by default
- **Access Controls:** Handles permission denied errors gracefully

---

## 📈 Research & Educational Value

This framework demonstrates:
- **Operating System Concepts:** Process management, network monitoring
- **Security Engineering:** Firewall design, rule-based access control
- **Performance Analysis:** Resource consumption, overhead measurement
- **System Programming:** Multi-threading, real-time monitoring
- **GUI Development:** Event-driven programming, data visualization

---

## 🚀 Future Enhancements

Potential improvements:
- **Packet-level inspection** with throughput analysis
- **Machine learning** for anomaly detection
- **Rule cache optimization** with hit rate tracking
- **Network latency measurement** per connection
- **Historical data export** for trend analysis
- **Comparison mode** for different rule matching algorithms
- **Advanced visualizations** (heatmaps, rule dependency graphs)

---

## 📄 License

This project is for educational and research purposes.

---

## 👥 Contributors

Developed as a demonstration of user-level firewall concepts with performance evaluation capabilities.
