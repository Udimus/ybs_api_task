"""
Tools to put and get data from DB.
"""
import re
from collections import defaultdict

import psycopg2
from flask import current_app as app

from api_tools.check_data import (
    DATE_FORMAT,
    str_to_date,
    date_to_str,
)
from api_tools.sql_queries import (
    SET_TIMEZONE_SQL,
    GET_TABLES_SQL,
    CREATE_TYPE_SQL,
    CREATE_TABLE_SQL,
    INSERT_DATA_PATTERN,
    FIELD_NAMES,
    INSERT_INTO_SQL,
    CHECK_IF_TABLE_EXISTS_SQL,
    CHECK_IF_CITIZEN_EXISTS_SQL,
    GET_FULL_TABLE_SQL,
    UPDATE_SQL,
    GET_RELATIVES_SQL,
    GET_CITIZEN_SQL,
    GET_BIRTHDAYS_SQL,
    GET_AGES_SQL,
)

DB_CREDENTIALS = {
    'dbname': 'api_db',
    'user': 'api',
    'host': 'db',
}
TABLE_NAME_PATTERN = 'import_(\\d+)'
POSTGRES_DATE_FORMAT = '%Y-%m-%d'


def get_new_table_id(cur):
    """
    For new import create new unique import id.
    """
    cur.execute(GET_TABLES_SQL)
    table_ids = [int(re.match(TABLE_NAME_PATTERN, table[0])[1])
                 for table in cur.fetchall()
                 if re.match(TABLE_NAME_PATTERN, table[0]) is not None]
    if len(table_ids) == 0:
        return 0
    return max(table_ids) + 1


def accurate_rounding(number, precision):
    multiplier = 10 ** precision
    return int(number * multiplier) / multiplier


def convert_date_string(date_string,
                        input_format=DATE_FORMAT,
                        output_format=POSTGRES_DATE_FORMAT):
    date = str_to_date(date_string, input_format)
    return date_to_str(date, output_format)


def check_import_exists(import_id, cur):
    """
    Does import with this id really exist?
    """
    sql = CHECK_IF_TABLE_EXISTS_SQL.format(import_id=import_id)
    cur.execute(sql)
    result = cur.fetchall()[0][0]
    app.logger.debug('to_regclass() output for import %d: %s',
                     import_id,
                     result)
    if result is None:
        raise ValueError('There is no import {}'
                         .format(import_id))


def check_citizen_exists(import_id, citizen_id, cur):
    """
    Does citizen_id in this import_id really exist?
    """
    sql = CHECK_IF_CITIZEN_EXISTS_SQL.format(import_id=import_id,
                                             citizen_id=citizen_id)
    cur.execute(sql)
    result = cur.fetchall()[0][0]
    app.logger.debug('Is citizen %d in import %d: %s',
                     citizen_id,
                     import_id,
                     result)
    if not result:
        raise ValueError('There is no citizen {} in import {}'
                         .format(citizen_id, import_id))


def check_citizen_relatives_exist(import_id, citizen_update, cur):
    """
    Does realtives of this citizen really exist?
    """
    if 'relatives' in citizen_update:
        for relative_id in citizen_update['relatives']:
            check_citizen_exists(import_id, relative_id, cur)


def citizen_data_to_string(citizen_data, cur):
    """
    Convert citizen data to table insert format.
    """
    data = []
    for field in FIELD_NAMES:
        value = citizen_data[field]
        if field == 'birth_date':
            value = convert_date_string(value)
        data.append(value)
    return (cur
            .mogrify(INSERT_DATA_PATTERN, tuple(data))
            .decode('utf-8'))


def tuple_to_citizen_data(citizen_tuple):
    """
    Convert DB answer to dict.
    """
    return {field: value for field, value
            in zip(FIELD_NAMES, citizen_tuple)}


