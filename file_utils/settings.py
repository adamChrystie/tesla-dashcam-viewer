"""A module for the settings file and other related settings actions."""
import datetime
import os
import logging

from constants import SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE
from PySide6.QtCore import QSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppSettings(QSettings):
    """A class related to the app's settings."""
    def __init__(self, organization="atomfx.com", app_name="tesla_dashcam_viewer"):
        super().__init__(organization, app_name)
        self.create_initial_settings_file()
        if os.path.exists(self.fileName()):
            logger.info(f'Settings file path:{self.fileName()}')
        self.ensure_required_defaults_exist()

    def create_initial_settings_file(self):
        if not os.path.exists(self.fileName()):
            now = datetime.datetime.now().isoformat()
            logger.info(f'Setting default for setting key: {SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE}={now})')
            self.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now)
            self.sync()

    def ensure_required_defaults_exist(self):
        last_check_for_update = self.value(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE)
        if last_check_for_update is None:
            now = datetime.datetime.now().isoformat()
            logger.info(f'Setting default for setting key: {SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE}={now})')
            self.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now)
            self.sync()

    def setValue(self, key, value):
        """
        Override setValue to add custom behavior if needed.
        """
        logger.info(f"Saving setting: {key} = {value}")
        super().setValue(key, value)

    def value(self, key, default_value=None):
        """
        Override value to ensure default values are handled correctly.
        """
        result = super().value(key, default_value)
        logger.info(f"Retrieving setting: {key} -> {result}")
        return result

    def remove(self, key):
        """
        Override remove to log actions.
        """
        logger.info(f"Removing setting: {key}")
        super().remove(key)

    def clear(self):
        """
        Override clear to add confirmation or additional logging.
        """
        logger.info("Clearing all settings")
        super().clear()

    def sync(self):
        """
        Override sync, write the settings to disk on demand. Typically there is no need to call this
        as QSettings will save periodically automatically and when the instance is destroyed.
        Returns:
        """
        super().sync()

