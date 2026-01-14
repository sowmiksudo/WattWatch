# ⚡ WattWatch
**Kernel-Level Power Profiling & Anomaly Detection for Android**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Android%20(Rooted)-green) ![ML](https://img.shields.io/badge/Model-XGBoost-orange)

**WattWatch** is a research project and security tool that uses Machine Learning to detect "invisible" battery drain on Android devices. Unlike standard battery monitors that rely on system averages, WattWatch bridges the kernel-to-user-space gap by harvesting raw telemetry directly from `/sys/class` interfaces.

By training an **XGBoost Regressor** on a custom dataset of hardware states (CPU frequency, screen brightness), the system identifies processes that consume disproportionate power—effectively flagging hidden crypto-miners or malware that attempt to evade traditional detection.

---

## 🚀 The Concept
Standard Android battery stats tell you *which* app is using battery, but they don't tell you *if the usage makes sense*.

**WattWatch changes the approach:**
1.  **Listen to the Kernel:** It reads raw hardware files (`/sys/class/...`) to log real-time voltage, current, brightness, and CPU frequency.
2.  **Train the Brain:** An **XGBoost** regression model learns the device's "Power Fingerprint" (e.g., *100% Brightness + 2GHz CPU should equal ~900mA*).
3.  **Detect Anomalies:** If the battery drains at 900mA but the screen is dim and CPU is reported as "low," the model flags a high **Residual Score** (Suspicious Activity).

---

## 🛠 Architecture
* **Data Acquisition:** Python script (`watt_logger.py`) running in Termux (Root) harvesting data from Linux kernel interfaces.
* **Preprocessing:** Cleaning and synchronizing timestamps for CPU cores and display drivers.
* **Model:** XGBoost Regressor (Gradient Boosting) for non-linear power prediction.
* **Verification:** Simulated "Crypto-Miner" scenario successfully flagged with >95% confidence.

---

## 📊 Results & Analysis (Prototype v1)

**1. Hardware Power Analysis**
*The correlation between Screen Brightness (Top Right), CPU Frequency (Bottom Left), and Battery Drain.*
![Hardware Analysis](images/figure_1.png)

**2. Model Performance (Actual vs. Predicted)**
*The XGBoost model (Red) successfully predicting the battery drain trends against the real Multimeter data (Blue).*
![Model Training](images/figure_2.png)

* **Data Collected:** ~1,000 datapoints across Idle, Video, and Gaming states.
* **Model Accuracy:** $R^2$ Score of **0.69** (Base model using only CPU & Brightness).
* **Anomaly Detection:** Successfully distinguished between legitimate high-drain (Gaming) and suspicious high-drain (Simulated hidden process).

---

## 📂 Project Structure

```text
/
├── watt_logger.py       # The 'Sensor': Runs on phone (Root) to log kernel metrics
├── watt_watch_data.csv  # The 'Dataset': Raw telemetry (Time, Current, Brightness, Freq)
├── train_model.py       # The 'Brain': Trains the XGBoost model & saves it
├── test_detector.py     # The 'Guard': Loads model & runs anomaly detection scenarios
├── images/              # Graph visualizations
│   ├── figure_1.png
│   └── figure_2.png
└── README.md

```

---

## 🔧 Prerequisites

* **Android Device:** Rooted (Magisk/KernelSU) to access `/sys/class` files.
* **Termux:** For on-device logging.
* **Python Libraries:**
```bash
pip install pandas xgboost scikit-learn matplotlib seaborn

```



---

## 🚦 Usage

### 1. Data Collection (On Phone)

Run the logger via SSH or directly in Termux. Ensure you grant Root permissions.

```bash
su
python watt_logger.py

```

*Perform various tasks (Idle, Gaming, Max Brightness) for ~15 minutes to generate `watt_watch_data.csv`.*

### 2. Training (On PC)

Transfer the CSV to your PC and run the training script.

```bash
python train_model.py

```

*This generates `watt_model.json` and the performance graphs.*

### 3. Anomaly Detection Simulation

Test the model against fake malware data.

```bash
python test_detector.py

```

---

## 🔮 Roadmap (v2.0)

* [ ] **GPU Profiling:** Add `/sys/class/kgsl/gpus` telemetry to improve model accuracy beyond 0.70.
* [ ] **Network States:** Integrate Wi-Fi/Cellular radio power states.
* [ ] **Real-Time App:** Port the inference engine back to Android for live alerting.

---

## 📄 License

This project is open-source and available under the MIT License.
