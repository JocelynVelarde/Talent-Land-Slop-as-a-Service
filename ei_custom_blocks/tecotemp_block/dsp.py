import numpy as np

def generate_features(implementation_version, draw_graphs, raw_data, axes, sampling_freq, scale_axes):
    # features is a 1D array, reshape so we have a matrix


    # temp_cols = [c for c in df.columns if 'temp_' in c]
    # hum_cols = [c for c in df.columns if 'hum_' in c]
    tmp_avg = np.average(np.array(raw_data[:10]))
    hum_avg = np.average(np.array(raw_data[10:]))
    
    return {
        'features': [tmp_avg, hum_avg],
        'labels': ["avg_temperature", "avg_humidity"],
        'graphs': [],
        # if you use FFTs then set the used FFTs here (this helps with memory optimization on MCUs)
        'fft_used': [],
        'output_config': {
            # type can be 'flat', 'image' or 'spectrogram'
            'type': 'flat',
            'shape': {
                # shape should be { width, height, channels } for image, { width, height } for spectrogram
                'width': 2
            }
        }
    }
