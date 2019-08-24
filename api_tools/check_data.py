"""
Check, if citizens data is correct.
"""
import re
from datetime import datetime, timezone
from collections import Counter


DATE_FORMAT = '%d.%m.%Y'
FIELDS = {
    'citizen_id': {
        'type': int,
    },
    'town': {
        'type': str,
        'max_length': 256,
        'pattern': '\\w+'
    },
    'street': {
        'type': str,
        'max_length': 256,
        'pattern': '\\w+'
    },
    'building': {
        'type': str,
        'max_length': 256,
        'pattern': '\\w+'
    },
    'apartment': {
        'type': int,
    },
    'name': {
        'type': str,
        'max_length': 256,
        'pattern': '.+'
    },
    'birth_date': {
        'type': str,
    },
    'gender': {
        'type': str,
    },
    'relatives': {
        'type': list,
    },
}
POSSIBLE_GENDERS = ['male', 'female']


def get_today():
    return datetime.now(timezone.utc).date()


def str_to_date(date_string):
    return datetime.strptime(date_string, DATE_FORMAT).date()


def date_to_str(date):
    return datetime.strftime(date, DATE_FORMAT)


def check_gender(citizen_data):
    gender = citizen_data['gender']
    if gender not in POSSIBLE_GENDERS:
        raise ValueError("{} isn't correct gender, we are in Russia."
                         .format(gender))


def check_birth_date(citizen_data):
    today = get_today()
    birthday = str_to_date(citizen_data['birth_date'])
    if today <= birthday:
        raise ValueError("{} isn't correct birth date."
                         .format(citizen_data['birth_date']))


def check_relatives(citizen_data):
    # Here we just check, if it is list of ids.
    # Later we should check,
    # if they are correct and commutative.
    for citizen_id in citizen_data['relatives']:
        if (type(citizen_id) is not int
                or citizen_id < 0):
            raise ValueError("List of relatives shouldn't contain {}."
                             .format(citizen_id))


def check_citizen_fields(citizen_data):
    for field, value in citizen_data.items():
        if type(value) != FIELDS[field]['type']:
            raise ValueError("{} isn't correct value for the {}."
                             .format(value, field))
        if type(value) is int and value < 0:
            raise ValueError("{} isn't correct value for the {}."
                             .format(value, field))
        max_length = FIELDS[field].get('max_length')
        if (max_length is not None
                and len(value) > max_length):
            raise ValueError("{} is too long value for the {}."
                             .format(value, field))
        pattern = FIELDS[field].get('pattern')
        if (pattern is not None
                and re.search(pattern, value) is None):
            raise ValueError("{} isn't correct value for the {}."
                             .format(value, field))
    if 'birth_date' in citizen_data:
        check_birth_date(citizen_data)
    if 'gender' in citizen_data:
        check_gender(citizen_data)
    if 'relatives' in citizen_data:
        check_relatives(citizen_data)


def check_init_citizen(citizen_data):
    if type(citizen_data) is not dict:
        raise ValueError("Citizen info should be dictionary.")
    # If there are unexpected or missed fields.
    if set(FIELDS) != set(citizen_data):
        missed_fields = set(FIELDS) - set(citizen_data)
        unexpected_fields = set(citizen_data) - set(FIELDS)
        error_messages = []
        if missed_fields:
            error_messages.append('{} fields are missed'
                                  .format(missed_fields))
        if unexpected_fields:
            error_messages.append('{} fields are unexpected'
                                  .format(unexpected_fields))
        error_message = ", ".join(error_messages) + '.'
        raise ValueError(error_message)
    # Check data types and correctness.
    check_citizen_fields(citizen_data)


def check_update_citizen(citizen_data):
    if type(citizen_data) is not dict:
        raise ValueError("Citizen info should be dictionary.")
    # If there unexpected fields
    unexpected_fields = set(citizen_data) - set(FIELDS)
    if unexpected_fields:
        raise ValueError('{} fields are unexpected.'
                         .format(unexpected_fields))
    if 'citizen_id' in citizen_data:
        raise ValueError('You can\'t update \'citizen_id\'.')
    check_citizen_fields(citizen_data)
    # Later we should check, if relatives update is correct.


def check_citizens_group(citizens_group):
    if type(citizens_group) is not list:
        raise ValueError("Citizens data should be list.")

    # Check every citizen's data.
    for citizen in citizens_group:
        check_init_citizen(citizen)

    # Check correct relationships.
    citizens = [citizen['citizen_id'] for citizen in citizens_group]
    uniq_citizens = list(set(citizens))

    pairs_counter = Counter()
    if len(uniq_citizens) != len(citizens):
        raise ValueError('There are not unique citizen ids.')
    for citizen in citizens_group:
        relatives = citizen['relatives']
        uniq_relatives = list(set(relatives))
        if len(uniq_relatives) != len(relatives):
            raise ValueError('{} has not unique citizen ids.')
        citizen_id = citizen['citizen_id']
        for relative_id in relatives:
            incoming_edge = (relative_id, citizen_id)
            outgoing_edge = (citizen_id, relative_id)
            pairs_counter[outgoing_edge] += 1
            pairs_counter[incoming_edge] -= 1
            for edge in [incoming_edge, outgoing_edge]:
                if pairs_counter[edge] == 0:
                    del pairs_counter[edge]
    if len(pairs_counter) > 0:
        for pair in pairs_counter:
            raise ValueError('There is something wrong with {} relatives.'
                             .format(pair[0]))
