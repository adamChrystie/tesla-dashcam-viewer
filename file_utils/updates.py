import os
import datetime
import json
import platform
from typing import Union
import requests
from constants import APP_TMP_DATA_FOLDER, APP_VERSION, API_URL


def should_check_for_update(last_check_timestamp):
    # Convert the stored timestamp to a datetime object
    last_check_time = datetime.datetime.fromtimestamp(last_check_timestamp)
    # Get the current time
    now = datetime.now()
    # Check if 24 hours have passed
    return now >= last_check_time + datetime.timedelta(days=1)

def get_update_check_path():
    if platform.system() == "Windows":  # Windows
        folder = os.path.join(os.getenv("APPDATA"), APP_TMP_DATA_FOLDER)  # Roaming folder
    elif platform.system() == 'Darwin':  # macOS
        folder = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "YourApp")
    else:
        return None

    os.makedirs(folder, exist_ok=True)  # Ensure folder exists
    return os.path.join(folder, "last_update_check.json")

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

def write_json_file(fpath: str, data: dict):
    with open(fpath, 'w') as f:
        json.dump(data, f)
