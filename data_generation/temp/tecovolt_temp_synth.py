import numpy as np
import pandas as pd

np.random.seed(42)

# Config
SAMPLE_RATE_HZ = 1       # BMP280 a 1 Hz
WINDOW_SAMPLES = 10      # 10 segundos por ventana
SAMPLES_PER_CLASS = 150  # 150 ventanas por clase → 450 total

def generate_window(temp_range, hum_range, noise_temp=0.8, noise_hum=2.0):
    """Genera una ventana de 10 muestras con variación fair. """
    base_temp = np.random.uniform(*temp_range)
    base_hum  = np.random.uniform(*hum_range)
    
    temps = base_temp + np.random.normal(0, noise_temp, WINDOW_SAMPLES)
    hums  = base_hum  + np.random.normal(0, noise_hum,  WINDOW_SAMPLES)
    
    # Clip a rangos físicamente posibles
    temps = np.clip(temps, 10, 100)
    hums  = np.clip(hums,  0,  100)
    return temps, hums

# Rangos
# bajo  → operación normal del tablero
# medio → sobrecarga incipiente, mandar alerta
# alto  → riesgo de falla, actuar relay

classes = {
    "bajo":  {"temp": (20, 45), "hum": (30, 60)},
    "medio": {"temp": (45, 65), "hum": (60, 75)},
    "alto":  {"temp": (65, 90), "hum": (10, 25)},  # seco+caliente = peor caso
}

rows = []

for label, params in classes.items():
    for _ in range(SAMPLES_PER_CLASS):
        temps, hums = generate_window(params["temp"], params["hum"])
        
        # Edge Impulse CSV format:
        # timestamp(ms), feat1, feat2, ... featN, label
        timestamp = 0  # EI lo ignora cuando usas el uploader CSV
        row = [timestamp] + list(temps) + list(hums) + [label]
        rows.append(row)

# cols: timestamp + temp_0..9 + hum_0..9 + label
temp_cols = [f"temp_{i}" for i in range(WINDOW_SAMPLES)]
hum_cols  = [f"hum_{i}"  for i in range(WINDOW_SAMPLES)]
columns   = ["timestamp"] + temp_cols + hum_cols + ["label"]

df = pd.DataFrame(rows, columns=columns)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

# Split 80/20 train/test
split = int(len(df) * 0.8)
train = df.iloc[:split]
test  = df.iloc[split:]

train.to_csv("/home/claude/tecovolt_thermal_train.csv", index=False)
test.to_csv("/home/claude/tecovolt_thermal_test.csv",  index=False)

print(f"Agenerados:")
print(f"   tecovolt_thermal_train.csv → {len(train)} ventanas")
print(f"   tecovolt_thermal_test.csv  → {len(test)}  ventanas")
print(f"\nDistribución por clase (train):")
print(train["label"].value_counts())
print(f"\nEjemplo de fila (alto):")
print(train[train["label"] == "alto"].iloc[0].to_dict())