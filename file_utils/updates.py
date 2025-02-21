from typing import Union
import requests
import constants


def check_for_new_version(current_version: str=None) -> Union[str, None]:
    """ Check to see if there is a newer version and return the version string or None."""
    if not current_version:
        current_version = constants.APP_VERSION
    try:
        response = requests.get(f'{constants.API_URL}/version')
        data = response.json()
        latest_version = data["latest_version"]
        if latest_version > current_version:
            return  latest_version
    except requests.RequestException:
        print("WARNING: Could not check for updates.")
    return None
