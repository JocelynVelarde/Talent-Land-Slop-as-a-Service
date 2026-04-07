import numpy as np

def generate_features(implementation_version, draw_graphs, raw_data, axes, sampling_freq, scale_axes):
    fs = 6279.8   
    # values turned into np array
    v = np.array(raw_data)
    
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
    
    features_dict = {
        'rms_v':            round(rms, 6),
        'peak_to_peak_v':   round(ptp, 6),
        'crest_factor':     round(crest, 6),
        'rms_ripple_v':     round(rms_ripple, 6),
        'dominant_freq_hz': round(dom_freq, 4),
    }

    labels = list(features_dict.keys())
    values = list(features_dict.values())
    return {
        'features': values,
        'labels': labels,
        'graphs': [],
        'output_config': {
            'type': 'flat',
            'shape': {
                'width': len(labels)
            }
        }
    }