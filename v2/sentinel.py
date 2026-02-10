import time
import pandas as pd
import xgboost as xgb
import os
import sys
import glob

# --- CONFIGURATION ---
MODEL_FILE = "watt_model_v2.json"
CHECK_INTERVAL = 2.0       # Check every 2 seconds
ANOMALY_THRESHOLD = 350.0  # Alert if drain is >350mA higher than expected
SUSPICION_LIMIT = 5        # Alert after 5 consecutive bad checks (10 seconds)

# --- HARDWARE PATHS (Must match your Logger!) ---
BATTERY_CURRENT = "/sys/class/power_supply/battery/current_now"
BRIGHTNESS_PATH = "/sys/class/leds/lcd-backlight/brightness"
GPU_PATH = "/sys/kernel/ged/hal/gpu_sum_loading"
WIFI_IFACE = "wlan0"
CELL_IFACE = "ccmni1"  # Your Cellular Interface

# --- DATA GATHERING FUNCTIONS ---
cpu_paths = glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq")
cpu_paths.sort()

def read_val(path):
    try:
        with open(path, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def get_gpu_busy_counter():
    try:
        with open(GPU_PATH, 'r') as f:
            data = f.read().strip().split()
            return int(data[1])
    except:
        return 0

def get_iface_bytes(iface_name):
    rx = f"/sys/class/net/{iface_name}/statistics/rx_bytes"
    tx = f"/sys/class/net/{iface_name}/statistics/tx_bytes"
    if os.path.exists(rx):
        return read_val(rx) + read_val(tx)
    return 0

def get_cpu_avg():
    total = 0
    count = 0
    for p in cpu_paths:
        val = read_val(p)
        if val > 0:
            total += val
            count += 1
    return int(total / count) if count > 0 else 0

def send_alert(actual, predicted, diff):
    """Triggers a System Notification via Termux API (if available) or standard print"""
    msg = f"⚠️ ANOMALY! Drain: {actual}mA | Expected: {predicted:.0f}mA | Diff: +{diff:.0f}mA"
    
    # 1. Print to Terminal (Red Text)
    print(f"\033[91m{msg}\033[0m") 
    
    # 2. Try Termux Vibration (Needs Termux:API app installed, optional)
    os.system("termux-vibrate -d 500 -f > /dev/null 2>&1")
    
    # 3. Try System Notification
    os.system(f"termux-notification --title 'WattWatch Security' --content '{msg}' > /dev/null 2>&1")

# --- MAIN SECURITY LOOP ---
def main():
    print(f"[*] Loading Brain: {MODEL_FILE}...")
    try:
        model = xgb.XGBRegressor()
        model.load_model(MODEL_FILE)
    except Exception as e:
        print(f"[!] Error loading model: {e}")
        sys.exit(1)

    print(f"[*] Sentinel Active. Threshold: +{ANOMALY_THRESHOLD}mA")
    print(f"[*] Press CTRL+C to stop.")

    # Init Counters
    prev_gpu_busy = get_gpu_busy_counter()
    prev_wifi = get_iface_bytes(WIFI_IFACE)
    prev_cell = get_iface_bytes(CELL_IFACE)
    prev_time = time.time()
    
    suspicion_counter = 0

    while True:
        try:
            time.sleep(CHECK_INTERVAL)

            # 1. Calculate Deltas
            curr_time = time.time()
            time_delta = curr_time - prev_time
            if time_delta <= 0: time_delta = 1.0

            curr_gpu = get_gpu_busy_counter()
            gpu_load = (((curr_gpu - prev_gpu) / 1e9) / time_delta) * 100
            gpu_load = max(0, min(100, gpu_load))

            curr_wifi = get_iface_bytes(WIFI_IFACE)
            wifi_kbps = ((curr_wifi - prev_wifi) / 1024.0) / time_delta
            
            curr_cell = get_iface_bytes(CELL_IFACE)
            cell_kbps = ((curr_cell - prev_cell) / 1024.0) / time_delta

            # 2. Get Absolute States
            current_ma = read_val(BATTERY_CURRENT)
            current_ma = current_ma // 1000 if current_ma > 10000 else current_ma
            bright = read_val(BRIGHTNESS_PATH)
            cpu_freq = get_cpu_avg()

            # 3. ASK THE AI: "Is this normal?"
            # We must provide features in the EXACT order of training
            features = pd.DataFrame([[bright, cpu_freq, gpu_load, wifi_kbps, cell_kbps]], 
                                    columns=['brightness', 'avg_cpu_freq', 'gpu_load', 'wifi_kbps', 'cell_kbps'])
            
            predicted_ma = model.predict(features)[0]
            
            # 4. The Judgment
            diff = current_ma - predicted_ma
            
            # Status Bar
            status = f"Act: {current_ma}mA | Exp: {predicted_ma:.0f}mA | Diff: {diff:+.0f}mA | Suspicion: {suspicion_counter}/5"
            
            if diff > ANOMALY_THRESHOLD:
                suspicion_counter += 1
                print(f"\033[93m{status}\033[0m") # Yellow warning
            else:
                suspicion_counter = 0 # Reset if normal
                print(f"\033[92m{status}\033[0m", end='\r') # Green normal

            # 5. TRIGGER ALERT
            if suspicion_counter >= SUSPICION_LIMIT:
                send_alert(current_ma, predicted_ma, diff)
                # Don't reset counter immediately so it keeps alerting if persistent

            # Update Pointers
            prev_gpu_busy = curr_gpu
            prev_wifi = curr_wifi
            prev_cell = curr_cell
            prev_time = curr_time

        except KeyboardInterrupt:
            print("\nSentinel deactivated.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()