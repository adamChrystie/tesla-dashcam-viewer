import os
from pathlib import Path
import datetime
import json
import platform
from typing import Union
import requests
from constants import APP_VERSION, API_URL


def is_time_to_check(self, last_time_checked: datetime.datetime) -> bool:
    """Check for updates once per day and display a message if there is one."""
    check_for_update = False
    current_datatime = datetime.datetime.now().isoformat()

    return check_for_update

def get_last_time_checked(last_check_fpath: Union[str, Path]) -> Union[str, Path, None]:
    """Get the last time the app checked to see if there was a new version available."""

    last_updated_jason_fpath = file_utils.updates.get_app_settings_file_path()
    if os.path.exists(last_updated_jason_fpath):
        # read it and see if it has been 24 hours
        pass
    else:
        file_utils.updates.write_json_file(last_updated_jason_fpath, data_dict)

def should_check_for_update(last_check_timestamp):
    # Convert the stored timestamp to a datetime object
    last_check_time = datetime.datetime.fromtimestamp(last_check_timestamp)
    # Get the current time
    now = datetime.now()
    # Check if 24 hours have passed
    return now >= last_check_time + datetime.timedelta(days=1)


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

