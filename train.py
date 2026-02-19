import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import m2cgen as m2c 

# 1. Load the Gold Standard Dataset
df = pd.read_csv('watt_watch_data_v5.csv')

# Filter out bad reads (charging or errors)
df = df[df['current_ma'] > 0]
df = df[df['gpu_load'] <= 100] # Safety filter

print(f"Loaded {len(df)} rows of training data.")

# 2. Define Features (The Inputs)
# Now we have 5 inputs instead of 2!
features = ['brightness', 'avg_cpu_freq', 'gpu_load', 'wifi_kbps', 'cell_kbps']
target = 'current_ma'

X = df[features]
y = df[target]

# 3. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Upgrade (XGBoost)
print("Training WattWatch v2.0...")
model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6)
model.fit(X_train, y_train)

# 5. Evaluate
preds = model.predict(X_test)
r2 = r2_score(y_test, preds)
mae = mean_absolute_error(y_test, preds)

print(f"\n--- 🏆 MODEL SCORECARD ---")
print(f"Previous Accuracy (v1): ~0.69")
print(f"New Accuracy (v2):      {r2:.3f}")
print(f"Average Error:          {mae:.0f} mA")

if r2 > 0.85:
    print("Result: EXCELLENT. The AI now deeply understands your battery.")
elif r2 > 0.75:
    print("Result: GOOD. Much better than before.")
else:
    print("Result: OKAY. Data might be noisy.")

# 6. Feature Importance (The "Power Hunger" Graph)
# This tells us WHICH component drains the most battery
plt.figure(figsize=(10, 5))
xgb.plot_importance(model, importance_type='weight', title='What Kills Your Battery?', show_values=False)
plt.tight_layout()
plt.show()

# 7. Visualization: Prediction vs Reality
plt.figure(figsize=(12, 6))
plt.plot(y_test.values[:150], label='Real Battery Drain', color='black', alpha=0.6)
plt.plot(preds[:150], label='AI Prediction', color='#00ff00', linestyle='--', linewidth=2)
plt.title(f"WattWatch v2.0 (Accuracy: {r2:.2f})")
plt.xlabel("Time Samples")
plt.ylabel("Current (mA)")
plt.legend()
plt.show()

# Save the new brain
model.save_model("watt_model_v2.json")

# --- NEW: TRANSPILE TO PURE PYTHON ---
print("\n[*] Translating AI into pure Python code (brain.py)...")
code = m2c.export_to_python(model)

with open("brain.py", "w") as f:
    f.write(code)

print("[+] Success! The brain.py file is ready for Termux.")