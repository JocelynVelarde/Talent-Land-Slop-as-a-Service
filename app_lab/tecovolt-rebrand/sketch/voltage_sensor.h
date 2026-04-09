#ifndef VOLTAGE_SENSOR_H
#define VOLTAGE_SENSOR_H

void voltage_init(int pin);
float voltage_get_rms();
float voltage_get_raw();

#endif
