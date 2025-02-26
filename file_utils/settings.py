"""A module for the settings file and other related settings actions."""
import datetime
import os.path

from constants import SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE
from PySide6.QtCore import QSettings

class AppSettings(QSettings):
    """A class related to the app's settings."""
    def __init__(self, organization="atomfx.com", app_name="tesla_dashcam_viewer"):
        super().__init__(organization, app_name)
        self.create_initial_settings_file()
        if os.path.exists(self.fileName()):
            print(f'Settings file path:{self.fileName()}')
        self.ensure_required_defaults_exist()

    def create_initial_settings_file(self):
        if not os.path.exists(self.fileName()):
            now = datetime.datetime.now().isoformat()
            print(f'Setting default for setting key: {SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE}={now})')
            self.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now)
            self.sync()

    def ensure_required_defaults_exist(self):
        last_check_for_update = self.value(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE)
        if last_check_for_update is None:
            now = datetime.datetime.now().isoformat()
            print(f'Setting default for setting key: {SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE}={now})')
            self.setValue(SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE, now)
            self.sync()

    def setValue(self, key, value):
        """
        Override setValue to add custom behavior if needed.
        """
        print(f"Saving setting: {key} = {value}")
        super().setValue(key, value)

    def value(self, key, default_value=None):
        """
        Override value to ensure default values are handled correctly.
        """
        result = super().value(key, default_value)
        print(f"Retrieving setting: {key} -> {result}")
        return result

    def remove(self, key):
        """
        Override remove to log actions.
        """
        print(f"Removing setting: {key}")
        super().remove(key)

    def clear(self):
        """
        Override clear to add confirmation or additional logging.
        """
        print("Clearing all settings")
        super().clear()

    def sync(self):
        """
        Override sync, write the settings to disk on demand. Typically there is no need to call this
        as QSettings will save periodically automatically and when the instance is destroyed.
        Returns:
        """
        super().sync()


# class SettingsFile(object):
#     """A class related to reading and writing the app's setting fire."""
#     def __init__(self):
#         self._fpath = os.path.join(self.get_app_settings_folder_path(), APP_SETTINGS_FILE_NAME)
#         if not os.path.exists(self._fpath):
#             # If there's not settings file, make an initial file with default settings.
#             self.write_settings_file(create_new=True)
#         self._data = self.read_settings_file()
#
#     def get_app_settings_folder_path(self):
#         folder = None
#         if platform.system() == "Windows":  # Windows
#             folder = os.path.join(os.getenv("APPDATA"), APP_SETTINGS_DATA_FOLDER)  # Roaming folder
#         elif platform.system() == 'Darwin':  # macOS
#             folder = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_SETTINGS_DATA_FOLDER)
#         return folder
#
#     def read_settings_file(self):
#         """Read the app settings file and return a dictionary or None"""
#         with open(self._fpath, 'r') as fp:
#             data = json.load(fp)
#         return data
#
#     def write_settings_file(self, create_new=False):
#         """Write the app settings file."""
#         if create_new:
#             os.makedirs(self.get_app_settings_folder_path(), exist_ok=True)
#             data = {'last_update_check': datetime.datetime.now().isoformat()}
#             print(f'INFO: Writing initial settings file: {self._fpath}')
#         else:
#             data = self._data
#             data['last_update_check'] = datetime.datetime.now().isoformat()
#             print(f'INFO: Updating settings file: {self._fpath}')
#         with open(self._fpath, 'w') as fp:
#             json.dump(data, fp)

if __name__ == '__main__':
    settings_obj = AppSettings()
    print(settings_obj.fileName())
    settings_obj.setValue('app/datetime_of_last_check_for_updates', 'never')
