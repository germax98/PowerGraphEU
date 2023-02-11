import arrow
import json
import time
import atexit
import sys
import logging

from flask import Flask, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from pymongo import MongoClient


from entsoe_definition import *

import parsers

def update_database():
    parsers.update_all_production()
    parsers.update_all_percentage()
    app.logger.info('Database updated')

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(update_database,'interval', seconds = 3600)
scheduler.start()

app = Flask(__name__)
CORS(app)

def connect_to_database():
    client = MongoClient('',
                     username = '',
                     password = mongo_password
    )
    return client

def get_last_update_timestamp(documentType, client = None):
    if not client:
        client = connect_to_database()
    metadata_db = client['metadata']
    datetimes_collection = metadata_db['datetimes']

    metadata = datetimes_collection.find_one({'documentType': documentType})
    datetime = arrow.get(metadata['datetime'])

    return datetime

@app.route("/update_renewable_percentage", methods=['GET'])
def current_renewable_percentage():
    country_code = request.args.get('country')
    client = connect_to_database()
    database = client[country_code]
    collection = database['generation_by_type']

    last_update_datetime = get_last_update_timestamp('A75', client)

    last_update_datetime = last_update_datetime.shift(hours=-1)

    renewable = []
    non_renewable = []

    for psr_type in ENTSOE_RENEWABLE:
            document = collection.find_one({'psr_type': psr_type, 'time': str(last_update_datetime)})
            if document:
                    renewable.append(document['quantity'])

    for psr_type in ENTSOE_NON_RENEWABLE:
            document = collection.find_one({'psr_type': psr_type, 'time': str(last_update_datetime)})
            if document:
                    non_renewable.append(document['quantity'])

    renewable = sum(renewable)
    non_renewable = sum(non_renewable)
        
    production_values = {'renewable': renewable, 'non_renewable': non_renewable}
    return production_values

@app.route('/production', methods=['GET'])
def query_production():
    country_code = request.args.get('country')
    return_json = dict()
    client = connect_to_database()
    database = client[country_code]
    collection = database['generation_by_type']

    result = collection.find({'psr_type': 'B01'}, {'_id': 0, 'documentType': 0, 'processType': 0, 'psr_type': 0})
    for entry in result:
        return_json[entry['time']] = entry['quantity']
    print(return_json)
    return return_json

@app.route('/percentage', methods=['GET'])
def query_percentage():
    country_code = request.args.get('country')

    date = arrow.utcnow()
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    beginning = date.shift(days=-8)
    end = date

    renewable_percentage = list()
    fossile_percentage = list()
    data_date = list()

    client = connect_to_database()
    database = client[country_code]
    collection = database['renewable_percentage']

    result = collection.find({'time': {'$gt': str(beginning), '$lt': str(end)}})

    for entry in result:
        data_date.append(arrow.get(entry['time']).format('YYYY-MM-DD'))
        renewable_percentage.append(entry['renewable_percentage'])
        fossile_percentage.append(entry['fossile_percentage'])

    data = {
        'date': data_date,
        'renewable_percentage': renewable_percentage,
        'fossile_percentage': fossile_percentage
    }

    return data

@app.route('/renewable_forecast', methods=['GET'])
def renewable_forecast():
    country_code = 'DE'

    params_renewable = {
            'documentType': 'A69',
            'processType': 'A01'
        }

    params_aggregated = {
        'documentType': 'A71',
        'processType': 'A01'
    }

    start_datetime = arrow.utcnow()
    start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    end_datetime = start_datetime.shift(days=+1)

    response = parsers.query_entsoe(params_renewable, country_code, start_datetime, end_datetime)
    productions, datetimes = parsers.parse_production_by_type(response)

    renewable_production_list = list()

    for entry in productions:
        for key in entry:
            sum_production =+ entry[key]
        renewable_production_list.append(sum_production)

    renewable_production_dict = dict(zip(datetimes, renewable_production_list))

    response = parsers.query_entsoe(params_aggregated, country_code, start_datetime, end_datetime)
    productions, datetimes = parsers.parse_aggregated_production(response)

    aggregated_production = dict(zip(datetimes, productions))

    renewable_production = list()
    datetimes = list()

    for entry in aggregated_production:
        renewable_production.append(renewable_production_dict[entry])
        datetimes.append(entry)

    renewable_production = dict(zip(datetimes, renewable_production))

    renewable_percentage = {k: renewable_production[k]/aggregated_production[k] for k in renewable_production.keys()}

    productions = list()
    datetimes = list()

    for datetime,value in renewable_percentage.items():
        if datetime >= start_datetime and datetime < end_datetime:
            datetimes.append(datetime.format('YYYY-MM-DDTHH'))
            productions.append(value)

    data = {
        'date': datetimes,
        'renewable_percentage': productions
    }

    return data

@app.route('/')
def logging():
    app.logger.warning('test warning')
    app.logger.error('test error')
    app.logger.info('test info')
    return 'check console'

# atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)

    
