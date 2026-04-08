"""
Tecovolt — gen synth de demanda energética
=====================================================
Basado en readings reales del ACS712-30A sesión 20260408 en picoscope:
  baja:  rawRMS = 0.00   (sin carga)
  alta:  rawRMS = 170.0  (dos calentadores ~1900W)
  media: rawRMS = 85.0   (estimado — un calentador, reemplazar con real)

El modelo recibe una ventana de N lecturas de rawRMS a 0.5Hz
(el thread Zephyr actualiza cada ~600ms).

Clases → thresholds reales del sketch:
  baja  : rawRMS < 3.0
  media : 3.0 ≤ rawRMS < 120
  alta  : rawRMS ≥ 120

Uso:
    python tecovolt_demand_synth.py
    python tecovolt_demand_synth.py --n 300 --output ./demand_dataset/
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# ── Parámetros medidos reales (sesión 20260408) ──────────────────────────────
# Thread Zephyr: k_usleep(100) × 1000 samples + k_msleep(500) ≈ 1 lectura/600ms
SAMPLE_RATE_HZ  = 1.67      # Hz — una lectura cada ~600ms
WINDOW_SAMPLES  = 10        # 10 lecturas por ventana (~6 segundos)
N_PER_CLASS     = 200       # ventanas por clase

# Perfiles de rawRMS medidos realmente en el hack
PROFILES = {
    "baja": {
        "rawRMS_center": 0.0,
        "rawRMS_noise":  0.8,    # ruido del ADC en reposo
        "desc": "Sin carga — rawRMS < 3.0 (threshold del sketch)"
    },
    "media": {
        "rawRMS_center": 85.0,   # estimado — UN calentador (~950W)
        "rawRMS_noise":  4.0,    # variación típica de carga resistiva
        "desc": "Carga media — un calentador ~950W (REEMPLAZAR con captura real)"
    },
    "alta": {
        "rawRMS_center": 169.5,  # medido real: mean de [170.09,170.38,170.20,168.36,170.41,167.73,169.56]
        "rawRMS_noise":  1.2,    # std real medido
        "desc": "Carga alta — dos calentadores ~1900W"
    },
}


def generate_window(profile: dict, rng: np.random.Generator) -> np.ndarray:
    """Genera una ventana de WINDOW_SAMPLES lecturas de rawRMS."""
    center = profile["rawRMS_center"]
    noise  = profile["rawRMS_noise"]
    
    # Drift lento dentro de la ventana (la carga no es perfectamente estable)
    drift = rng.uniform(-noise * 0.5, noise * 0.5)
    samples = rng.normal(center + drift, noise, WINDOW_SAMPLES)
    
    # Clip físico: rawRMS no puede ser negativo
    samples = np.clip(samples, 0, 4095)
    
    return samples.astype(np.float32)


def main():
    parser = argparse.ArgumentParser(description="Tecovolt — demand synth")
    parser.add_argument("--n",      type=int, default=N_PER_CLASS,
                        help=f"Ventanas por clase (default: {N_PER_CLASS})")
    parser.add_argument("--output", default="./demand_dataset",
                        help="Carpeta de salida")
    parser.add_argument("--seed",   type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    all_rows = []

    print(f"Generando {args.n} ventanas × 3 clases = {args.n * 3} total\n")

    for label, profile in PROFILES.items():
        print(f"  [{label}] {profile['desc']}")
        rows = []

        for _ in range(args.n):
            window = generate_window(profile, rng)
            row = {"label": label}
            row.update({f"r{i}": round(float(window[i]), 4) for i in range(WINDOW_SAMPLES)})
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(out_dir / f"demand_{label}.csv", index=False)

        mean = df[[f"r{i}" for i in range(WINDOW_SAMPLES)]].values.mean()
        std  = df[[f"r{i}" for i in range(WINDOW_SAMPLES)]].values.std()
        print(f"         rawRMS: {mean:.1f} ± {std:.1f}")
        all_rows.extend(rows)

    # Dataset combinado shuffleado
    df_all = pd.DataFrame(all_rows).sample(frac=1, random_state=42).reset_index(drop=True)

    # Split 80/20 train/test
    split = int(len(df_all) * 0.8)
    train = df_all.iloc[:split]
    test  = df_all.iloc[split:]

    train.to_csv(out_dir / "demand_train.csv", index=False)
    test.to_csv(out_dir  / "demand_test.csv",  index=False)

    print(f"\n✓ {len(df_all)} ventanas totales")
    print(f"  demand_train.csv → {len(train)} filas")
    print(f"  demand_test.csv  → {len(test)} filas")
    print(f"\nDistribución (train):")
    print(train["label"].value_counts().to_string())
    print(f"\n⚠️  NOTA: clase 'media' usa rawRMS estimado (85.0)")
    print(f"   Reemplazar con captura real de un calentador cuando esté disponible.")
    print(f"\nPara Edge Impulse:")
    print(f"  1. Data acquisition → Upload → CSV → demand_train.csv")
    print(f"  2. Impulse: Input (10 features) → Flatten → Classification (3 clases)")
    print(f"  3. Features: r0..r9 (rawRMS por ventana)")


if __name__ == "__main__":
    main()