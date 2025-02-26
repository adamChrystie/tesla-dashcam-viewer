import os
from pathlib import Path
import datetime
import json
import platform
from typing import Union
import requests

import file_utils.settings
from constants import APP_VERSION, API_URL


def should_check_for_update(settings: file_utils.settings.SettingsFile):
    """Is it time to check for available updates? App checks after 24
    hours."""
    last_time_checked = settings._data['last_update_check']
    # Convert the stored timestamp str to a datetime object
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    last_timestamp_checked = datetime.datetime.strptime(last_time_checked, date_format)
    print('##########', type(last_timestamp_checked))
    # Get the current time
    now = datetime.datetime.now()
    # Check if 24 hours have passed
    return now >= (last_timestamp_checked + datetime.timedelta(days=1))

def check_for_new_version(current_version: str=None) -> Union[str, None]:
    """ Check to see if there is a newer version and return the version string or None."""
    if not current_version:
        current_version = APP_VERSION
    try:
        response = requests.get(f'{API_URL}/version')
        data = response.json()
        latest_version = data["latest_version"]
        if latest_version > current_version:
            return latest_version
    except requests.RequestException:
        print("WARNING: Could not check for updates.")
    return None

