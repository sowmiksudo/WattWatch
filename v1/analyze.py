import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the Data
df = pd.read_csv('watt_watch_data.csv')

# Clean: Remove any rows where current is 0 or negative (charging/errors)
df = df[df['current_ma'] > 0]

print(f"Loaded {len(df)} rows of data.")
print(df.head())

# 2. Setup the Plotting Grid
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('WattWatch: Hardware Power Analysis', fontsize=16)

# Plot A: The Timeline (What happened during the experiment?)
sns.lineplot(ax=axes[0, 0], x=df.index, y='current_ma', data=df, color='red')
axes[0, 0].set_title('Battery Drain over Time')
axes[0, 0].set_ylabel('Current (mA)')
axes[0, 0].set_xlabel('Time (Seconds)')

# Plot B: Brightness vs Power (The Screen Cost)
sns.scatterplot(ax=axes[0, 1], x='brightness', y='current_ma', data=df, alpha=0.5)
axes[0, 1].set_title('Screen Brightness vs. Power')
axes[0, 1].set_ylabel('Current (mA)')

# Plot C: CPU Freq vs Power (The Silicon Cost)
sns.scatterplot(ax=axes[1, 0], x='avg_cpu_freq', y='current_ma', data=df, color='green', alpha=0.5)
axes[1, 0].set_title('CPU Speed vs. Power')
axes[1, 0].set_ylabel('Current (mA)')

# Plot D: The Correlation Matrix (The "Heatmap" of Truth)
sns.heatmap(ax=axes[1, 1], data=df[['current_ma', 'brightness', 'avg_cpu_freq']].corr(), annot=True, cmap='coolwarm')
axes[1, 1].set_title('Correlation Matrix')

plt.tight_layout()
plt.show()