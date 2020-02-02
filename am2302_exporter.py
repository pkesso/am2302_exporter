#!/usr/bin/env python

# TODO parse args: bus, verbose, pin, c/f/k, addr, port

import time
import Adafruit_DHT
from prometheus_client import start_http_server, Summary, Gauge

temperature_scale='celsius'
listen='0.0.0.0'
port=8001

usage_message = """Prometheus exporter for AM2302 air temperature and relative humidity sensor
           Homepage:
           Options:
           --temperature-scale=[celsius|farenheit|kelvin], default is celsius
           --pin=<pin number>, MANDATORY pin № in BCM notation, see `gpio readall`
           --refresh_interval=<seconds>, default is 1
           --verbose
           --listen=<ip>, default is 0.0.0.0
           --port=<port>, default is 8000 #TODO"""

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

sensor=Adafruit_DHT.AM2302
pin=18

humidity = Gauge('am2302_humidity', 'Air relative humidity, %')
temperature = Gauge('am2302_temperature', 'Air temperature, ' + temperature_scale)

def usage():
    print('usage_message')
    exit(0)

@REQUEST_TIME.time()
def get_data():
    humidity_raw, temperature_raw = Adafruit_DHT.read_retry(sensor, pin)

    if temperature_scale=='celsius':
        temperature_processed=temperature_raw
    elif humidity_scale=='kelvin':
        temperature_processed=temperature_raw+273.15
    elif temperature_scale=='farenheit':
        temperature_processed= 9.0/5.0 * temperature_raw + 32
    else:
        print('ERROR: Wrong temperature_scale: only celsius|farenheit|kelvin supported')
        exit(1)



    temperature.set(temperature_processed)
    humidity.set(humidity_raw)

if __name__ == '__main__':
    start_http_server(port)
    while True:
        get_data()
        time.sleep(1)
