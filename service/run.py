import os
import pickle
import logging

from flask import Flask, request, jsonify, abort


app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

PATCH_URL = '/imports/<int:import_id>/citizens/<int:citizen_id>'
GET_CITIZENS_URL = '/imports/<int:import_id>/citizens'
GET_BIRTHDAYS_URL = '/imports/<int:import_id>/citizens/birthdays'
GET_AGES_URL = '/imports/<int:import_id>/towns/stat/percentile/age'


@app.route('/ping')
def ping():
    return 'pong'


@app.route('/imports', methods=['POST'])
def import_data():
    logger.info('Data import.')
    pass


@app.route(PATCH_URL, methods=['PATCH'])
def patch_data(import_id, citizen_id):
    logger.info('Data patch.')
    logger.debug('In import {} patch citizen {}.'
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
    logger.info('Get birthdays.')
    logger.debug('Get birthdays from  import {}.'
                 .format(import_id))
    pass


@app.route(GET_AGES_URL, methods=['GET'])
def get_ages(import_id):
    logger.info('Get ages.')
    logger.debug('Get ages from  import {}.'
                 .format(import_id))
    pass



