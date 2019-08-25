"""
Run Flask application.
"""
import os
import pickle
import logging

from flask import (
    Flask,
    request,
    jsonify,
    abort,
    make_response,
    logging as flask_logging,
)

from api_tools.check_data import (
    check_citizens_group,
    check_update_citizen,
)
from api_tools.db_tools import (
    check_citizen_exists,
    check_citizen_relatives_exist,
    check_import_exists,
    save_new_import,
    update_import,
    load_import,
    calculate_birthdays,
    calculate_ages_stat,
)

app = Flask(__name__)

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(module)s %(message)s')

PATCH_URL = '/imports/<int:import_id>/citizens/<int:citizen_id>'
GET_CITIZENS_URL = '/imports/<int:import_id>/citizens'
GET_BIRTHDAYS_URL = '/imports/<int:import_id>/citizens/birthdays'
GET_AGES_URL = '/imports/<int:import_id>/towns/stat/percentile/age'


def abort_request(message, code=400):
    app.logger.error('Request error (%d): %s', code, message)

    response = jsonify(code=code, message=message)
    response.status_code = code
    abort(response)


def correct_response(data, code=200):
    json_data = {'data': data}
    return make_response(jsonify(json_data), code)


@app.route('/ping')
def ping():
    app.logger.debug('Test.')
    return 'pong'


@app.route('/imports', methods=['POST'])
def import_data():
    app.logger.info('Data import.')
    data = request.get_json(force=True)
    citizens = data['citizens']
    try:
        check_citizens_group(citizens)
    except ValueError as error:
        abort_request(error.args)
    else:
        import_id_json = save_new_import(citizens)
        return correct_response(import_id_json, code=201)


@app.route(PATCH_URL, methods=['PATCH'])
def patch_data(import_id, citizen_id):
    app.logger.info('Data patch.')
    app.logger.debug('In import {} patch citizen {}.'
                     .format(import_id, citizen_id))
    citizen_update = request.get_json(force=True)
    try:
        check_update_citizen(citizen_update)
        check_import_exists(import_id)
        check_citizen_relatives_exist(import_id, citizen_id)
        check_citizen_exists(import_id, citizen_id)
    except ValueError as error:
        abort_request(error.args)
    else:
        citizen_json = update_import(import_id,
                                     citizen_id,
                                     citizen_update)
        return correct_response(citizen_json)


@app.route(GET_CITIZENS_URL, methods=['GET'])
def get_citizens(import_id):
    app.logger.info('Get citizens.')
    app.logger.debug('Get citizens from  import {}.'
                     .format(import_id))
    try:
        check_import_exists(import_id)
    except ValueError as error:
        abort_request(error.args)
    else:
        data = load_import(import_id)
        return correct_response(data)


@app.route(GET_BIRTHDAYS_URL, methods=['GET'])
def get_birthdays(import_id):
    app.logger.info('Get birthdays.')
    app.logger.debug('Get birthdays from  import {}.'
                     .format(import_id))
    try:
        check_import_exists(import_id)
    except ValueError as error:
        abort_request(error.args)
    else:
        birthdays = calculate_birthdays(import_id)
        return correct_response(birthdays)


@app.route(GET_AGES_URL, methods=['GET'])
def get_ages(import_id):
    app.logger.info('Get ages.')
    app.logger.debug('Get ages from  import {}.'
                     .format(import_id))
    try:
        check_import_exists(import_id)
    except ValueError as error:
        abort_request(error.args)
    else:
        ages = calculate_birthdays(import_id)
        return correct_response(ages)
