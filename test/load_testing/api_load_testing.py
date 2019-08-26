#!/usr/bin/env python3
"""
Load testing of our service.
"""
import sys
import os
import subprocess
import random
import logging
import json
import argparse
from copy import deepcopy
from datetime import datetime
from argparse import RawTextHelpFormatter

from api_tools.check_data import DATE_FORMAT
import requests

MIN_DATE = '01.01.1920'
MAX_DATE = '01.01.2019'
MIN_TS = datetime.strptime(MIN_DATE, DATE_FORMAT).timestamp()
MAX_TS = datetime.strptime(MAX_DATE, DATE_FORMAT).timestamp()
TEST_JSON = 'test/test_data/import_large_data.json'
IMPORT_PATH = '/imports'
GET_CITIZENS_PATH = '/imports/{import_id}/citizens'
GET_BIRTHDAYS_PATH = '/imports/{import_id}/citizens/birthdays'
GET_AGES_PATH = '/imports/{import_id}/towns/stat/percentile/age'

logger = logging.getLogger(__name__)


def get_towns(towns_number=20):
    return ['town_' + str(i) for i in range(towns_number)]


def get_random_birth_date():
    random_ts = random.randrange(MIN_TS, MAX_TS)
    random_dt = datetime.fromtimestamp(random_ts)
    return random_dt.strftime(DATE_FORMAT)


def generate_pair(citizen_number):
    first = random.randrange(citizen_number)
    second = random.randrange(citizen_number)
    return first, second


def remove_test_file(filename=TEST_JSON):
    try:
        os.remove(filename)
    except OSError:
        pass


def create_test_import(citizen_number=10000,
                       pairs_number=1000,
                       towns_number=20):
    towns = get_towns(towns_number)
    base_dict = {
        'name': 'Аркадий',
        'street': 'Тимура Фрунзе',
        'building': 'Мамонтов',
        'apartment': 1,
        'gender': 'male',
    }
    random.seed(42)
    citizens = []
    for citizen_id in range(citizen_number):
        citizen = deepcopy(base_dict)
        citizen['citizen_id'] = citizen_id
        citizen['birth_date'] = get_random_birth_date()
        citizen['town'] = random.choice(towns)
        citizen['relatives'] = []
        citizens.append(citizen)
    for _ in range(pairs_number):
        pair = generate_pair(citizen_number)
        if (pair[0] not in citizens[pair[1]]['relatives']
                and pair[1] not in  citizens[pair[0]]['relatives']):
                if pair[0] != pair[1]:
                    citizens[pair[1]]['relatives'].append(pair[0])
                    citizens[pair[0]]['relatives'].append(pair[1])
                else:
                    citizens[pair[1]]['relatives'].append(pair[0])
    return {'citizens': citizens}



def main():
    argparser = argparse.ArgumentParser(description=__doc__,
                                        formatter_class=RawTextHelpFormatter)
    argparser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        type=str,
        default=logging.INFO,
        choices=[
           "CRITICAL",
           "ERROR",
           "WARNING",
           "INFO",
           "DEBUG",
           "NOTSET",
        ],
        help='Set output verbosity level.')
    argparser.add_argument(
        "-n",
        "--citizens",
        type=int,
        default=10000
    )
    argparser.add_argument(
        "-p",
        "--pairs",
        type=int,
        default=1000,
        help='Relationships number.'
    )
    argparser.add_argument(
        "-t",
        "--towns",
        type=int,
        default=20
    )
    argparser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=100,
        help='Number of multiple requests to make at a time'
    )
    argparser.add_argument(
        "-r",
        "--requests",
        type=int,
        default=1000,
        help='Number of requests to perform'
    )
    argparser.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help='Address to test.'
    )

    args = argparser.parse_args()
    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s %(levelname)s:%(module)s %(message)s')

    logger.info('Preparing test data...')
    test_import_data = create_test_import(
        citizen_number=args.citizens,
        pairs_number=args.pairs,
        towns_number=args.towns,
    )
    import_url = args.address + IMPORT_PATH
    logger.info('Post data to {}'.format(import_url))
    response = requests.post(import_url, json=test_import_data)
    if response.status_code != 201:
        logger.warning('Import failed with message: {}'
                       .format(response.text))
        return 1
    import_id = response.json()['data']['import_id']
    logger.info('Test data is successfully imported with id={}.'
                .format(import_id))

    logger.info('Test getting full table from DB.')
    get_full_url = (args.address
                    + GET_CITIZENS_PATH.format(import_id=import_id))
    subprocess.call(["ab",
                    '-c',
                     str(args.concurrency),
                     '-n',
                     str(args.requests),
                     get_full_url
                     ])

    logger.info('Test getting birthdays from DB.')
    get_birthdays_url = (args.address
                     + GET_BIRTHDAYS_PATH.format(import_id=import_id))
    subprocess.call(["ab",
                    '-c',
                     str(args.concurrency),
                     '-n',
                     str(args.requests),
                     get_birthdays_url
                     ])

    logger.info('Test getting ages from DB.')
    get_ages_url = (args.address
                     + GET_AGES_PATH.format(import_id=import_id))
    subprocess.call(["ab",
                    '-c',
                     str(args.concurrency),
                     '-n',
                     str(args.requests),
                     get_ages_url
                     ])



if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logger.critical(err, exc_info=True)
        sys.exit(1)


