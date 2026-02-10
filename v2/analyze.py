import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the Gold Standard Data
FILE_NAME = 'watt_watch_data_v5.csv'
try:
    df = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    print(f"Error: Could not find {FILE_NAME}. Make sure you moved it to this folder!")
    exit()

# Clean: Remove bad rows (charging or errors)
df = df[df['current_ma'] > 0]
df = df[df['gpu_load'] <= 100]

print(f"Loaded {len(df)} rows of telemetry.")
print(df.head())

# 2. Setup the Plotting Grid (3 Rows, 2 Columns)
fig, axes = plt.subplots(3, 2, figsize=(16, 15))
fig.suptitle('WattWatch v2.0: Full System Profiling', fontsize=18)

# Plot A: The Master Timeline
sns.lineplot(ax=axes[0, 0], x=df.index, y='current_ma', data=df, color='red', linewidth=1)
axes[0, 0].set_title('Battery Drain Timeline (The "Heartbeat")')
axes[0, 0].set_ylabel('Current (mA)')
axes[0, 0].set_xlabel('Time (Samples)')

# Plot B: GPU Load vs Power
sns.scatterplot(ax=axes[0, 1], x='gpu_load', y='current_ma', data=df, color='purple', alpha=0.5)
axes[0, 1].set_title('GPU Load vs. Power')
axes[0, 1].set_xlabel('GPU Load (%)')
axes[0, 1].set_ylabel('Current (mA)')

# Plot C: Wi-Fi Speed vs Power
# We filter for rows where Wi-Fi was actually active (> 10KB/s)
wifi_active = df[df['wifi_kbps'] > 10]
sns.scatterplot(ax=axes[1, 0], x='wifi_kbps', y='current_ma', data=wifi_active, color='blue', alpha=0.6)
axes[1, 0].set_title('Wi-Fi Traffic vs. Power')
axes[1, 0].set_xlabel('Wi-Fi Speed (KB/s)')
axes[1, 0].set_ylabel('Current (mA)')

# Plot D: Cellular Speed vs Power
# We filter for rows where Cell was active

cell_active = df[df['cell_kbps'] > 10]
sns.scatterplot(ax=axes[1, 1], x='cell_kbps', y='current_ma', data=cell_active, color='orange', alpha=0.6)
axes[1, 1].set_title('Cellular Traffic vs. Power')
axes[1, 1].set_xlabel('Cell Speed (KB/s)')
axes[1, 1].set_ylabel('Current (mA)')

# Plot E: CPU vs Power (Classic)
sns.scatterplot(ax=axes[2, 0], x='avg_cpu_freq', y='current_ma', data=df, color='green', alpha=0.3)
axes[2, 0].set_title('CPU Frequency vs. Power')
axes[2, 0].set_xlabel('CPU Freq (Hz)')
axes[2, 0].set_ylabel('Current (mA)')

# Plot F: The Correlation Heatmap (The Truth)
# Which variable has the strongest relationship with Battery Drain?
corr_features = ['current_ma', 'brightness', 'avg_cpu_freq', 'gpu_load', 'wifi_kbps', 'cell_kbps']
sns.heatmap(ax=axes[2, 1], data=df[corr_features].corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
axes[2, 1].set_title('Correlation Matrix (Red = Power Hungry)')

plt.tight_layout()
plt.show()