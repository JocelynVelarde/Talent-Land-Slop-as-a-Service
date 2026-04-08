"""
Tecovolt — Serial DAQ → Edge Impulse CSV
=========================================
Lee rawRMS del Arduino via Serial y genera CSV listo para subir a EI.

Uso:
    python tecovolt_capture.py --port /dev/cu.usbmodem1101 --label baja
    python tecovolt_capture.py --port /dev/cu.usbmodem1101 --label media
    python tecovolt_capture.py --port /dev/cu.usbmodem1101 --label alta
    python tecovolt_capture.py --combine   # une todos los parciales

Puerto en Mac:   /dev/cu.usbmodem*
Puerto en Linux: /dev/ttyACM0
Puerto en Win:   COM3

Para ver puertos disponibles:
    python tecovolt_capture.py --list-ports
"""

import argparse
import time
import glob
import os
from pathlib import Path
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Instala pyserial: pip install pyserial")
    exit(1)

import pandas as pd
import numpy as np

# ── Parámetros — deben coincidir con tecovolt_demand_synth.py ────────────────
WINDOW_SAMPLES  = 10      # 10 lecturas por ventana
BAUD_RATE       = 9600    # Monitor del Arduino App Lab
CAPTURE_SECS    = 35      # segundos de captura por clase (35s → ~50 lecturas)
OUTPUT_DIR      = "./demand_capture"
# ─────────────────────────────────────────────────────────────────────────────


def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No se encontraron puertos seriales.")
        return
    print("Puertos disponibles:")
    for p in ports:
        print(f"  {p.device:25} — {p.description}")


def capture(port, label, duration):
    readings = []
    print(f"\nConectando a {port} @ {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=2)
    except serial.SerialException as e:
        print(f"Error abriendo puerto: {e}")
        return []

    time.sleep(2)
    ser.reset_input_buffer()

    print(f"Capturando clase '{label}' por {duration} segundos...")
    print("Presiona Ctrl+C para detener antes.\n")

    start = time.time()
    try:
        while time.time() - start < duration:
            line = ser.readline().decode('utf-8', errors='ignore').strip()

            if not line or line.startswith('#'):
                if line.startswith('#'):
                    print(f"  {line}")
                continue

            try:
                val = float(line)
                readings.append(val)
                elapsed = time.time() - start
                bar = "█" * int((elapsed / duration) * 30)
                print(f"  [{bar:<30}] {elapsed:5.1f}s | rawRMS: {val:7.2f} | n={len(readings)}", end='\r')
            except ValueError:
                continue

    except KeyboardInterrupt:
        print("\nCaptura detenida manualmente.")

    ser.close()
    print(f"\n\n✓ {len(readings)} lecturas capturadas para clase '{label}'")
    return readings


def readings_to_windows(readings, label):
    rows = []
    n_windows = len(readings) // WINDOW_SAMPLES

    if n_windows == 0:
        print(f"⚠️  Solo {len(readings)} lecturas — necesitas al menos {WINDOW_SAMPLES}.")
        return []

    for i in range(n_windows):
        window = readings[i * WINDOW_SAMPLES:(i + 1) * WINDOW_SAMPLES]
        row = {"label": label}
        row.update({f"r{j}": round(float(window[j]), 4) for j in range(WINDOW_SAMPLES)})
        rows.append(row)

    print(f"  → {n_windows} ventanas de {WINDOW_SAMPLES} lecturas cada una")
    return rows


def save_partial(rows, label):
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"capture_{label}_{ts}.csv")
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)

    vals = df[[f"r{i}" for i in range(WINDOW_SAMPLES)]].values.flatten()
    print(f"  Guardado: {path}")
    print(f"  rawRMS mean: {vals.mean():.2f} ± {vals.std():.2f}")
    return path


def combine():
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "capture_*.csv")))
    if not files:
        print(f"No se encontraron capturas en {OUTPUT_DIR}/")
        return

    dfs = [pd.read_csv(f) for f in files]
    combined = pd.concat(dfs, ignore_index=True).sample(frac=1, random_state=42)

    split = int(len(combined) * 0.8)
    train = combined.iloc[:split]
    test  = combined.iloc[split:]

    train.to_csv(os.path.join(OUTPUT_DIR, "demand_train_real.csv"), index=False)
    test.to_csv(os.path.join(OUTPUT_DIR,  "demand_test_real.csv"),  index=False)

    print(f"\n✓ {len(combined)} ventanas totales")
    print(f"  demand_train_real.csv → {len(train)} filas")
    print(f"  demand_test_real.csv  → {len(test)} filas")
    print(f"\nDistribución por clase:")
    print(combined["label"].value_counts().to_string())

    # Sugerir actualización del synth si hay media real
    if "media" in combined["label"].values:
        media_vals = combined[combined["label"] == "media"][
            [f"r{i}" for i in range(WINDOW_SAMPLES)]].values.flatten()
        print(f"\n⚡ Actualiza tecovolt_demand_synth.py con el rawRMS real de 'media':")
        print(f'   "rawRMS_center": {media_vals.mean():.1f},')
        print(f'   "rawRMS_noise":  {media_vals.std():.1f},')

    print(f"\nPara Edge Impulse:")
    print(f"  Data acquisition → Upload → CSV → demand_train_real.csv")


def main():
    global OUTPUT_DIR
    parser = argparse.ArgumentParser(description="Tecovolt Serial DAQ → EI CSV")
    parser.add_argument("--port",       help="Puerto serial (ej: /dev/cu.usbmodem1101)")
    parser.add_argument("--label",      choices=["baja", "media", "alta"])
    parser.add_argument("--duration",   type=int, default=CAPTURE_SECS)
    parser.add_argument("--output",     default=OUTPUT_DIR)
    parser.add_argument("--combine",    action="store_true")
    parser.add_argument("--list-ports", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR = args.output

    if args.list_ports:
        list_ports()
        return

    if args.combine:
        combine()
        return

    if not args.port or not args.label:
        parser.print_help()
        return

    readings = capture(args.port, args.label, args.duration)
    if not readings:
        return

    rows = readings_to_windows(readings, args.label)
    if not rows:
        return

    save_partial(rows, args.label)

    # Mostrar siguiente paso
    labels_done = set(f.split('_')[1] for f in
                      glob.glob(os.path.join(OUTPUT_DIR, "capture_*.csv")))
    missing = [l for l in ["baja", "media", "alta"] if l not in labels_done]
    print(f"\nSiguiente:")
    if missing:
        print(f"  Capturar: {missing}")
        print(f"  python tecovolt_capture.py --port {args.port} --label {missing[0]}")
    else:
        print(f"  Todas las clases listas. Combinar:")
        print(f"  python tecovolt_capture.py --combine")


if __name__ == "__main__":
    main()