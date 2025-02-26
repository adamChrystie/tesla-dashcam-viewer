import os
from pathlib import Path
import datetime
import json
import platform
from typing import Union
import requests

from file_utils.settings import AppSettings
from constants import (SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE,
                       API_URL,
                       APP_VERSION)

def should_check_for_update(settings: AppSettings):
    """Is it time to check for available updates? App checks after 24
    hours."""
    last_time_checked = settings.value(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE)
    print(f'last_time_checked:{last_time_checked}')
    # Convert the stored timestamp str to a datetime object
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    last_timestamp_checked = datetime.datetime.strptime(last_time_checked, date_format)
    # Get the current time
    now = datetime.datetime.now()
    # Check if 24 hours have passed
    should_check = now >= (last_timestamp_checked + datetime.timedelta(days=0.15))
    if should_check:
        print(
            f'Updating setting {SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE} '
            f'with new value {now}')
        settings.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now.isoformat())
    return should_check

def check_for_new_version(current_version: str=None) -> bool:
    """ Check to see if there is a newer version and return the version string or None."""
    if not current_version:
        current_version = APP_VERSION
    try:
        response = requests.get(f'{API_URL}/version')
        data = response.json()
        latest_version = data["latest_version"]
        print(f'Current version:{current_version} Latest Versions:{latest_version}')
        if latest_version > current_version:
            return True
    except requests.RequestException:
        print("WARNING: Could not check for updates.")
    return False

