"""A module for the settings file and other related settings actions."""
import datetime
import os
import platform
import json

from constants import APP_SETTINGS_DATA_FOLDER, APP_SETTINGS_FILE_NAME

from PySide6 import QtCore

class Settings(QtCore.QSettings):
    """A class related to the app's settings."""
    def __init__(self, organization, app_name):
        super().__init__(organization, app_name)
        self._settings = QtCore.QSettings('WizardAssistant', 'WizardAssistantDesktop')
        print(settings.fileName())

class SettingsFile(object):
    """A class related to reading and writing the app's setting fire."""
    def __init__(self):
        self._fpath = os.path.join(self.get_app_settings_folder_path(), APP_SETTINGS_FILE_NAME)
        if not os.path.exists(self._fpath):
            # If there's not settings file, make an initial file with default settings.
            self.write_settings_file(create_new=True)
        self._data = self.read_settings_file()

    def get_app_settings_folder_path(self):
        folder = None
        if platform.system() == "Windows":  # Windows
            folder = os.path.join(os.getenv("APPDATA"), APP_SETTINGS_DATA_FOLDER)  # Roaming folder
        elif platform.system() == 'Darwin':  # macOS
            folder = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_SETTINGS_DATA_FOLDER)
        return folder

    def read_settings_file(self):
        """Read the app settings file and return a dictionary or None"""
        with open(self._fpath, 'r') as fp:
            data = json.load(fp)
        return data

    def write_settings_file(self, create_new=False):
        """Write the app settings file."""
        if create_new:
            os.makedirs(self.get_app_settings_folder_path(), exist_ok=True)
            data = {'last_update_check': datetime.datetime.now().isoformat()}
            print(f'INFO: Writing initial settings file: {self._fpath}')
        else:
            data = self._data
            data['last_update_check'] = datetime.datetime.now().isoformat()
            print(f'INFO: Updating settings file: {self._fpath}')
        with open(self._fpath, 'w') as fp:
            json.dump(data, fp)

if __name__ == '__main__':
    from pprint import pprint
    settings_obj = SettingsFile()
    pprint(settings_obj._data)