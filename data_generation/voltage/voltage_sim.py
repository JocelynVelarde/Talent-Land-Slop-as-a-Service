import matplotlib.pyplot as plt
import numpy as np

fs = 1000 #sampling
t = np.linspace(0, 1, fs, endpoint=False) 

signal = np.sin(2 * np.pi * 60 * t)


# plt.plot(t, signal)
# plt.title("Simulated Voltage Signal (60 Hz) taco mexicano ")
# plt.show()

signal_sag = signal.copy()
signal_sag[300:600] *= 0.5

# plt.plot(t, signal_sag)
# plt.title("Simulated Voltage Signal SAG (60 Hz)")
# plt.show()

signal_swell = signal.copy()
signal_swell[300:600] *= 1.5


# plt.plot(t, signal_swell)
# plt.title("Simulated Voltage Signal SWELL (60 Hz)")
# plt.show()

mod = 1 + 0.2 * np.sin(2 * np.pi * 10 * t)
signal_flicker = signal * mod

# plt.plot(t, signal_flicker)
# plt.title("Simulated Voltage Signal FLICKER (60 Hz)")
# plt.show()

plt.figure(figsize=(10,6))

plt.subplot(3,1,1)
plt.title("SAG")
plt.plot(signal_sag)

plt.subplot(3,1,2)
plt.title("SWELL")
plt.plot(signal_swell)

plt.subplot(3,1,3)
plt.title("FLICKER")
plt.plot(signal_flicker)

plt.tight_layout()
plt.show()

def create_event(type):
    mod_signal = signal.copy()
    
    if type == "sag":
        mod_signal[300:600] *= 0.5
    elif type == "swell":
        mod_signal[300:600] *= 1.5
    elif type == "fl":
        mod = 1 + 0.2 * np.sin(2 * np.pi * 10 * t)
        mod_signal = mod_signal * mod
    
    return mod_signal

modified_signal = input("Enter event type (sag, swell, flicker): ")
result_signal = create_event(modified_signal)
plt.plot(t, result_signal)
plt.title(f"Simulated Voltage Signal with {modified_signal}")
plt.show()