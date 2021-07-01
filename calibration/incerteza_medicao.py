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

class MeasurementUncertainty():
		def ___init__(self, sensors, measurement):
			self.sensors = sensors
			self.measurement = measurement
					
		def repeatability(self, readings):
			"""
			Desvio padrao experimental da media das leituras do dispositivo padrao e medidor dividido 
			pela raiz quadrada do numero de medicoes
			
			:readings - number
			
			"""
			number_readings = len(readings)
			stdev = (np.std(readings, ddof=1))/(math.sqrt(number_readings))
			return stdev
			

		def standard_uncertainty(self, expanded_uncertainty_standard, k):
			"""
			Incerteza proveniente do certificado de calibracao do dispositivo padrao
			E obtida pela divisao da incerteza expandida pelo fator de abrangência
			"""
			return expanded_uncertainty_standard/k
			
		def curve_fit(self, st_error_estimate):
			"""
			Incerteza proveniente da correcao das leituras atraves do ajuste da curva de calibracao
			"""
			return st_error_estimate/1
			
			
		def standard_derives(self, derives):
			"""
			Incerteza devido a deriva do dispositivo padrao
			"""
			return derives/math.sqrt(3)
			
			
		def resolution(self, instrument_resolution):
			"""
			Incerteza devido a resolucao dos dispositivos
			"""
			return instrument_resolution/math.sqrt(12)
			
			
		def camara_stability(self, stability):
			"""
			Incerteza devido a estabilidade da camara climatica usada para a calibracao do dispositivo padrao
			"""
			return stability/math.sqrt(3)

		def camara_uniformity(self, uniformity):
			"""
			Incerteza devido a uniformidade da camara climatica usada para a calibracao do dispositivo padrao
			"""
			return uniformity/math.sqrt(3)
			
		def item_stability(self, itemstability):
			"""
			Incerteza proveniente da estabilidade do dispositivo medidor em calibracao
			"""
			return itemstability/math.sqrt(3)

		def combined_uncertainty(self, uncertainties, sens_coefficient):
			"""
			Combinacao das componentes de incerteza para temperatura e umidade
			"""
			combined = 0
			for i in uncertainties:
				combined += i*i
			
			combined = (combined * sens_coefficient)
			combined = math.sqrt(combined)
			return combined

		def expanded_uncertainty (self, combined_uncertainty, k):
			"""
			Incerteza expandida para temperatura e umidade
			"""
			return combined_uncertainty*k
	

