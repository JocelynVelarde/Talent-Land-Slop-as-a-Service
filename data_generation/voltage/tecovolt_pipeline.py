"""
Tecovolt — PicoScope CSV → Edge Impulse pipeline
================================================
1. Lee todos los CSVs de una carpeta (un CSV = una waveform)
2. Calcula features: RMS, peak-to-peak, crest factor, RMS ripple, freq dominante
3. Augmenta con ruido/variacion de amplitud realista (basado en el ruido medido)
4. Exporta dos archivos:
   - edge_impulse_raw.csv     : senal cruda (1260 samples por fila) para Time Series
   - edge_impulse_features.csv: features calculadas para Classifier clasico

USO:
    python tecovolt_pipeline.py --input ./capturas/normal     --label normal
    python tecovolt_pipeline.py --input ./capturas/sag_leve   --label sag_leve
    python tecovolt_pipeline.py --input ./capturas/sag_severo --label sag_severo
    python tecovolt_pipeline.py --input ./capturas/swell      --label swell
    python tecovolt_pipeline.py --input ./capturas/outage     --label outage
    python tecovolt_pipeline.py --input ./capturas/flicker    --label flicker

    # Combinar todo en un solo CSV al final:
    python tecovolt_pipeline.py --combine
"""

import argparse
import glob
import os
import numpy as np
import pandas as pd

# ── Parametros ────────────────────────────────────────────────────────────────
N_SAMPLES   = 1260      # muestras por waveform (PicoScope 200ms @ 6280Hz)
SAMPLE_RATE = 6279.8    # Hz
N_AUG       = 50        # variaciones sinteticas por captura real
OUTPUT_DIR  = "./edge_impulse_output"
# ─────────────────────────────────────────────────────────────────────────────


def load_waveform(path):
    """Lee un CSV de PicoScope, devuelve (time_ms, voltage_V)."""
    df = pd.read_csv(path, skiprows=[1, 2])  # salta fila de unidades y blank
    t = df['Time'].values        # ms
    v = df['Channel A'].values   # V
    # Truncar/padear a N_SAMPLES para uniformidad
    if len(v) >= N_SAMPLES:
        v, t = v[:N_SAMPLES], t[:N_SAMPLES]
    else:
        pad = N_SAMPLES - len(v)
        v = np.pad(v, (0, pad), mode='edge')
        t = np.pad(t, (0, pad), mode='linear_ramp')
    return t, v


def compute_features(v, fs=SAMPLE_RATE):
    """Extrae features de calidad electrica de una senal de voltaje."""
    rms   = float(np.sqrt(np.mean(v ** 2)))
    peak  = float(np.max(np.abs(v)))
    ptp   = float(np.max(v) - np.min(v))
    crest = float(peak / rms) if rms > 1e-9 else 0.0

    # RMS ripple: std del RMS por ciclo (ventana de 1/60Hz)
    cycle_samples = int(fs / 60)
    n_windows = len(v) // cycle_samples
    if n_windows > 0:
        window_rms = [
            float(np.sqrt(np.mean(v[i * cycle_samples:(i + 1) * cycle_samples] ** 2)))
            for i in range(n_windows)
        ]
        rms_ripple = float(np.std(window_rms))
    else:
        rms_ripple = 0.0

    # Frecuencia dominante via FFT (ignora DC)
    freqs    = np.fft.rfftfreq(len(v), d=1.0 / fs)
    fft_mag  = np.abs(np.fft.rfft(v))
    dom_freq = float(freqs[1 + np.argmax(fft_mag[1:])])

    return {
        'rms_v':            round(rms, 6),
        'peak_to_peak_v':   round(ptp, 6),
        'crest_factor':     round(crest, 6),
        'rms_ripple_v':     round(rms_ripple, 6),
        'dominant_freq_hz': round(dom_freq, 4),
    }


def augment(signal, n=N_AUG):
    """
    Genera n variaciones sinteticas de una senal real.
    Ruido basado en el perfil de ruido medido del instrumento.
    """
    noise_level = float(np.std(np.diff(signal))) * 0.8
    augmented = []
    for _ in range(n):
        noise   = np.random.normal(0, noise_level, len(signal))
        amp_var = np.random.uniform(0.92, 1.08)
        augmented.append(signal * amp_var + noise)
    return augmented


