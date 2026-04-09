import numpy as np

def generate_features(implementation_version, draw_graphs, raw_data, axes, sampling_freq, scale_axes):
    fs = 6279.8
    v = np.array(raw_data)

    # ── Features de amplitud ─────────────────────────────────────────────────
    rms   = float(np.sqrt(np.mean(v ** 2)))
    peak  = float(np.max(np.abs(v)))
    ptp   = float(np.max(v) - np.min(v))
    crest = float(peak / rms) if rms > 1e-9 else 0.0

    # ── RMS ripple ───────────────────────────────────────────────────────────
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

    # ── Frecuencia dominante via FFT ─────────────────────────────────────────
    freqs   = np.fft.rfftfreq(len(v), d=1.0 / fs)
    fft_mag = np.abs(np.fft.rfft(v))
    dom_freq = float(freqs[1 + np.argmax(fft_mag[1:])]) if rms > 1e-9 else 0.0

    # ── THD (Total Harmonic Distortion) — feature clave para flicker/normal ──
    # Ratio de energía en armónicos 2° y 3° vs fundamental (60Hz)
    fund_idx = int(np.argmin(np.abs(freqs - 60.0)))
    h2_idx   = fund_idx * 2
    h3_idx   = fund_idx * 3
    h2 = float(fft_mag[h2_idx]) if h2_idx < len(fft_mag) else 0.0
    h3 = float(fft_mag[h3_idx]) if h3_idx < len(fft_mag) else 0.0
    thd = float((h2 + h3) / (fft_mag[fund_idx] + 1e-9)) if rms > 1e-9 else 0.0

    features_dict = {
        'rms_v':            round(rms,      6),
        'peak_to_peak_v':   round(ptp,      6),
        'crest_factor':     round(crest,    6),
        'rms_ripple_v':     round(rms_ripple, 6),
        'dominant_freq_hz': round(dom_freq, 4),
        'thd':              round(thd,      6),   # nueva feature
    }

    labels = list(features_dict.keys())
    values = list(features_dict.values())

    return {
        'features': values,
        'labels':   labels,
        'graphs':   [],
        'output_config': {
            'type':  'flat',
            'shape': {'width': len(labels)}
        }
    }