def prepare_update_info_sql(
        import_id,
        citizen_id,
        citizen_update_data,
        cur):
    """
    Prepare query, which updates data for given citizen.
    """
    fields = []
    for field, value in citizen_update_data.items():
        if field == 'birth_date':
            value = convert_date_string(value)
        field_update_string = field + ' = %s'
        fields.append(cur
                      .mogrify(field_update_string, (value,))
                      .decode('utf-8'))
    fields = ",\n".join(fields)
    return UPDATE_SQL.format(import_id=import_id,
                             fields=fields,
                             citizen_id=citizen_id)


def get_current_relatives(
        import_id,
        citizen_id,
        cur):
    """
    Load list if current relatives of given citizen.
    """
    cur.execute(GET_RELATIVES_SQL.format(import_id=import_id,
                                         citizen_id=citizen_id))
    return cur.fetchall()[0][0]


def remove_relative(
        import_id,
        citizen_id,
        relative_id,
        cur):
    """
    Remove relative from this citizen's relatives.
    """
    app.logger.debug('Removing %d from %d relatives...',
                     relative_id,
                     citizen_id)
    current_relatives = get_current_relatives(import_id, citizen_id, cur)
    new_relatives = []
    for relative in current_relatives:
        if relative != relative_id:
            new_relatives.append(relative)
    app.logger.debug('%d new relatives: %s',
                     citizen_id,
                     new_relatives)
    update_data = {'relatives': new_relatives}
    sql = prepare_update_info_sql(
        import_id,
        citizen_id,
        update_data,
        cur)
    cur.execute(sql)


def add_relative(
        import_id,
        citizen_id,
        relative_id,
        cur):
    """
    Add relative to this citizen's realtives.
    """
    app.logger.debug('Adding %d to %d relatives...',
                     relative_id,
                     citizen_id)
    new_relatives = get_current_relatives(import_id, citizen_id, cur)
    new_relatives.append(relative_id)
    app.logger.debug('%d new relatives: %s',
                     citizen_id,
                     new_relatives)
    update_data = {'relatives': new_relatives}
    sql = prepare_update_info_sql(
        import_id,
        citizen_id,
        update_data,
        cur)
    cur.execute(sql)


def prepare_birthday_stat(import_id, cur):
    """
    Load from database and convert to answer format birthdays presents stat.
    """
    data = defaultdict(list)
    cur.execute(GET_BIRTHDAYS_SQL.format(import_id=import_id))
    for row in cur.fetchall():
        citizen_dict = {
            'citizen_id': row[1],
            'presents': row[2],
        }
        data[str(int(row[0]))].append(citizen_dict)
    return data


def prepare_ages_stat(import_id, cur):
    """
    Load from database and convert to answer format ages stat.
    """
    data = []
    cur.execute(GET_AGES_SQL.format(import_id=import_id))
    for row in cur.fetchall():
        town_dict = {
            'town': row[0],
            'p50': float(row[1]),
            'p75': float(row[2]),
            'p99': float(row[3]),
        }
        app.logger.debug('Town ages stat dict: {}'.format(town_dict))
        data.append(town_dict)
    return data


def save_new_import(citizens):
    """
    Create table, save there data, return table id.
    """
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            app.logger.debug('DB cursor is ready...')
            cur.execute(SET_TIMEZONE_SQL)
            app.logger.debug('Set GMT as timezone.')
            cur.execute(CREATE_TYPE_SQL)
            app.logger.debug('Create gender type.')

            import_id = get_new_table_id(cur)
            app.logger.debug('New import id is %d', import_id)
            cur.execute(CREATE_TABLE_SQL.format(import_id=import_id))
            app.logger.debug('Table \'import_%d\' has been created.', import_id)

            citizens_str_data = [citizen_data_to_string(citizen_data, cur)
                                 for citizen_data in citizens]
            app.logger.debug('There are %d rows to insert.',
                             len(citizens_str_data))
            data_to_insert = ','.join(citizens_str_data)

            app.logger.debug('Data inserting...')
            cur.execute(INSERT_INTO_SQL.format(import_id=import_id)
                        + data_to_insert)
            app.logger.debug('Success!')
            conn.commit()
            return {"import_id": import_id}


