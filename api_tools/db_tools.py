"""
Tools to put and get data from DB.
"""
import re

import psycopg2
from flask import current_app as app


DB_CREDENTIALS = {
    'dbname': 'api_db',
    'user': 'api',
    'host': 'db',
}
GET_TABLES_SQL = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
"""
CREATE_TABLE_SQL = """
    CREATE TABLE import_{} (
        citizen_id integer PRIMARY KEY,
        town varchar(256),
        street varchar(256),
        building varchar(256),
        apartment integer,
        name varchar(256),
        birth_date varchar(10),
        gender varchar(10),
        relatives integer[]
    );
"""
INSERT_DATA_PATTERN = '({})'.format(','.join(['%s' for _ in range(9)]))
FIELD_NAMES = [
    'citizen_id',
    'town',
    'street',
    'building',
    'apartment',
    'name',
    'birth_date',
    'gender',
    'relatives',
]
INSERT_INTO_SQL = 'INSERT INTO import_{} VALUES '
TABLE_NAME_PATTERN = 'import_(\\d+)'


def get_new_table_id(cur):
    cur.execute(GET_TABLES_SQL)
    table_ids = [int(re.match(TABLE_NAME_PATTERN, table[0])[1])
                 for table in cur.fetchall()
                 if re.match(TABLE_NAME_PATTERN, table[0]) is not None]
    return max(table_ids) + 1


def check_import_exists(import_id, cur):
    """
    Does import with this id really exist?
    """


def check_citizen_exists(import_id, citizen_id):
    """
    Does citizen_id in this import_id really exist?
    """
    pass


def check_citizen_relatives_exist(import_id, citizen_id):
    """
    Does realtives of this citizen really exist?
    """
    pass


def prepare_citizen_data(citizen_data, cur):
    data_as_tuple = tuple(citizen_data[field]
                          for field in FIELD_NAMES)
    return (cur
            .mogrify(INSERT_DATA_PATTERN, data_as_tuple)
            .decode('utf-8'))


def save_new_import(citizens):
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            app.logger.debug('DB cursor is ready...')
            import_id = get_new_table_id(cur)
            app.logger.debug('New import id is %d', import_id)
            cur.execute(CREATE_TABLE_SQL.format(import_id))
            app.logger.debug('Table import_%d is created', import_id)
            citizens_str_data = [prepare_citizen_data(citizen_data, cur)
                                 for citizen_data in citizens]
            app.logger.debug('There is %d rows to insert.',
                             len(citizens_str_data))
            data_to_insert = ','.join(citizens_str_data)

            app.logger.debug('Data inserting...')
            cur.execute(INSERT_INTO_SQL.format(import_id) + data_to_insert)
            app.logger.debug('Success!')
            conn.commit()
    return {"import_id": import_id}


def update_import(import_id,
                  citizen_id,
                  citizen_update):
    citizen_data = citizen_update
    return citizen_data


def load_import(import_id):
    citizens = []
    return citizens


def calculate_birthdays(import_id):
    birthdays_stat = {}
    return birthdays_stat


def calculate_ages_stat(import_id):
    ages_stat = {}
    return ages_stat
