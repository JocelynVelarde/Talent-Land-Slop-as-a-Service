import time
from arduino.app_utils import *

def main():
    time.sleep(5)
    print("ACS712 AC Current Monitor")
    print("---")
    while True:
        try:
            current = Bridge.call("getCurrent")
            raw = Bridge.call("getRawRMS")
            if current is not None:
                print(f"Current: {current:.3f} A | Raw RMS: {raw:.2f}")
        except Exception as e:
            print(f"Bridge error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    main()