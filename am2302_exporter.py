#!/usr/bin/env python3
'''Prometheus exporter for am2302 air temperature and humidity sensor'''

import sys
import argparse
import time
import Adafruit_DHT
from prometheus_client import start_http_server, Summary, Gauge

parser = argparse.ArgumentParser(
        description="Prometheus exporter for am2302 air temperature and humidity sensor")

parser.add_argument('--temperature_scale',
                    action='store',
                    default='celsius',
                    help='[celsius|farenheit|kelvin], default: celsius')
parser.add_argument('--listen',
                    action='store',
                    default='0.0.0.0',
                    help='bind to address, default: 0.0.0.0')
parser.add_argument('--port',
                    action='store',
                    type=int,
                    default=8001,
                    help='bind to port, default: 8001')
parser.add_argument('--polling_interval',
                    action='store',
                    type=int,
                    default=1,
                    help='sensor polling interval, seconds, default: 1')
parser.add_argument('--pin',
                    action='store',
                    type=int,
                    default=18,
                    help='pin number, where sensor is connected, default: 18')
parser.add_argument('--verbose',
                    action='store_true',
                    help='print output to stdout')

args = parser.parse_args()

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

sensor=Adafruit_DHT.AM2302

humidity = Gauge('am2302_humidity', 'Air relative humidity, %')
temperature = Gauge('am2302_temperature', 'Air temperature, ' + args.temperature_scale)


@REQUEST_TIME.time()
def get_data():
    '''Get data from sensor'''
    humidity_raw, temperature_raw = Adafruit_DHT.read_retry(sensor, args.pin)

    if args.temperature_scale=='celsius':
        temperature_processed=temperature_raw
    elif args.temperature_scale=='kelvin':
        temperature_processed=temperature_raw+273.15
    elif args.temperature_scale=='farenheit':
        temperature_processed= 9.0/5.0 * temperature_raw + 32
    else:
        print('ERROR: Wrong temperature_scale: only celsius|farenheit|kelvin supported')
        sys.exit(1)

    temperature.set(temperature_processed)
    humidity.set(humidity_raw)

    if args.verbose:
        print(f"{temperature_processed:05.2f} {args.temperature_scale}; {humidity_raw:05.2f}%")

if __name__ == '__main__':
    start_http_server(args.port, args.listen)
    while True:
        get_data()
        time.sleep(args.polling_interval)
