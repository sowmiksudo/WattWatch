# ⚡ WattWatch
**Kernel-Level Power Profiling & Anomaly Detection for Android**

WattWatch is a research project that uses Machine Learning to detect "invisible" battery drain. By training a model on the physical relationship between hardware states (Screen, CPU) and electrical current (mA), WattWatch can flag when a device is consuming more power than its active hardware justifies—a signature of hidden background processes like crypto-miners or malware.

## 🚀 The Concept
Standard Android battery stats tell you *which* app is using battery, but they don't tell you *if the usage makes sense*.

**WattWatch changes the approach:**
1.  **Listen to the Kernel:** It reads raw hardware files (`/sys/class/...`) to log real-time voltage, current, brightness, and CPU frequency.
2.  **Train the Brain:** An **XGBoost** regression model learns the device's "Power Fingerprint" (e.g., *100% Brightness + 2GHz CPU should equal ~900mA*).
3.  **Detect Anomalies:** If the battery drains at 900mA but the screen is dim and CPU is reported as "low," the model flags a high **Residual Score** (Suspicious Activity). 

## 📈 Analysis & Visualizations

**Figure 1: Hardware Power Analysis**
*The correlation between Screen Brightness (Top Right), CPU Frequency (Bottom Left), and Battery Drain.*
![Hardware Analysis](images/figure_1.png)

**Figure 2: Model Performance (Actual vs. Predicted)**
*The XGBoost model (Red) successfully predicting the battery drain trends against the real Multimeter data (Blue).*
![Model Training](images/figure_2.png)

## 🛠 Architecture
* **Data Acquisition:** Python script running in Termux (Root) harvesting data from Linux kernel interfaces.
* **Preprocessing:** Cleaning and synchronizing timestamps for CPU cores and display drivers.
* **Model:** XGBoost Regressor (Gradient Boosting) for non-linear power prediction.
* **Verification:** Simulated "Crypto-Miner" scenario successfully flagged with >95% confidence.

## 📂 Project Structure
```text
/
├── watt_logger.py       # The 'Sensor': Runs on phone (Root) to log kernel metrics
├── watt_watch_data.csv  # The 'Dataset': Raw telemetry (Time, Current, Brightness, Freq)
├── train_model.py       # The 'Brain': Trains the XGBoost model & saves it
├── test_detector.py     # The 'Guard': Loads model & runs anomaly detection scenarios
└── README.md