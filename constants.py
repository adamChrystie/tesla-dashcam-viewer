"""A module for constants."""
import os
import platform

API_URL = "https://www.adamchrystie.com/tesla-dashcam-viewer/api"
APP_VERSION = 'v1.0.1'
APP_TMP_DATA_FOLDER = 'tesla_dashcam_viewer'
TESLAS_CAMERA_NAMES = ['back', 'front', 'left_repeater', 'right_repeater']

if platform.system() == 'Windows':
    TMP_DATA_DIR = os.path.join(os.getenv("APPDATA"), APP_TMP_DATA_FOLDER)
elif platform.system() == 'Darwin':
    TMP_DATA_DIR = os.path.join(os.getenv("HOME"), "Library", "Application Support", APP_TMP_DATA_FOLDER)
else:
    TMP_DATA_DIR = None
