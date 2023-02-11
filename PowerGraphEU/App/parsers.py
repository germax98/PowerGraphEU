"""Provides parsers for the ENTSOE API"""

import re
from collections import defaultdict
import concurrent.futures

import arrow
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient

from secret import mongo_password
from entsoe_definition import *


def init_session(session=None):
    if not session:
        session = requests.Session()
        session.params.update({'securityToken': ''})
    return session

def query_entsoe(params, country_code, datetime_start, datetime_end, session = None):
    if not session:
        session = init_session()
    params['in_Domain'] = ENTSOE_DOMAIN_MAPPINGS[country_code]
    params['periodStart'] = datetime_start.format('YYYYMMDDHHmm')
    params['periodEnd'] = datetime_end.format('YYYYMMDDHHmm')
    
    return session.get(ENTSOE_ENDPOINT, params = params).text

def datetime_from_position(start, position, resolution):
    """Finds time granularity of data."""

    m = re.search(r'PT(\d+)([M])', resolution)
    if m:
        digits = int(m.group(1))
        scale = m.group(2)
        if scale == 'M':
            return start.shift(minutes=(position - 1) * digits)
    raise NotImplementedError('Could not recognise resolution %s' % resolution)

def connect_to_database():
    client = MongoClient('192.168.2.108',
                     username = 'leon',
                     password = mongo_password
    )
    return client

def get_last_update_timestamp(documentType, country_code, client = None):
    if not client:
        client = connect_to_database()
    metadata_db = client['metadata']
    datetimes_collection = metadata_db['datetimes']

    metadata = datetimes_collection.find_one({'documentType': documentType, 'country': country_code})
    datetime = arrow.get(metadata['datetime'])

    return datetime

def get_last_aggregated_timestamp(country_code, client = None):
    if not client:
        client = connect_to_database()
    metadata_db = client['metadata']
    datetimes_collection = metadata_db['datetimes']

    metadata = datetimes_collection.find_one({'aggregated': 'true', 'country': country_code})
    datetime = arrow.get(metadata['datetime'])

    return datetime

def write_to_database(data, database, collection, client=None):
    if not client:
        client = connect_to_database()
    db = client[database]
    collection = db[collection]
    return collection.insert_many(data)

def update_database_metadata(document_type, country_code, new_datetime , client=None):
    if not client:
        client = connect_to_database()
    db = client['metadata']
    collection = db['datetimes']
    collection.update_one({'documentType': document_type, 'country': country_code}, {'$set': {'datetime': str(new_datetime)}}, upsert=True)
    return

def parse_production_by_type(xml_text):
    soup = BeautifulSoup(xml_text, 'html.parser')
    # Get all points
    productions = []
    datetimes = []
    for timeseries in soup.find_all('timeseries'):
        resolution = timeseries.find_all('resolution')[0].contents[0]
        datetime_start = arrow.get(timeseries.find_all('start')[0].contents[0])
        is_production = len(timeseries.find_all('inBiddingZone_Domain.mRID'.lower())) > 0
        psr_type = timeseries.find_all('mktpsrtype')[0].find_all('psrtype')[0].contents[0]

        for entry in timeseries.find_all('point'):
            quantity = float(entry.find_all('quantity')[0].contents[0])
            position = int(entry.find_all('position')[0].contents[0])
            datetime = datetime_from_position(datetime_start, position, resolution)
            try:
                i = datetimes.index(datetime)
                if is_production:
                    productions[i][psr_type] += quantity
                elif psr_type in ENTSOE_STORAGE_PARAMETERS:
                    # Only include consumption if it's for storage. In other cases
                    # it is power plant self-consumption which should be ignored.
                    productions[i][psr_type] -= quantity
            except ValueError:  # Not in list
                datetimes.append(datetime)
                productions.append(defaultdict(lambda: 0))
                productions[-1][psr_type] = quantity if is_production else -1 * quantity
    return productions, datetimes

def parse_aggregated_production(xml_text):
    soup = BeautifulSoup(xml_text, 'html.parser')
    # Get all points
    productions = []
    datetimes = []
    for timeseries in soup.find_all('timeseries'):
        resolution = timeseries.find_all('resolution')[0].contents[0]
        datetime_start = arrow.get(timeseries.find_all('start')[0].contents[0])
        is_production = len(timeseries.find_all('inBiddingZone_Domain.mRID'.lower())) > 0

        for entry in timeseries.find_all('point'):
            quantity = float(entry.find_all('quantity')[0].contents[0])
            position = int(entry.find_all('position')[0].contents[0])
            datetime = datetime_from_position(datetime_start, position, resolution)

            datetimes.append(datetime)
            productions.append(quantity)
    return productions, datetimes

