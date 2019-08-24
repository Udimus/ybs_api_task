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
    logging as flask_logging,
)

app = Flask(__name__)

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(module)s %(message)s')

PATCH_URL = '/imports/<int:import_id>/citizens/<int:citizen_id>'
GET_CITIZENS_URL = '/imports/<int:import_id>/citizens'
GET_BIRTHDAYS_URL = '/imports/<int:import_id>/citizens/birthdays'
GET_AGES_URL = '/imports/<int:import_id>/towns/stat/percentile/age'


@app.route('/ping')
def ping():
    app.logger.debug('Test.')
    return 'pong'


@app.route('/imports', methods=['POST'])
def import_data():
    app.logger.info('Data import.')
    data = request.get_json(force=True)


@app.route(PATCH_URL, methods=['PATCH'])
def patch_data(import_id, citizen_id):
    app.logger.info('Data patch.')
    app.logger.debug('In import {} patch citizen {}.'
                     .format(import_id, citizen_id))
    pass


@app.route(GET_CITIZENS_URL, methods=['GET'])
def get_citizens(import_id):
    logger.info('Get citizens.')
    logger.debug('Get citizens from  import {}.'
                 .format(import_id))
    pass


@app.route(GET_BIRTHDAYS_URL, methods=['GET'])
def get_birthdays(import_id):
    app.logger.info('Get birthdays.')
    app.logger.debug('Get birthdays from  import {}.'
                     .format(import_id))
    pass


@app.route(GET_AGES_URL, methods=['GET'])
def get_ages(import_id):
    app.logger.info('Get ages.')
    app.logger.debug('Get ages from  import {}.'
                     .format(import_id))
    pass