def update_import(import_id,
                  citizen_id,
                  citizen_update):
    """
    Update citizen data at the table(import).
    """
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            app.logger.debug('DB cursor is ready...')
            cur.execute(SET_TIMEZONE_SQL)
            app.logger.debug('Set GMT as timezone.')

            app.logger.debug('If there is import %d...',
                             import_id)
            check_import_exists(import_id, cur)
            app.logger.debug('If there is citizen %d...',
                             citizen_id)
            check_citizen_exists(import_id, citizen_id, cur)
            app.logger.debug('If his new relatives list is correct...',
                             citizen_id)
            check_citizen_relatives_exist(import_id, citizen_update, cur)

            if 'relatives' in citizen_update:
                new_relatives = citizen_update['relatives']
                app.logger.debug('New relatives: %s', new_relatives)
                current_relatives = get_current_relatives(import_id,
                                                          citizen_id,
                                                          cur)
                app.logger.debug('Old relatives: %s', current_relatives)
                ex_relatives = list(set(current_relatives)
                                    - set(new_relatives))
                new_relatives = list(set(new_relatives)
                                     - set(current_relatives))
                for relative_id in ex_relatives:
                    remove_relative(
                        import_id=import_id,
                        relative_id=citizen_id,
                        citizen_id=relative_id,
                        cur=cur)
                for relative_id in new_relatives:
                    add_relative(
                        import_id=import_id,
                        relative_id=citizen_id,
                        citizen_id=relative_id,
                        cur=cur)

            update_sql = prepare_update_info_sql(
                import_id,
                citizen_id,
                citizen_update,
                cur)
            cur.execute(update_sql)
            citizen_sql = GET_CITIZEN_SQL.format(import_id=import_id,
                                                 citizen_id=citizen_id)
            cur.execute(citizen_sql)
            citizen_tuple = cur.fetchall()[0]
            citizen_data = tuple_to_citizen_data(citizen_tuple)
            return citizen_data


def load_import(import_id):
    """
    Load citizens data from given table(import).
    """
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            app.logger.debug('DB cursor is ready...')
            cur.execute(SET_TIMEZONE_SQL)
            app.logger.debug('Set GMT as timezone.')
            app.logger.debug('If there is import %d...',
                             import_id)
            check_import_exists(import_id, cur)

            sql = GET_FULL_TABLE_SQL.format(import_id=import_id)
            cur.execute(sql)
            result = cur.fetchall()
            app.logger.debug('There is %d rows at import %d.',
                             len(result),
                             import_id)
            citizens = [tuple_to_citizen_data(citizen_tuple)
                        for citizen_tuple in result]
            return citizens


def calculate_birthdays(import_id):
    """
    Calculate birthdays presents stat.
    """
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            app.logger.debug('DB cursor is ready...')
            cur.execute(SET_TIMEZONE_SQL)
            app.logger.debug('Set GMT as timezone.')
            app.logger.debug('If there is import %d...',
                             import_id)
            check_import_exists(import_id, cur)

            app.logger.debug('Birthdays stat preparing...')
            birthdays_stat = prepare_birthday_stat(import_id, cur)
            return birthdays_stat


def calculate_ages_stat(import_id):
    """
    Calculate towns ages percentiles.
    """
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            app.logger.debug('DB cursor is ready...')
            cur.execute(SET_TIMEZONE_SQL)
            app.logger.debug('Set GMT as timezone.')
            app.logger.debug('If there is import %d...',
                             import_id)
            check_import_exists(import_id, cur)

            app.logger.debug('Ages stat preparing...')
            ages_stat = prepare_ages_stat(import_id, cur)
            return ages_stat
