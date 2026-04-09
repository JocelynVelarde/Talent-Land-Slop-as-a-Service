# from arduino.app_utils import *

# class SensorManager:
#     def read_voltage(self):
#         try:
#             return Bridge.call("getVoltage") or 0.0
#         except:
#             return 0.0

#     def read_current(self):
#         try:
#             return Bridge.call("getCurrent") or 0.0
#         except:
#             return 0.0

#     def read_temperature(self):
#         try:
#             return Bridge.call("getTemperature") or 0.0
#         except:
#             return 0.0

#     def read_pressure(self):
#         try:
#             return Bridge.call("getPressure") or 0.0
#         except:
#             return 0.0
#     def read_raw_rms(self):
#         try:
#             return Bridge.call("getRawRMS") or 0.0
#         except:
#             return 0.0

#     def read_all(self):
#         return {
#             "voltage": self.read_voltage(),
#             "current": self.read_current(),
#             "temperature": self.read_temperature(),
#             "pressure": self.read_pressure(),
#             "rms": self.read_raw_rms(),
#         }