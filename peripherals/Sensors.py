# -*- coding: utf-8 -*-

import json
import Adafruit_DHT
import RPi.GPIO as GPIO
import numpy as np
from security.Sign import Signature
from utils.DataStructures import Queue
from utils.Config import ConfigSensors, ConfigDeviceInfo
from datetime import datetime


class Sensor(object):
    def __init__(self):
        self.LAST_READ_TIME = 0
        self.signature = Signature()

    @staticmethod
    def register_measures(data):
        """
        Converte dicionario com informaçoes de mediçao em formato JSON e registra em um arquivo com extensão .json.
            :data - dict
            :return - None
        """
        json_data = json.dumps(data)
        file_path = "registros/" + data["property"] + "/" + str(data["date"]) + ".json"

        with open(file_path, "a+") as f:
            f.write(json_data)

    def format_data(self, _property, value):
        """
        Informacoes a serem inseridas junto ao registro das medicoes (arquivo com extensao .json)

        :_property - string
        :value - number

        """
        config = ConfigDeviceInfo()
        _id = config.id
        location = config.location
        date = datetime.now().timestamp()

        data = {'id': _id,
                'location': location,
                'property': _property,
                'date': date,
                'value': value
                }

        signature = self.signature.sign(str(data).encode())
        signature = str(signature)
        data['signature'] = signature
        self.register_measures(data)
       
        return data

    @staticmethod
    def is_valid_std_deviation(readings):
        """
        Verifica o desvio padrao de um conjunto de leituras em uma lista.
        :readings - list
        :return - boolean
        """
        std_deviation = np.std(readings)
        return std_deviation < 10


class DHT22(Sensor):
    def __init__(self):
        '''
        Construtor da classe DHT22, onde pino identifica e a porta GPIO do Raspberry no qual o sensor se encontra
        conectado, quantidade_leituras esta relacionando com a quantidade de leituras que o sensor devera realizar
        para verificar o desvio padrao e consolidar uma unica mediçao e intervalo_medicao e o tempo, em segundos,
        entre mediçoes consecutivas. As confiuraçoes do sensor sao obtidas atraves do arquivo config.ini
        '''
        super().__init__()
        config = ConfigSensors()
        self.DHT_SENSOR = Adafruit_DHT.DHT22
        self.DHT_PIN = config.DHT_pin
        self.NUMBER_OF_READINGS = config.DHT_number_of_readings
        self.INTERVAL = config.DHT_interval
        self.humidity_queue = Queue(size=self.NUMBER_OF_READINGS)
        self.temperature_queue = Queue(size=self.NUMBER_OF_READINGS)

    @property
    def read(self):
        temperature_size = 0
        humidity_size = 0
        has_new_value = False
        if datetime.now().timestamp() - self.LAST_READ_TIME > self.INTERVAL:
            self.clean_queue()
            while (temperature_size < self.NUMBER_OF_READINGS and
                   humidity_size < self.NUMBER_OF_READINGS):
                self.get_temperature_and_humidity()
                temperature_size = len(self.temperature_queue.get_items())
                humidity_size = len(self.humidity_queue.get_items())
                has_new_value = True
            self.LAST_READ_TIME = datetime.now().timestamp()
        return self.format_last_temperature_and_humidity_readings() if has_new_value else None

    def clean_queue(self):
        self.temperature_queue.pop_item()
        self.humidity_queue.pop_item()

    def get_temperature_and_humidity(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.DHT_SENSOR, self.DHT_PIN)
        if humidity is not None and temperature is not None:
            print(f'Umidade: {humidity} | Temperatura: {temperature}')
            if self.is_valid_reading(self.humidity_queue, humidity):
                self.humidity_queue.add(humidity)

            if self.is_valid_reading(self.temperature_queue, temperature):
                self.temperature_queue.add(temperature)
        else:
            print("Falha ao receber os dados do sensor DHT22.")

    def is_valid_reading(self, readings_list, new_reading):
        temp = []
        temp.extend(readings_list.get_items())
        temp.append(new_reading)
        return self.is_valid_std_deviation(temp)

    def format_last_temperature_and_humidity_readings(self):
        humidity = self.humidity_queue.get_items()[-1]
        humidity = self.format_data('UMIDADE', humidity)

        temperature = self.temperature_queue.get_items()[-1]
        temperature = self.format_data('TEMPERATURA', temperature)

        return [humidity, temperature]
        
    def get_queues_items(self):
        temp = self.temperature_queue.get_items()
        humi = self.humidity_queue.get_items()
	
        return temp, humi


class PIR(Sensor):
    def __init__(self):
        '''
        Construtor da classe PIR, onde pino identifica e a porta GPIO do Raspberry no qual o sensor se encontra
        conectado e intervalo_medicao e o tempo, em segundos, entre mediçoes consecutivas.

        :pino - int
        :intervalo_medicao: - int

        '''
        super().__init__()
        config = ConfigSensors()
        self.PIN = config.PIR_pin
        self.INTERVAL = config.PIR_interval
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN, GPIO.IN)

    def read(self):
        data_to_send = []
        if (datetime.now().timestamp() - self.LAST_READ_TIME > self.INTERVAL and
                GPIO.input(self.PIN)):
            data_to_send.append(self.format_data("MOVIMENTO", 1))
            self.LAST_READ_TIME = datetime.now().timestamp()
        return data_to_send if len(data_to_send) > 0 else None
