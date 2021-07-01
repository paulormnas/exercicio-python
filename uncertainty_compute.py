# -*- coding: utf-8 -*-

import json
import Adafruit_DHT
import math
import numpy as np
from security.Sign import Signature
from utils.DataStructures import Queue
from utils.Config import ConfigSensors, ConfigDeviceInfo
from datetime import datetime
from peripherals.Sensors import *
from calibration.incerteza_medicao import MeasurementUncertainty

incert = {}
		
with open("info_incerteza.json") as f:
	incert_json = f.read()
	incert = json.loads(incert_json) 

sensors = DHT22()
sensors.read

measurement = MeasurementUncertainty()

### Meter device readings ###
meter_temp_readings, meter_hum_readings = sensors.get_queues_items()

### Standard device readings ###
st_temp_readings = [25 for x in range(0,10)]
st_hum_readings  = [70.8 for x in range(0,10)]

### Uncertainty components ###

### Temperature ###
u_standard_temp = measurement.repeatability(st_temp_readings)
u_meter_temp = measurement.repeatability(meter_temp_readings)

u_curve_fit_temp = measurement.curve_fit(incert["standard_components"]["st_error_estimate_temp"])
U_st_temp = measurement.standard_uncertainty(incert["standard_components"]["st_temp_expanded_uncertainty"], incert["standard_components"]["k"])
u_derives_temp = measurement.standard_derives(incert["temp_components"]["derive"])
u_res_meter = measurement.resolution(incert["temp_components"]["value_resolution"])
u_res_standard = measurement.resolution(incert["temp_components"]["value_resolution"])
u_stability_temp = measurement.camara_stability(incert["temp_components"]["stability"])
u_uniformity_temp = measurement.camara_uniformity(incert["temp_components"]["uniformity"])
u_item_temp = measurement.item_stability(incert["temp_components"]["itemstability"])

### Humidity ###

u_standard_hum = measurement.repeatability(st_hum_readings)
u_meter_hum = measurement.repeatability(meter_hum_readings)


u_curve_fit_hum = measurement.curve_fit(incert["standard_components"]["st_error_estimate_hum"])
U_st_hum = measurement.standard_uncertainty(incert["standard_components"]["st_hum_expanded_uncertainty"],incert["standard_components"]["k"])
u_derives_hum = measurement.standard_derives(incert["hum_components"]["derive"])
u_res_meter = measurement.resolution(incert["hum_components"]["value_resolution"])
u_res_standard = measurement.resolution(incert["hum_components"]["value_resolution"])
u_stability_hum = measurement.camara_stability(incert["hum_components"]["stability"])
u_uniformity_hum = measurement.camara_uniformity(incert["hum_components"]["uniformity"])
u_item_hum = measurement.item_stability(incert["hum_components"]["itemstability"])


list_of_uncertainties_temp = [u_standard_temp,u_meter_temp,u_curve_fit_temp, U_st_temp, u_derives_temp, u_res_meter, u_res_standard, u_stability_temp, u_uniformity_temp, u_item_temp]
list_of_uncertainties_hum = [u_standard_hum, u_meter_hum, u_curve_fit_hum, U_st_hum, u_derives_hum, u_res_meter, u_res_standard, u_stability_hum, u_uniformity_hum, u_item_hum]

### Calculation of combined uncertainty ###
### Temperature ###
u_comb_temp = measurement.combined_uncertainty(list_of_uncertainties_temp, incert["standard_components"]["sensitivity_coefficient"])
u_comb_hum = measurement.combined_uncertainty(list_of_uncertainties_hum, incert["standard_components"]["sensitivity_coefficient"])

### Calculation of expanded uncertainty ###
U_temp = measurement.expanded_uncertainty(u_comb_temp,incert["standard_components"]["k"])
U_hum = measurement.expanded_uncertainty(u_comb_hum,incert["standard_components"]["k"])

### Results printing  ###
print("The standard deviation of the average temperature of standard device: ",u_standard_temp, "°C")
print("The standard deviation of the average humidity of standard device: ",u_standard_hum, "%ur")
print("The standard deviation of the average temperature of meter device: ",u_meter_temp, "°C")
print("The standard deviation of the average humidity of meter device: ",u_meter_hum, "%ur")

print("The Uncertainty due to curve fit temperature:", u_curve_fit_temp)
print("The Uncertainty due to curve fit humidity:", u_curve_fit_hum)


print("The uncertainty of the standard device from the calibration certificate temperature:",U_st_temp, "°C")
print("The uncertainty of the standard device from the calibration certificate humidity:",U_st_hum, "°C")


print("The uncertainty due to the standard derives:",u_derives_temp, "°C")
print("The uncertainty due to the standard derives:",u_derives_hum, "%ur")

print("The uncertainty due to the meter resolution:",u_res_meter, "°C")
print("The uncertainty due to the standard resolution:",u_res_standard, "°C")

print("The uncertainty due to the camara stability temperature:",u_stability_temp, "°C")
print("The uncertainty due to the camara uniformity temperature:",u_uniformity_temp, "°C")
print("The uncertainty due to the camara stability humidity:",u_stability_hum, "%ur")
print("The uncertainty due to the camara uniformity:humidity",u_uniformity_hum, "%ur")

print("The uncertainty due to the item stability:",u_item_temp, "°C")
print("The uncertainty due to the item stability:",u_item_hum, "%ur")

print("The combined uncertainty of temperature is:", u_comb_temp,"°C")
print("The expanded uncertainty of temperature is:", U_temp, "°C")

print("The combined uncertainty of humidity is:", u_comb_hum, "%ur")
print("The expanded uncertainty of humidity is:", U_hum, "%ur")


#incert["temp_components"]["derive"]
