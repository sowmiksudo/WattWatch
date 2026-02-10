import os
import time
import csv
import glob
import sys

# --- CONFIGURATION ---
LOG_FILE = "watt_watch_data_v5.csv"
INTERVAL = 1.0 

# --- PATHS ---
BATTERY_CURRENT = "/sys/class/power_supply/battery/current_now"
BRIGHTNESS_PATH = "/sys/class/leds/lcd-backlight/brightness"
GPU_PATH = "/sys/kernel/ged/hal/gpu_sum_loading"

# --- NETWORK CONFIG ---
# We track them separately for better ML accuracy
WIFI_IFACE = "wlan0"
CELL_IFACE = "ccmni1"  # UPDATED: The one you found!

# Find CPU cores
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
    """Returns RX + TX bytes for a specific interface"""
    rx_path = f"/sys/class/net/{iface_name}/statistics/rx_bytes"
    tx_path = f"/sys/class/net/{iface_name}/statistics/tx_bytes"
    if os.path.exists(rx_path):
        return read_val(rx_path) + read_val(tx_path)
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

def main():
    print(f"[*] Starting WattWatch v5.0 (Dual-Radio)...")
    print(f"[*] GPU: {GPU_PATH}")
    print(f"[*] WiFi: {WIFI_IFACE} | Cell: {CELL_IFACE}")
    print(f"[*] Logging to {LOG_FILE}...\n")

    # NEW HEADERS: Separate WiFi and Cell columns
    headers = ["timestamp", "current_ma", "brightness", "avg_cpu_freq", "gpu_load", "wifi_kbps", "cell_kbps"]
    file_exists = os.path.isfile(LOG_FILE)
    
    # Init Counters
    prev_gpu_busy = get_gpu_busy_counter()
    prev_wifi_bytes = get_iface_bytes(WIFI_IFACE)
    prev_cell_bytes = get_iface_bytes(CELL_IFACE)
    prev_time = time.time()

    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)

        try:
            while True:
                time.sleep(INTERVAL)
                
                # 1. Time Delta
                curr_time = time.time()
                time_delta = curr_time - prev_time
                if time_delta <= 0: time_delta = 1.0
                
                # 2. GPU Load
                curr_gpu_busy = get_gpu_busy_counter()
                busy_seconds = (curr_gpu_busy - prev_gpu_busy) / 1_000_000_000.0
                gpu_load = (busy_seconds / time_delta) * 100
                if gpu_load > 100: gpu_load = 100.0
                if gpu_load < 0: gpu_load = 0.0

                # 3. WiFi Speed
                curr_wifi_bytes = get_iface_bytes(WIFI_IFACE)
                delta_wifi = curr_wifi_bytes - prev_wifi_bytes
                wifi_kbps = (delta_wifi / 1024.0) / time_delta
                if wifi_kbps < 0: wifi_kbps = 0

                # 4. Cellular Speed
                curr_cell_bytes = get_iface_bytes(CELL_IFACE)
                delta_cell = curr_cell_bytes - prev_cell_bytes
                cell_kbps = (delta_cell / 1024.0) / time_delta
                if cell_kbps < 0: cell_kbps = 0

                # 5. Standard Metrics
                raw_current = read_val(BATTERY_CURRENT)
                current_ma = raw_current // 1000 if raw_current > 10000 else raw_current
                bright = read_val(BRIGHTNESS_PATH)
                cpu_freq = get_cpu_avg()

                # 6. Log & Save
                writer.writerow([int(curr_time), current_ma, bright, cpu_freq, round(gpu_load, 1), int(wifi_kbps), int(cell_kbps)])
                f.flush()
                
                # Update Pointers
                prev_gpu_busy = curr_gpu_busy
                prev_wifi_bytes = curr_wifi_bytes
                prev_cell_bytes = curr_cell_bytes
                prev_time = curr_time

                print(f"GPU:{gpu_load:4.1f}% | Wifi:{int(wifi_kbps):4}K | Cell:{int(cell_kbps):4}K | I:{current_ma}mA  ", end='\r')
                
        except KeyboardInterrupt:
            print("\n[!] Stopped.")

if __name__ == "__main__":
    main()