def mkdict_production_by_type(db_params, productions, datetimes):
    dicts = []
    for index,value in enumerate(productions):
        for key in productions[index].keys():
            dict = {
                "documentType": db_params["documentType"],
                "processType": db_params["processType"],
                "psr_type": str(key),
                "time": str(datetimes[index]),
                "quantity": productions[index][key]
            }
            dicts.append(dict)
    return dicts
    
def fetch_production_by_type(country_code, datetime_start, datetime_end, session = None):
    params = {
        'documentType': 'A75',
        'processType': 'A16'
    }
    response = query_entsoe(params, country_code, datetime_start, datetime_end, session = session)
    productions, datetimes = parse_production_by_type(response)
    database_entries = mkdict_production_by_type(params, productions, datetimes)

    return database_entries

def update_production_database(country_code, client=None):
    update_finished = False
    while not update_finished:
        last_datetime = get_last_update_timestamp('A75', country_code, client)
        end_datetime = last_datetime.shift(months=+1)

        if end_datetime > arrow.utcnow():
            end_datetime = end_datetime = arrow.utcnow()
            end_datetime = end_datetime.shift(hours=-1)
            end_datetime = end_datetime.replace(minute=0, second=0, microsecond=0)
            update_finished = True

        if last_datetime != end_datetime:
            production_data_dict = fetch_production_by_type(country_code, last_datetime, end_datetime)
            write_to_database(production_data_dict, country_code, 'generation_by_type', client)
            update_database_metadata('A75', country_code, end_datetime)
    return

def update_all_production(client=None):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(update_production_database, list(ENTSOE_DOMAIN_MAPPINGS.keys()))
    # for country in list(ENTSOE_DOMAIN_MAPPINGS.keys()):
    #     update_production_database(country)
    return

def get_accumulated_production(start_datetime, end_datetime, country_code, psr_type, client=None):
    documentType = 'A75'
    production = 0
    if not client:
        client = connect_to_database()
    db = client[country_code]
    collection = db['generation_by_type']

    result = collection.find({'time': {'$gt': str(start_datetime), '$lt': str(end_datetime)}, 'psr_type': psr_type})
    
    quantities = list()
    for entry in result:
        quantities.append(entry['quantity'])

    try:
        production = sum(quantities) / len(quantities)
    except ZeroDivisionError:
        return 0

    return production

def write_percentage_to_database(country_code, datetime, renewable_percentage, fossile_percentage, client=None):
    if not client:
        client = connect_to_database()
    db = client[country_code]
    collection = db['renewable_percentage']
    data = {
        'time': str(datetime),
        'renewable_percentage': renewable_percentage,
        'fossile_percentage': fossile_percentage
    }
    return collection.insert_one(data)

def update_percentage_metadata(country_code, new_datetime , client=None):
    if not client:
        client = connect_to_database()
    db = client['metadata']
    collection = db['datetimes']
    collection.update_one({'aggregated': 'true', 'country': country_code}, {'$set': {'datetime': str(new_datetime)}}, upsert=True)
    return

def update_aggregated_production(country_code, client=None):
    update_finished = False
    while not update_finished:
        last_datetime = get_last_aggregated_timestamp(country_code, client)
        end_datetime = last_datetime.shift(days=+1)

        if end_datetime > arrow.utcnow():
            end_datetime = last_datetime
            update_finished = True
            break

        renewable_production = list()
        fossile_production = list()

        if last_datetime != end_datetime:
            for psr_type in ENTSOE_RENEWABLE:
                renewable_production.append(get_accumulated_production(last_datetime, end_datetime, country_code, psr_type))
            for psr_type in ENTSOE_NON_RENEWABLE:
                fossile_production.append(get_accumulated_production(last_datetime, end_datetime, country_code, psr_type))

        renewable_percentage = (sum(renewable_production) / (sum(renewable_production) + sum(fossile_production))) * 100
        fossile_percentage = 100 - renewable_percentage

        write_percentage_to_database(country_code, last_datetime, renewable_percentage, fossile_percentage)
        update_percentage_metadata(country_code, end_datetime)

def update_all_percentage(client=None):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(update_aggregated_production, list(ENTSOE_DOMAIN_MAPPINGS.keys()))
    return

def  get_renewable_forecast(country_code, client=None):
    params = {
        'documentType': 'A69',
        'processType': 'A01'
    }

    start_datetime = arrow.utcnow()
    start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    
    end_datetime = start_datetime.shift(days=+1)
    productions, datetimes = parse_production_by_type(response)

    response = query_entsoe(params, country_code, start_datetime, end_datetime, session = session)

