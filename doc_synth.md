## Docs Tecovoltianos Impulse

### tecovolt_synth.py

> basically crea los datos de acuerdo a la red eléctrica mexicana, agrega ruido sintético compatible con las condiciones de aglomeraciones urbanas y/o rurales.

Toma en cuenta los factores de ruido del Periscope para una aplicación on the edge.

### tecovolt_pipeline.py

> lee los csvs de el dir seleccionado, calcula las features necesarias para el classifier + at the same time hace augmentation para poder tener un insight

Features:

1. RMS,
2. peak-to-peak,
3. crest factor,
4. RMS ripple,
5. freq dominante

El ruido medido se basa en datos realistas del picoscope 2000.

```python
N_SAMPLES   = 1260      # muestras por waveform (PicoScope 200ms @ 6280Hz)
SAMPLE_RATE = 6279.8    # Hz
N_AUG       = 50        # variaciones sinteticas por captura real
OUTPUT_DIR  = "./edge_impulse_output"
```

### Main functions:

#### compute_features

> Obtiene: rms, peak, crest, ptp.

#### augment

> genera n variaciones sinteticas de una senal real. Ruido basado en el perfil de ruido medido del instrumento Picoscope.

#### process_folder

> Procesa todos los CSVs en input_dir con el label dado. Devuelve (raw_rows, feature_rows)

## Output

Un master csv con labels para classifier clásico.

## Temp Anomaly Detection

> Usa datos del BMP280 para clasificar la integrdad del tablero energético. Clasifica riesgo: bajo, alto, medio.

## Tipo de modelo

Flatten:
Es ideal, ya que, aunque recibamos datos a 1 Hz, la temperatura cambia lento. No es necesario sobrecargar el flujo de recibimiento de la Arduino Q.

_Usa temperatura y humedad del BMP280 a 1 Hz para clasificar el riesgo térmico del tablero en tres niveles. Elegimos Flatten como bloque de procesamiento porque el calor es un fenómeno lento, así que no necesita análisis de frecuencia. Lo entrenamos con datos sintéticos generados a partir de rangos documentados para tableros residenciales mexicanos."_
