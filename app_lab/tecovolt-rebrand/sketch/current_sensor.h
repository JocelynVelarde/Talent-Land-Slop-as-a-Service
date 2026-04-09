#ifndef CURRENT_SENSOR_H
#define CURRENT_SENSOR_H

void current_init(int pin);
float current_get_amps();
float current_get_raw_rms();

#endif