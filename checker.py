import time
import os
import sys
import glob

# Import our pure-math translated model!
try:
    from brain import score
except ImportError:
    print("[!] Error: Could not find brain.py. Make sure you transferred it!")
    sys.exit(1)

# --- CONFIGURATION ---
CHECK_INTERVAL = 1.0       
ANOMALY_THRESHOLD = 350.0  

# --- HARDWARE PATHS ---
BATTERY_CURRENT = "/sys/class/power_supply/battery/current_now"
BRIGHTNESS_PATH = "/sys/class/leds/lcd-backlight/brightness"
GPU_PATH = "/sys/kernel/ged/hal/gpu_sum_loading"
WIFI_IFACE = "wlan0"
CELL_IFACE = "ccmni1"

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
            return int(f.read().strip().split()[1])
    except:
        return 0

def get_iface_bytes(iface_name):
    rx = f"/sys/class/net/{iface_name}/statistics/rx_bytes"
    tx = f"/sys/class/net/{iface_name}/statistics/tx_bytes"
    if os.path.exists(rx): return read_val(rx) + read_val(tx)
    return 0

def get_cpu_avg():
    total, count = 0, 0
    for p in cpu_paths:
        val = read_val(p)
        if val > 0:
            total += val
            count += 1
    return int(total / count) if count > 0 else 0

def main():
    print("[*] Loading Pure-Python Brain...")
    print(f"[*] Sentinel Active. Threshold: +{ANOMALY_THRESHOLD}mA")
    
    prev_gpu = get_gpu_busy_counter()
    prev_wifi = get_iface_bytes(WIFI_IFACE)
    prev_cell = get_iface_bytes(CELL_IFACE)
    prev_time = time.time()

    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            curr_time = time.time()
            time_delta = max(curr_time - prev_time, 1.0)

            # Calculate metrics
            curr_gpu = get_gpu_busy_counter()
            gpu_load = max(0, min(100, (((curr_gpu - prev_gpu) / 1e9) / time_delta) * 100))

            curr_wifi = get_iface_bytes(WIFI_IFACE)
            wifi_kbps = ((curr_wifi - prev_wifi) / 1024.0) / time_delta
            
            curr_cell = get_iface_bytes(CELL_IFACE)
            cell_kbps = ((curr_cell - prev_cell) / 1024.0) / time_delta

            current_ma = read_val(BATTERY_CURRENT)
            current_ma = current_ma // 1000 if current_ma > 10000 else current_ma
            bright = read_val(BRIGHTNESS_PATH)
            cpu_freq = get_cpu_avg()

            # ASK THE AI (Using the raw math function)
            features = [bright, cpu_freq, gpu_load, wifi_kbps, cell_kbps]
            predicted_ma = score(features)
            
            # The Judgment
            diff = current_ma - predicted_ma
            status = f"Act: {current_ma}mA | Exp: {predicted_ma:.0f}mA | Diff: {diff:+.0f}mA"
            
            if diff > ANOMALY_THRESHOLD:
                print(f"\a\n\033[91m⚠️ [SECURITY ALERT] {status} ⚠️\033[0m")
            else:
                print(f"\033[92m{status} (Normal)\033[0m          ", end='\r')

            # Update pointers
            prev_gpu, prev_wifi, prev_cell, prev_time = curr_gpu, curr_wifi, curr_cell, curr_time

        except KeyboardInterrupt:
            print("\nDeactivated.")
            break

if __name__ == "__main__":
    main()