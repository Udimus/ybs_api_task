"""
Tools to put and get data from DB.
"""


def check_import_exists(import_id):
    """
    Does import with this id really exist?
    """
    pass


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


def save_new_import(citizens):
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
