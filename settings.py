import copy
import json
import os
import logging

SETTINGS_FILE_PATH = 'settings.json'
SCRAPING_LOG_FILE_PATH = 'run_history.log'
CACHED_IDS_PATH = 'cached_ids.json'
LOG_FILE_PATH = 'info.log'

DEFAULT_VALUES = {
    'scraping_log_file_path': SCRAPING_LOG_FILE_PATH,
    'folder_path': "ig_media",
    'extra_ids': [],
    'cached_ids_path': CACHED_IDS_PATH,
}

def get_settings_file():
    if not os.path.exists(SETTINGS_FILE_PATH):
        return {}
    with open(SETTINGS_FILE_PATH, 'r') as f:
        settings = json.load(f)
    return copy.deepcopy(settings)

def update_settings_file(new_settings):
    with open(SETTINGS_FILE_PATH, 'w') as f:
        json.dump(new_settings, f)

def has_setting(setting_name):
    return setting_name in get_settings_file()

def get(setting_name=None):
    settings = get_settings_file()
    if not setting_name:
        return settings  # If no specific setting value is specified we return all of them.
    elif setting_name in settings:
        return settings[setting_name]
    elif setting_name in DEFAULT_VALUES:
        return DEFAULT_VALUES[setting_name]
    else:
        raise KeyError(f'{setting_name} is not in the settings file and does not have a default value')

def clear_setting(setting_name):
    new_settings = get_settings_file()
    if setting_name in new_settings:
        new_settings.pop(setting_name)
    else:
        raise KeyError(f'{setting_name} is not in the settings file and does not have a default value')
    update_settings_file(new_settings)

def update(setting_name, updated_value):
    settings = get_settings_file()
    settings[setting_name] = updated_value
    update_settings_file(settings)

def setup_logger():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, 
                        format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
