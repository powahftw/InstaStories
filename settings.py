import copy
import json
import os
import sys
import logging
from telegram_handler import TelegramHandler

SETTINGS_FILE_PATH = 'settings.json'
FOLDER_PATH = "ig_media"
SCRAPING_LOG_FILE_PATH = 'run_history.log'
CACHED_IDS_PATH = 'cached_ids.json'
LOG_FILE_PATH = 'info.log'

LOGGING_TO_STDOUT = True
stream_handler = None

LOGGING_TO_TELEGRAM = False
telegram_handler = None

LOGGING_TO_FILE = False
file_handler = None

DEFAULT_VALUES = {
    'scraping_log_file_path': SCRAPING_LOG_FILE_PATH,
    'folder_path': FOLDER_PATH,
    'extra_ids': [],
    'cached_ids_path': CACHED_IDS_PATH,
    'loop_delay_seconds': 8 * 60 * 60,
    'loop_variation_percentage': 20
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
    values = {}
    values.update(DEFAULT_VALUES)
    values.update(settings)
    if not setting_name:
        return values  # If no specific setting value is specified we return all of them.
    elif setting_name in values:
        return values[setting_name]
    else:
        raise KeyError(f'{setting_name} is not in the settings file and does not have a default value')

def clear_setting(setting_name):
    new_settings = get_settings_file()
    if setting_name in new_settings:
        new_settings.pop(setting_name)
    else:
        raise KeyError(f'{setting_name} is not in the settings file.')
    update_settings_file(new_settings)

def update(setting_name, updated_value):
    settings = get_settings_file()
    settings[setting_name] = updated_value
    update_settings_file(settings)

def setup_logger():
    handlers = []
    if LOGGING_TO_FILE:
        global file_handler
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setLevel(logging.INFO)
        handlers.append(file_handler)
    if LOGGING_TO_STDOUT:
        global stream_handler
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        handlers.append(stream_handler)
    if LOGGING_TO_TELEGRAM:
        global telegram_handler
        telegram_handler = TelegramHandler(get("telegram_bot_api_key"), get("telegram_chat_id"))
        telegram_handler.setLevel(logging.INFO)
        telegram_formatter = logging.Formatter('%(message)s')
        telegram_handler.setFormatter(telegram_formatter)
        handlers.append(telegram_handler)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    logging.basicConfig(level=logging.NOTSET,
                        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=handlers
                        )

def completed_scraping():
    if LOGGING_TO_TELEGRAM and telegram_handler:
        telegram_handler.send_buffered_data()
