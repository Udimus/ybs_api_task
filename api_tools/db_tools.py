"""
Tools to put and get data from DB.
"""
import psycopg2


DB_CREDENTIALS = {
    'dbname': 'api_db',
    'user': 'api',
    'host': 'db',
    'password': 'password',
}
GET_TABLES_SQL = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
"""
CREATE_TABLE_SQL = """
    CREATE TABLE %s (
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
INSERT_INTO_SQL = 'INSERT INTO %s VALUES %s;'


def tables_number_at_db(cur):
    cur.execute(GET_TABLES_SQL)
    return len(cur.fetchall())


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


def prepare_citizen_data(citizen_data):
    return [citizen_data[field] for field in FIELD_NAMES]


def save_new_import(citizens):
    with psycopg2.connect(**DB_CREDENTIALS) as conn:
        with conn.cursor() as cur:
            import_id = tables_number_at_db(cur)
            cur.execute(CREATE_TABLE_SQL, (import_id,))
            citizens_str_data = [cur.mogrify(INSERT_DATA_PATTERN,
                                             prepare_citizen_data(citizen_data))
                                 for citizen_data in citizens]
            data_to_insert = ','.join(citizens_str_data)
            cur.execute(INSERT_INTO_SQL, (import_id, data_to_insert))
            conn.commit()
    import_id = 0
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
