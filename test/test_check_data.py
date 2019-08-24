"""
Tests for api_tools/check_data.py
"""
import json
from copy import deepcopy

import pytest
from api_tools.check_data import (
    check_gender,
    check_birth_date,
    check_relatives,
    check_citizen_fields,
    check_init_citizen,
    check_update_citizen,
    check_citizens_group,
)

DATA_PATH = 'test/test_data/import_data.json'
GENDER_TEST = [
    ('male', True),
    ('female', True),
    ('smth_else', False),
]
BIRTH_DATE_TEST = [
    ('31.02.2019', False),
    ('01.02.3019', False),
    ('01.02.2019', True),
    ('1.2.2019', True),
    ('don\'t remember', False),
    ('2019.01.02', False),
    ('01/02/2019', False),
    ('12.31.2010', False),
    ('01.01.1900', True),
    ('', False),
]
RELATIVES_TEST = [
    ([1, 2, 3], True),
    ([1], True),
    ([], True),
    ([1, 1], True),
    ([1, '4'], False),
    (['1'], False),
    ([[]], False),
]


def load_data(data_path=DATA_PATH):
    with open(data_path, 'r') as file_object:
        return json.load(file_object)


@pytest.mark.parametrize('gender,is_correct', GENDER_TEST)
def test_check_gender(gender, is_correct):
    test_data = {'gender': gender}
    if is_correct:
        check_gender(test_data)
    else:
        with pytest.raises(ValueError):
            check_gender(test_data)


@pytest.mark.parametrize('birth_date,is_correct', BIRTH_DATE_TEST)
def test_check_birth_date(birth_date, is_correct):
    test_data = {'birth_date': birth_date}
    if is_correct:
        check_birth_date(test_data)
    else:
        with pytest.raises(ValueError):
            check_birth_date(test_data)


@pytest.mark.parametrize('relatives,is_correct', RELATIVES_TEST)
def test_check_relatives(relatives, is_correct):
    test_data = {'relatives': relatives}
    if is_correct:
        check_relatives(test_data)
    else:
        with pytest.raises(ValueError):
            check_relatives(test_data)


def prepare_fields_test():
    data = load_data()
    citizen_fields_test = []

    # Correct samples.
    for citizen in data:
        citizen_fields_test.append((citizen, True))
    correct_citizen = data[0]

    for field in correct_citizen:
        value = correct_citizen[field]
        if type(value) is int:

            # Wrong type.
            citizen = deepcopy(correct_citizen)
            citizen[field] = 'value'
            citizen_fields_test.append((citizen, False))

            # Wrong value.
            citizen = deepcopy(correct_citizen)
            citizen[field] = -1
            citizen_fields_test.append((citizen, False))

            # Correct value.
            citizen = deepcopy(correct_citizen)
            citizen[field] = 1
            citizen_fields_test.append((citizen, True))
        if type(value) is str:

            # Wrong type.
            citizen = deepcopy(correct_citizen)
            citizen[field] = 1
            citizen_fields_test.append((citizen, False))

            # Wrong value.
            citizen = deepcopy(correct_citizen)
            citizen[field] = ''
            citizen_fields_test.append((citizen, False))
            if field in ['town', 'street', 'building']:

                # Too long.
                citizen = deepcopy(correct_citizen)
                citizen[field] = "".join(['a' for _ in range(257)])
                citizen_fields_test.append((citizen, False))

                # Correct length.
                citizen = deepcopy(correct_citizen)
                citizen[field] = "".join(['a' for _ in range(256)])
                citizen_fields_test.append((citizen, True))

                # Wrong symbols.
                citizen = deepcopy(correct_citizen)
                citizen[field] = '~'
                citizen_fields_test.append((citizen, False))

    return citizen_fields_test


@pytest.mark.parametrize('citizen,is_correct',
                         prepare_fields_test())
