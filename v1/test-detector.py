import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt

model = xgb.XGBRegressor()
model.load_model("watt_model.json")

data = {
    'scenario': ['Normal Browsing', 'Gaming', 'Hidden Crypto Miner'],
    'brightness': [1200, 2550, 100],          # Miner hides with screen dim
    'avg_cpu_freq': [1400000, 2100000, 800000], # Miner tries to be subtle (or uses GPU)
    'actual_current_ma': [450, 1100, 900]     # BUT the battery doesn't lie!
}

df_test = pd.DataFrame(data)

features = df_test[['brightness', 'avg_cpu_freq']]
df_test['predicted_ma'] = model.predict(features)

df_test['suspicion_score'] = df_test['actual_current_ma'] - df_test['predicted_ma']

print("\n--- 🕵️ WATT-WATCH SECURITY REPORT ---")
print(df_test[['scenario', 'actual_current_ma', 'predicted_ma', 'suspicion_score']])

THRESHOLD = 200

print("\n[ ALERTS ]")
for index, row in df_test.iterrows():
    if row['suspicion_score'] > THRESHOLD:
        print(f"🚨 ALERT! {row['scenario']} is draining {row['suspicion_score']:.0f}mA more than expected!")
    else:
        print(f"✅ {row['scenario']} looks normal.")