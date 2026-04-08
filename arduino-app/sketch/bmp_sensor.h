#ifndef BMP_SENSOR_H
#define BMP_SENSOR_H

bool bmp_init();
float bmp_read_temperature();
float bmp_read_pressure();

#endif