def test_check_citizen_fields(citizen, is_correct):
    if is_correct:
        check_citizen_fields(citizen)
    else:
        with pytest.raises(ValueError):
            check_citizen_fields(citizen)


def prepare_init_citizens_test():
    data = load_data()
    citizens_test = []
    correct_citizen = data[0]
    citizens_test.append((correct_citizen, True))

    # Wrong fields set.
    # Delete field.
    for field in correct_citizen:
        citizen = deepcopy(correct_citizen)
        del citizen[field]
        citizens_test.append((citizen, False))

    # Or add some.
    citizen = deepcopy(correct_citizen)
    citizen['test_field'] = 'test'
    citizens_test.append((citizen, False))

    # Wrong type.
    citizens_test.append(([1], False))

    return citizens_test


@pytest.mark.parametrize('citizen,is_correct',
                         prepare_init_citizens_test())
def test_check_init_citizen(citizen, is_correct):
    if is_correct:
        check_init_citizen(citizen)
    else:
        with pytest.raises(ValueError):
            check_init_citizen(citizen)


def prepare_update_citizens_test():
    data = load_data()
    citizens_test = []

    # Wrong field
    citizens_test.append((deepcopy(data[0]), False))

    # Correct sample.
    correct_citizen = deepcopy(data[0])
    del correct_citizen['citizen_id']
    citizens_test.append((correct_citizen, True))

    # Remove some fields
    for field in correct_citizen:
        citizen = deepcopy(correct_citizen)
        del citizen[field]
        citizens_test.append((citizen, True))

    # Add some field.
    citizen = deepcopy(correct_citizen)
    citizen['test_field'] = 'test'
    citizens_test.append((citizen, False))

    # Wrong type.
    citizens_test.append(([1], False))

    return citizens_test


@pytest.mark.parametrize('citizen,is_correct',
                         prepare_update_citizens_test())
def test_check_update_citizen(citizen, is_correct):
    if is_correct:
        check_update_citizen(citizen)
    else:
        with pytest.raises(ValueError):
            check_update_citizen(citizen)


def prepare_citizens_group_test():
    data = load_data()
    citizens_groups_test = []

    # Correct sample.
    citizens_groups_test.append((deepcopy(data), True))

    # Wrong type.
    citizens_groups_test.append(({'test': 1}, False))

    # Wrong ids.
    spoiled_data = []
    for citizen in data:
        spoiled_citizen = deepcopy(citizen)
        spoiled_citizen['citizen_id'] = 1
        spoiled_data.append(spoiled_citizen)
    citizens_groups_test.append((spoiled_data, False))

    # Not unique relatives.
    spoiled_data = []
    for citizen in data:
        spoiled_citizen = deepcopy(citizen)
        spoiled_citizen['relatives'] = [1, 1]
        spoiled_data.append(spoiled_citizen)
    citizens_groups_test.append((spoiled_data, False))

    # Relatives with wrong ids.
    spoiled_data = []
    for i, citizen in enumerate(data):
        spoiled_citizen = deepcopy(citizen)
        spoiled_citizen['citizen_id'] = i
        spoiled_citizen['relatives'] = [100]
        spoiled_data.append(spoiled_citizen)
    citizens_groups_test.append((spoiled_data, False))

    # Not symmetric relationships.
    spoiled_data = []
    for i, citizen in enumerate(data):
        spoiled_citizen = deepcopy(citizen)
        spoiled_citizen['citizen_id'] = i
        spoiled_citizen['relatives'] = [0]
        spoiled_data.append(spoiled_citizen)
    citizens_groups_test.append((spoiled_data, False))

    return citizens_groups_test


@pytest.mark.parametrize('citizens,is_correct',
                         prepare_citizens_group_test())
def test_check_citizens_group(citizens, is_correct):
    if is_correct:
        check_citizens_group(citizens)
    else:
        with pytest.raises(ValueError):
            check_citizens_group(citizens)
