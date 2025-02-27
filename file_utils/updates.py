import datetime
import requests
import logging
from packaging import version
from typing import Union

from constants import (SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE,
                       API_URL,
                       APP_VERSION,
                       REQUESTS_TIMEOUT_LIMIT)
from file_utils.settings import AppSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def should_check_for_update(settings: AppSettings, frequency: int =4) -> bool:
    """ Is it time to query the server to see if newer versions are available.
    Args:
        settings (AppSettings): The app's settings object.
        frequency (int): Check for updates N hours after the last time checked.

    Returns: bool

    """
    last_time_checked = settings.value(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE)
    logger.info(f'last_time_checked:{last_time_checked}')
    # Convert the stored timestamp str to a datetime object
    #date_format = "%Y-%m-%dT%H:%M:%S.%f"
    try:
        last_timestamp_checked = datetime.datetime.fromisoformat(last_time_checked)
    except (TypeError, ValueError):
        last_timestamp_checked = datetime.datetime.min
    # Get the current time
    now = datetime.datetime.now()
    # Check if 24 hours have passed
    should_check = now >= (last_timestamp_checked + datetime.timedelta(hours=frequency))
    if should_check:
        logger.info(f'Updating last checked timestamp to: {now.isoformat()}')
        settings.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now.isoformat())
    return should_check

def check_for_new_version(current_version: str=None) -> Union[str, bool]:
    """ Check to see if there is a newer version.

    Args:
        current_version (str): The current version number.

    Returns: Union[str, bool]

    """
    if not current_version:
        current_version = APP_VERSION
    try:
        response = requests.get(f'{API_URL}/version', timeout= REQUESTS_TIMEOUT_LIMIT)
        response.raise_for_status() # Raise exception if there was an issue.
        data = response.json()
        latest_version = data.get('latest_version', '')
        if latest_version and version.parse(latest_version) > version.parse(current_version):
            logger.info(f'New version available: {latest_version} (Current: {current_version})')
            return latest_version
    except (requests.RequestException, ValueError, KeyError, requests.ConnectTimeout) as e:
        logger.warning(f'Could not check for updates: {e}')
    return False
