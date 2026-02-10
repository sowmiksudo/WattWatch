import os
import time
import csv
import glob
import sys

# --- CONFIGURATION ---
LOG_FILE = "watt_watch_data.csv"
INTERVAL = 1.0  # Seconds between logs

# --- PATH FINDER ---
BATTERY_CURRENT = "/sys/class/power_supply/battery/current_now"

# UPDATED: We hardcoded this based on your check earlier
BRIGHTNESS_PATH = "/sys/class/leds/lcd-backlight/brightness"

# Find all CPU cores
cpu_paths = glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq")
cpu_paths.sort()

def read_val(path):
    try:
        with open(path, 'r') as f:
            return int(f.read().strip())
    except:
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
    print(f"[*] Starting WattWatch Logger...")
    print(f"[*] Battery Path: {BATTERY_CURRENT}")
    print(f"[*] Brightness Path: {BRIGHTNESS_PATH}")
    print(f"[*] Found {len(cpu_paths)} CPU cores.")
    print(f"[*] Logging to {LOG_FILE}. Press CTRL+C to stop.\n")

    # Initialize CSV with headers
    headers = ["timestamp", "current_ma", "brightness", "avg_cpu_freq"]
    
    # Check if file exists so we don't overwrite headers
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)

        try:
            while True:
                ts = int(time.time())
                
                # 1. Get Current
                raw_current = read_val(BATTERY_CURRENT)
                # Convert microamps to milliamps if necessary
                current_ma = raw_current // 1000 if raw_current > 10000 else raw_current
                
                # 2. Get Features
                bright = read_val(BRIGHTNESS_PATH)
                cpu_freq = get_cpu_avg()

                # 3. Log
                writer.writerow([ts, current_ma, bright, cpu_freq])
                f.flush()

                # Print status
                print(f"Time: {ts} | Current: {current_ma}mA | Bright: {bright} | CPU: {cpu_freq}Hz   ", end='\r')
                time.sleep(INTERVAL)
                
        except KeyboardInterrupt:
            print("\n[!] Logging stopped. Data saved.")

if __name__ == "__main__":
    main()