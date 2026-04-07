"""
Tecovolt — Generador sintético de datos de entrenamiento
=========================================================
Genera señales sintéticas de 6 clases basadas en el perfil de ruido
real medido con PicoScope 2208B MSO en la red eléctrica de Puebla, MX.

Parámetros reales medidos (sesión 20260407-0003):
  - Sample rate:   6,280 Hz
  - Samples/wf:   1,259
  - RMS normal:   ~117 mV (escala ZMPT101B, ratio ~9x)
  - Noise floor:   ~0.86 mV std (diff-to-diff)
  - Freq nominal:  60 Hz

Uso:
    python tecovolt_synth.py
    python tecovolt_synth.py --n 100 --output ./mi_dataset/
    python tecovolt_synth.py --n 50 --classes normal sag_leve swell
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# ─── Parámetros del instrumento (medidos reales) ────────────────────────────
FS          = 6280       # Hz — sample rate real del PicoScope
N_SAMPLES   = 1259       # muestras por waveform
NOISE_STD   = 0.00086    # V — ruido medido (std de diff)
NOISE_P95   = 0.00172    # V — percentil 95 del ruido

# Parámetros de la señal (escala ZMPT101B, no voltaje real de red)
# Red real 127V RMS → ZMPT → ~14V pk-pk → Arduino ADC ~1.5V pk-pk
# Pero capturamos directamente con PicoScope: 1.5V AWG → ZMPT → ~0.166V pk-pk
V_NORMAL_AMP = 0.166     # V — amplitud pico de señal normal (~117mV RMS)
FREQ_NOMINAL = 60.0      # Hz

# ─── Definición de fenómenos ────────────────────────────────────────────────
PHENOMENA = {
    "normal": {
        "desc": "Red estable, 60Hz, sin anomalías",
        "amp_range":   (0.95, 1.05),   # variación de amplitud ±5%
        "freq_range":  (59.7, 60.3),   # variación de frecuencia ±0.3Hz
        "noise_mult":  (0.8, 1.2),     # multiplicador del noise floor
        "sag_depth":   None,
        "swell_boost": None,
        "flicker":     False,
        "outage":      False,
    },
    "sag_leve": {
        "desc": "Voltage sag leve: caída sostenida 10-25% del nominal",
        # RMS cae a 75-90% del nominal
        "amp_range":   (0.75, 0.90),
        "freq_range":  (59.5, 60.5),
        "noise_mult":  (1.0, 1.5),     # más ruido durante el sag
        "sag_depth":   None,
        "swell_boost": None,
        "flicker":     False,
        "outage":      False,
    },
    "sag_severo": {
        "desc": "Voltage sag severo: caída >25% del nominal",
        # RMS cae a 40-74% del nominal
        "amp_range":   (0.40, 0.74),
        "freq_range":  (59.0, 61.0),
        "noise_mult":  (1.5, 2.5),
        "sag_depth":   None,
        "swell_boost": None,
        "flicker":     False,
        "outage":      False,
    },
    "swell": {
        "desc": "Voltage swell: sobretensión sostenida >10% del nominal",
        # RMS sube a 110-140% del nominal
        "amp_range":   (1.10, 1.40),
        "freq_range":  (59.8, 60.2),
        "noise_mult":  (0.8, 1.2),
        "sag_depth":   None,
        "swell_boost": None,
        "flicker":     False,
        "outage":      False,
    },
    "outage": {
        "desc": "Corte total: voltaje cae a cero",
        # La señal colapsa — puede haber un transitorio al inicio
        "amp_range":   (0.0, 0.05),    # casi cero, solo ruido
        "freq_range":  (55.0, 65.0),   # frecuencia irrelevante
        "noise_mult":  (0.5, 1.0),
        "sag_depth":   None,
        "swell_boost": None,
        "flicker":     False,
        "outage":      True,
    },
    "flicker": {
        "desc": "Flicker: modulación de amplitud a baja frecuencia (1-25Hz)",
        # La envolvente de la señal varía rápidamente
        "amp_range":   (0.85, 1.15),   # amplitud base normal
        "freq_range":  (59.5, 60.5),
        "noise_mult":  (1.0, 2.0),
        "sag_depth":   None,
        "swell_boost": None,
        "flicker":     True,
        "outage":      False,
    },
}


# ─── Generador de señal ─────────────────────────────────────────────────────
def generate_waveform(label: str, rng: np.random.Generator) -> np.ndarray:
    """
    Genera una waveform sintética para la clase dada.
    Retorna array de floats en Volts (escala ZMPT101B).
    """
    p = PHENOMENA[label]
    t = np.linspace(0, N_SAMPLES / FS, N_SAMPLES)

    # Amplitud base
    amp = rng.uniform(*p["amp_range"]) * V_NORMAL_AMP

    # Frecuencia
    freq = rng.uniform(*p["freq_range"])

    # Fase aleatoria (el trigger no siempre cae en el mismo punto)
    phase = rng.uniform(0, 2 * np.pi)

    # Señal senoidal base
    signal = amp * np.sin(2 * np.pi * freq * t + phase).astype(np.float32)

    # Ruido realista basado en perfil medido
    noise_scale = rng.uniform(*p["noise_mult"]) * NOISE_STD
    noise = rng.normal(0, noise_scale, N_SAMPLES).astype(np.float32)

    # Añadir 2° y 3° armónico (distorsión de red mexicana, cargas no lineales)
    thd = rng.uniform(0.02, 0.08)   # 2-8% THD — típico colonia popular
    h2  = rng.uniform(0, thd) * amp * np.sin(2 * 2 * np.pi * freq * t + rng.uniform(0, np.pi))
    h3  = rng.uniform(0, thd) * amp * np.sin(3 * 2 * np.pi * freq * t + rng.uniform(0, np.pi))
    signal = signal + h2.astype(np.float32) + h3.astype(np.float32)

    # ── Fenómenos especiales ──────────────────────────────────────────────

    if p["outage"]:
        # Transitorio de colapso: la señal cae en algún punto de la ventana
        collapse_point = rng.integers(N_SAMPLES // 8, N_SAMPLES // 2)
        decay = np.ones(N_SAMPLES, dtype=np.float32)
        decay_len = rng.integers(10, 60)  # caída en 1-10ms
        decay[collapse_point:collapse_point + decay_len] = np.linspace(1, 0, decay_len)
        decay[collapse_point + decay_len:] = 0.0
        signal = signal * decay

    if p["flicker"]:
        # Modulación de amplitud: envolvente varía a frecuencia de flicker (1-25Hz)
        flicker_freq = rng.uniform(1, 25)
        flicker_depth = rng.uniform(0.10, 0.35)  # 10-35% de modulación
        envelope = 1.0 + flicker_depth * np.sin(2 * np.pi * flicker_freq * t + rng.uniform(0, np.pi))
        signal = (signal * envelope).astype(np.float32)

    return signal + noise


# ─── Cálculo de features ────────────────────────────────────────────────────
def compute_features(signal: np.ndarray) -> dict:
    sig_mv = signal * 1000.0
    rms = float(np.sqrt(np.mean(sig_mv ** 2)))
    ptp = float(sig_mv.max() - sig_mv.min())
    crest = float(sig_mv.max() / rms) if rms > 0.1 else 0.0
    samples_per_cycle = int(FS / FREQ_NOMINAL)
    rolling = (
        pd.Series(sig_mv)
        .rolling(samples_per_cycle, min_periods=samples_per_cycle)
        .apply(lambda x: np.sqrt(np.mean(x**2)), raw=True)
        .dropna().values
    )
    rms_ripple = float(rolling.std()) if len(rolling) > 1 else 0.0
    zc = np.where((sig_mv[:-1] < 0) & (sig_mv[1:] >= 0))[0]
    freq = float(FS / np.mean(np.diff(zc))) if len(zc) >= 2 else 0.0
    return {
        "rms_mV": round(rms, 3),
        "peak_to_peak_mV": round(ptp, 3),
        "crest_factor": round(crest, 4),
        "rms_ripple_mV": round(rms_ripple, 4),
        "frequency_hz": round(freq, 3),
    }


# ─── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Tecovolt — generador sintético")
    parser.add_argument("--n",       type=int, default=200,
                        help="Waveforms por clase (default: 200)")
    parser.add_argument("--output",  default="./dataset",
                        help="Carpeta de salida (default: ./dataset)")
    parser.add_argument("--classes", nargs="+",
                        default=list(PHENOMENA.keys()),
                        choices=list(PHENOMENA.keys()),
                        help="Clases a generar (default: todas)")
    parser.add_argument("--seed",    type=int, default=42)
    parser.add_argument("--features-only", action="store_true",
                        help="Solo genera features CSV, no señales crudas (más rápido)")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)

    all_features = []
    all_ei       = []

    print(f"Generando {args.n} waveforms × {len(args.classes)} clases = "
          f"{args.n * len(args.classes)} total\n")

    for label in args.classes:
        print(f"  [{label}] {PHENOMENA[label]['desc']}")
        signals  = []
        features = []

        for i in range(args.n):
            sig   = generate_waveform(label, rng)
            feats = compute_features(sig)
            signals.append(sig)
            features.append({"label": label, **feats})

        # Features CSV (liviano, siempre se guarda)
        df_feat = pd.DataFrame(features)
        df_feat.to_csv(out_dir / f"features_{label}.csv", index=False)

        # Resumen estadístico
        df_stats = df_feat.describe().round(3)
        print(f"         RMS: {df_feat.rms_mV.mean():.1f} ± {df_feat.rms_mV.std():.1f} mV  "
              f"| Freq: {df_feat.frequency_hz.mean():.1f} Hz  "
              f"| RMS Ripple: {df_feat.rms_ripple_mV.mean():.2f} mV")

        # EI upload CSV (señales crudas con label)
        if not args.features_only:
            rows = [{"label": label, **{f"s{j}": float(v) for j, v in enumerate(sig)}}
                    for sig in signals]
            pd.DataFrame(rows).to_csv(out_dir / f"ei_upload_{label}.csv", index=False)

        all_features.extend(features)
        if not args.features_only:
            all_ei.extend([
                {"label": label, **{f"s{j}": float(v) for j, v in enumerate(sig)}}
                for sig in signals
            ])

    # Dataset combinado
    pd.DataFrame(all_features).to_csv(out_dir / "features_all.csv", index=False)
    if not args.features_only:
        pd.DataFrame(all_ei).to_csv(out_dir / "ei_upload_all.csv", index=False)

    total = args.n * len(args.classes)
    print(f"\n✓ {total} waveforms generadas en {out_dir}/")
    print(f"  features_all.csv    → {total} filas, 6 columnas")
    if not args.features_only:
        print(f"  ei_upload_all.csv  → {total} filas, {N_SAMPLES + 1} columnas")
    print(f"\nPara subir a Edge Impulse:")
    print(f"  1. Data acquisition → Upload data → CSV")
    print(f"  2. Sube ei_upload_<clase>.csv para cada clase")
    print(f"  3. O sube ei_upload_all.csv si EI acepta múltiples labels en un CSV")


if __name__ == "__main__":
    main()