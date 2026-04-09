#include <Arduino_RouterBridge.h>
#include "current_sensor.h"
#include "voltage_sensor.h"
#include "bmp_sensor.h"

#define CURRENT_PIN A0
#define VOLTAGE_PIN A1
#define RELAY_PIN D2

float getRawRMS()     { return current_get_raw_rms(); }
float getAmps()       { return current_get_amps(); }
float getVoltage()    { return voltage_get_rms(); }
float getRawVoltage() { return voltage_get_raw(); }
float getTemp()       { return bmp_get_temperature(); }
float getPres()       { return bmp_get_pressure(); }

bool setRelay(bool state) {
    digitalWrite(RELAY_PIN, state ? HIGH : LOW);
    return state;
}

void setup() {
    Bridge.begin();
    Monitor.begin();

    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);

    Monitor.println("Initializing sensors...");
    current_init(CURRENT_PIN);
    voltage_init(VOLTAGE_PIN);
    bmp_init();

    Bridge.provide("getRawRMS", getRawRMS);
    Bridge.provide("getAmps", getAmps);
    Bridge.provide("getVoltage", getVoltage);
    Bridge.provide("getRawVoltage", getRawVoltage);
    Bridge.provide("getTemperature", getTemp);
    Bridge.provide("getPressure", getPres);
    Bridge.provide("setRelay", setRelay);

    Monitor.println("All sensors ready.");
}

void loop() {
}
