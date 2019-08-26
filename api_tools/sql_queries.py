SET_TIMEZONE_SQL = "SET timezone TO 'GMT';"
GET_TABLES_SQL = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
"""
CREATE_TYPE_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type')
    THEN
        CREATE TYPE gender_type AS ENUM ('male', 'female');
    END IF;
END $$;
"""
CREATE_TABLE_SQL = """
CREATE TABLE import_{import_id} (
    citizen_id integer PRIMARY KEY,
    town varchar(256),
    street varchar(256),
    building varchar(256),
    apartment integer,
    name varchar(256),
    birth_date date,
    gender gender_type,
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
INSERT_INTO_SQL = 'INSERT INTO import_{import_id} VALUES '
CHECK_IF_TABLE_EXISTS_SQL = """
SELECT to_regclass('public.import_{import_id}');
"""
CHECK_IF_CITIZEN_EXISTS_SQL = """
SELECT EXISTS (
    SELECT 1
    FROM import_{import_id}
    WHERE citizen_id={citizen_id}
)
"""
GET_FULL_TABLE_SQL = (
    "SELECT "
    + ",\n".join(FIELD_NAMES)
    + " FROM import_{import_id}"
).replace("birth_date",
          "to_char(birth_date, 'DD.MM.YYYY') as birth_date")
UPDATE_SQL = """
UPDATE import_{import_id}
SET {fields}
WHERE citizen_id={citizen_id}
"""
GET_RELATIVES_SQL = """
SELECT relatives
FROM import_{import_id}
WHERE citizen_id = {citizen_id}
"""
GET_CITIZEN_SQL = GET_FULL_TABLE_SQL + "\nWHERE citizen_id={citizen_id}"
GET_BIRTHDAYS_SQL = """
WITH birth_dates as (
        SELECT
        citizen_id,
        date_part('month', birth_date) as birth_month
        FROM import_{import_id}
        ),
    relatives as (
        SELECT
        citizen_id,
        unnest(relatives) as relative_id
        FROM import_{import_id}
        )
SELECT
    birth_month,
    citizen_id,
    SUM(counter) as presents
FROM (
    SELECT
    relatives.citizen_id as citizen_id,
    birth_dates.birth_month as birth_month,
    1 as counter
    FROM relatives
    INNER JOIN birth_dates
    ON (relatives.relative_id = birth_dates.citizen_id)
    ) as ungrouped_data
GROUP BY citizen_id, birth_month
ORDER BY birth_month, citizen_id
"""
GET_AGES_SQL = """
SELECT
town,
round(p50::numeric, 2) as p50,
round(p75::numeric, 2) as p75,
round(p99::numeric, 2) as p99
FROM (
    SELECT
    town,
    percentile_cont(0.5) within GROUP (order by age) as p50,
    percentile_cont(0.75) within GROUP (order by age) as p75,
    percentile_cont(0.99) within GROUP (order by age) as p99
    FROM (
        SELECT
        EXTRACT (YEAR FROM age(birth_date)) as age,
        town
        FROM import_{import_id}
        ) as towns_ages
    GROUP BY town
    ) as towns_stat
"""