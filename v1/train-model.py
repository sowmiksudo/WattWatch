import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import pickle

# 1. Load Data
df = pd.read_csv('watt_watch_data.csv')
df = df[df['current_ma'] > 0] # Filter bad reads

# 2. Prepare Features (X) and Target (y)
# We want to predict 'current_ma' using 'brightness' and 'avg_cpu_freq'
X = df[['brightness', 'avg_cpu_freq']]
y = df['current_ma']

# 3. Split: 80% for Training, 20% for Testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Model (XGBoost)
print("Training the brain...")
model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5)
model.fit(X_train, y_train)

# 5. Evaluate
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"\n--- Model Report Card ---")
print(f"Mean Absolute Error: {mae:.2f} mA")
print(f"Accuracy Score (R2): {r2:.2f} (1.0 is perfect)")
print(f"interpretation: On average, the model is 'off' by only {mae:.0f} mA.")

# 6. Visualize: Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.plot(y_test.values[:100], label='Actual (Multimeter)', color='blue', alpha=0.7)
plt.plot(predictions[:100], label='AI Prediction', color='red', linestyle='--', alpha=0.9)
plt.title("WattWatch AI: Did it learn the pattern?")
plt.xlabel("Time (Samples)")
plt.ylabel("Current (mA)")
plt.legend()
plt.show()

# 7. Save the model for later
model.save_model("watt_model.json")
print("\nModel saved as 'watt_model.json'. Ready for the anomaly detector!")