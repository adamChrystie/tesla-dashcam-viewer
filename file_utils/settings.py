"""A module for the settings file and other related settings actions."""
import datetime
import os
import logging
import platform

from typing import Any

from constants import (SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE,
                       APP_WINDOWS_SETTINGS_FILE_NAME,
                       APP_SETTINGS_DATA_FOLDER)
from PySide6.QtCore import QSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppSettings(QSettings):
    """ A class related to the app's settings."""
    def __init__(self, organization="atomfx.com", app_name="tesla_dashcam_viewer"):
        if platform.system() == "Windows":
            # Use INI format and store in the Roaming AppData directory
            app_data_dir = os.path.join(os.environ["APPDATA"], APP_SETTINGS_DATA_FOLDER)
            os.makedirs(app_data_dir, exist_ok=True)  # Ensure directory exists
            settings_path = os.path.join(app_data_dir, APP_WINDOWS_SETTINGS_FILE_NAME)
            super().__init__(settings_path, QSettings.IniFormat)
        elif platform.system() == 'Darwin':
            super().__init__(organization, app_name)

        self.create_initial_settings_file()
        if os.path.exists(self.fileName()):
            logger.info(f'Settings file path:{self.fileName()}')
        self.ensure_required_defaults_exist()

    def create_initial_settings_file(self) -> None:
        """ Create an initial settings file.

        Returns:None

        """
        if not os.path.exists(self.fileName()):
            now = datetime.datetime.now().isoformat()
            logger.info(f'Creating initial settings file:{self.fileName()}')
            self.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now)
            self.sync()

    def ensure_required_defaults_exist(self) -> None:
        """ Ensure the required default settings exist in the setting file.

        Returns: None

        """
        last_check_for_update = self.value(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE)
        if last_check_for_update is None:
            now = datetime.datetime.now().isoformat()
            logger.info(f'Setting default for setting key: {SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE}={now})')
            self.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now)
            self.sync()

    def setValue(self, key: str, value) -> None:
        """ Override setValue to add custom behavior if needed.
        Args:
            key (str): Setting name.
            value ():  Setting's value, can be anything QVariant can handle.

        Returns: None

        """
        logger.info(f"Saving setting: {key} = {value}")
        super().setValue(key, value)

    def value(self, key: str, default_value=None) -> Any:
        """ Override value to ensure default values are handled correctly.
        Args:
            key (str): Setting name.
            default_value (None): A value returned if the setting key can't be found.

        Returns: Any

        """
        result = super().value(key, default_value)
        logger.info(f"Retrieving setting: {key} -> {result}")
        return result

    def remove(self, key: str) -> None:
        """ Override remove to log actions.

        Args:
            key (str): Setting name.

        Returns: None

        """
        logger.info(f"Removing setting: {key}")
        super().remove(key)

    def clear(self) -> None:
        """
        Override clear to add confirmation or additional logging.

        Returns: None

        """
        logger.info("Clearing all settings")
        super().clear()

    def sync(self) -> None:
        """
        Override sync, write the settings to disk on demand. Typically there is no need to call this
        as QSettings will save periodically automatically and when the instance is destroyed.

        Returns: None

        """
        super().sync()

