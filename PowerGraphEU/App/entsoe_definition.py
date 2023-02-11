"""Provides definitions for the ENTSOE API"""

import itertools

ENTSOE_ENDPOINT = 'https://transparency.entsoe.eu/api'
ENTSOE_SECURITY_TOKEN = 'securityToken=d1709944-31ba-49c8-8293-f6d751d333e5'
ENTSOE_PARAMETER_DESC = {
    'B01': 'Biomass',
    'B02': 'Fossil Brown coal/Lignite',
    'B03': 'Fossil Coal-derived gas',
    'B04': 'Fossil Gas',
    'B05': 'Fossil Hard coal',
    'B06': 'Fossil Oil',
    'B07': 'Fossil Oil shale',
    'B08': 'Fossil Peat',
    'B09': 'Geothermal',
    'B10': 'Hydro Pumped Storage',
    'B11': 'Hydro Run-of-river and poundage',
    'B12': 'Hydro Water Reservoir',
    'B13': 'Marine',
    'B14': 'Nuclear',
    'B15': 'Other renewable',
    'B16': 'Solar',
    'B17': 'Waste',
    'B18': 'Wind Offshore',
    'B19': 'Wind Onshore',
    'B20': 'Other',
}
ENTSOE_PARAMETER_BY_DESC = {v: k for k, v in ENTSOE_PARAMETER_DESC.items()}
ENTSOE_PARAMETER_GROUPS = {
    'production': {
        'biomass': ['B01', 'B17'],
        'coal': ['B02', 'B05', 'B07', 'B08'],
        'gas': ['B03', 'B04'],
        'geothermal': ['B09'],
        'hydro': ['B11', 'B12'],
        'nuclear': ['B14'],
        'oil': ['B06'],
        'solar': ['B16'],
        'wind': ['B18', 'B19'],
        'unknown': ['B20', 'B13', 'B15']
    },
    'storage': {
        'hydro storage': ['B10']
    }
}
ENTSOE_PARAMETER_BY_GROUP = {v: k for k, g in ENTSOE_PARAMETER_GROUPS.items() for v in g}
# Get all the individual storage parameters in one list
ENTSOE_STORAGE_PARAMETERS = list(itertools.chain.from_iterable(
    ENTSOE_PARAMETER_GROUPS['storage'].values()))

ENTSOE_RENEWABLE_GROUPS = {
    'renewable': {
        'biomass': ['B01', 'B17'],
        'geothermal': ['B09'],
        'hydro': ['B11', 'B12'],
        'solar': ['B16'],
        'wind': ['B18', 'B19']
    },
    'non_renewable': {
        'coal': ['B02', 'B05', 'B07', 'B08'],
        'gas': ['B03', 'B04'],
        'nuclear': ['B14'],
        'oil': ['B06'],
        'unknown': ['B20', 'B13', 'B15'],
        'hydro storage': ['B10']
    }
}

ENTSOE_RENEWABLE_BY_GROUP = {v: k for k, g in ENTSOE_RENEWABLE_GROUPS.items() for v in g}
ENTSOE_RENEWABLE = list(itertools.chain.from_iterable(
    ENTSOE_RENEWABLE_GROUPS['renewable'].values()))
ENTSOE_NON_RENEWABLE = list(itertools.chain.from_iterable(
    ENTSOE_RENEWABLE_GROUPS['non_renewable'].values()))

ENTSOE_DOMAIN_MAPPINGS = {
    'AT': '10YAT-APG------L',   #austria
    'BE': '10YBE----------2',   #belgium
    'CH': '10YCH-SWISSGRIDZ',   #switzerland
    'CZ': '10YCZ-CEPS-----N',   #czech republic
    'DE': '10Y1001A1001A83F',   #germany
    'DK': '10Y1001A1001A65H',   #denmark
    'FR': '10YFR-RTE------C',   #france
    'GR': '10YGR-HTSO-----Y',   #greece
    'HR': '10YHR-HEP------M',   #croatia
    'HU': '10YHU-MAVIR----U',   #hungary
    'LU': '10YLU-CEGEDEL-NQ',   #luxembourg
    'NL': '10YNL----------L',   #netherlands
    'PL': '10YPL-AREA-----S',   #poland
    'PT': '10YPT-REN------W',   #portugal
}