def process_folder(input_dir, label, augment_data=True):
    """
    Procesa todos los CSVs en input_dir con el label dado.
    Devuelve (raw_rows, feature_rows).
    """
    files = sorted(glob.glob(os.path.join(input_dir, "*.csv")))
    if not files:
        print(f"  ⚠️  No se encontraron CSVs en {input_dir}")
        return [], []

    raw_rows, feature_rows = [], []

    for fpath in files:
        t, v = load_waveform(fpath)
        all_signals = [v] + (augment(v, N_AUG) if augment_data else [])

        for sig in all_signals:
            # Raw row: label + 1260 valores de la senal
            raw_row = {'label': label}
            raw_row.update({f's{i}': round(float(sig[i]), 6) for i in range(N_SAMPLES)})
            raw_rows.append(raw_row)

            # Feature row
            feat = compute_features(sig)
            feat['label'] = label
            feature_rows.append(feat)

    real_count = len(files)
    aug_count  = len(raw_rows) - real_count
    print(f"  ✓ {real_count} capturas reales → {len(raw_rows)} total "
          f"({aug_count} augmentadas) [{label}]")
    return raw_rows, feature_rows


def combine_outputs():
    """Combina todos los CSVs parciales del output dir en archivos finales."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_dfs, feat_dfs = [], []
    for f in sorted(glob.glob(os.path.join(OUTPUT_DIR, "raw_*.csv"))):
        raw_dfs.append(pd.read_csv(f))
    for f in sorted(glob.glob(os.path.join(OUTPUT_DIR, "features_*.csv"))):
        feat_dfs.append(pd.read_csv(f))

    if raw_dfs:
        combined = pd.concat(raw_dfs, ignore_index=True).sample(frac=1, random_state=42)
        out = os.path.join(OUTPUT_DIR, "edge_impulse_raw_ALL.csv")
        combined.to_csv(out, index=False)
        print(f"✓ Raw combinado: {len(combined)} filas → {out}")

    if feat_dfs:
        combined = pd.concat(feat_dfs, ignore_index=True).sample(frac=1, random_state=42)
        out = os.path.join(OUTPUT_DIR, "edge_impulse_features_ALL.csv")
        combined.to_csv(out, index=False)
        print(f"✓ Features combinado: {len(combined)} filas → {out}")
        print(f"\nDistribucion de clases:")
        print(combined['label'].value_counts().to_string())


def main():
    parser = argparse.ArgumentParser(description='Tecovolt PicoScope → Edge Impulse pipeline')
    parser.add_argument('--input',   help='Carpeta con CSVs de PicoScope')
    parser.add_argument('--label',   help='Clase: normal|sag_leve|sag_severo|swell|outage|flicker')
    parser.add_argument('--no-aug',  action='store_true', help='Desactivar augmentation')
    parser.add_argument('--combine', action='store_true', help='Combinar todos los parciales')
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.combine:
        combine_outputs()
        return

    if not args.input or not args.label:
        parser.print_help()
        return

    valid = {'normal', 'sag_leve', 'sag_severo', 'swell', 'outage', 'flicker'}
    if args.label not in valid:
        print(f"⚠️  Label invalido. Opciones: {valid}")
        return

    print(f"\nProcesando: {args.input} → label='{args.label}'")
    raw_rows, feat_rows = process_folder(args.input, args.label, not args.no_aug)

    if raw_rows:
        raw_df  = pd.DataFrame(raw_rows)
        feat_df = pd.DataFrame(feat_rows)

        raw_df.to_csv(os.path.join(OUTPUT_DIR, f"raw_{args.label}.csv"), index=False)
        feat_df.to_csv(os.path.join(OUTPUT_DIR, f"features_{args.label}.csv"), index=False)
        print(f"  → {OUTPUT_DIR}/raw_{args.label}.csv")
        print(f"  → {OUTPUT_DIR}/features_{args.label}.csv")


if __name__ == '__main__':
    main()