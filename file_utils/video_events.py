"""Module related to handling video events on disk."""
import re
from collections import defaultdict
from pathlib import Path
from typing import Union
from constants import TESLAS_CAMERA_NAMES


class VideoEventData(object):
    """A class which describes a video event."""
    def __init__(self):
        self._back_fpath = None
        self._front_fpath = None
        self._left_repeater_fpath = None
        self._right_repeater_fpath = None
        self._timestamp = None
        self._event_name = None
        self._camera_files_dict = defaultdict(Path)

    @property
    def camera_files_dict(self):
        return self._camera_files_dict

    @property
    def timestamp(self):
        return self._timestamp

    def update_camera_files_dict(self, video_file_paths: dict):
        """ Setup the dictionary mapping camera names to their video file paths."""
        for cam_name in TESLAS_CAMERA_NAMES:
            for video_fpath in video_file_paths:
                if cam_name in video_fpath.name:
                    self._camera_files_dict[cam_name] = video_fpath

def get_all_videos_in_dir(dir_path: Union[Path, str]) -> list:
    """Given a directory return all the mp4 files in the dir as a list."""
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    files = []
    for f in dir_path.glob('**/*.mp4'):
        files.append(f)
    return files

def group_videos_by_timestamp(fpath_list: list):
    """
    Groups video files based on their starting timestamp in the filename.

    Args:
        file_list (list of str): List of video file names.

    Returns:
        dict: A dictionary where the keys are timestamps and values are lists of files.
    """
    # Regular expression to extract the timestamp at the start of the filename
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})')
    grouped_files = defaultdict(list)
    for f_path in fpath_list:
        file_name = f_path.name
        match = timestamp_pattern.match(file_name)
        if match:
            timestamp = match.group(1)
            grouped_files[timestamp].append(f_path)
    return dict(grouped_files)

def make_event_data_objects_for_a_dir_path(dir_path: Union[Path, str]):
    """ Given a directory, make a list of event data objects for each timestamp event."""
    video_files = get_all_videos_in_dir(dir_path)
    grouped_videos = group_videos_by_timestamp(video_files)
    event_data_objs = []
    for timestamp, video_file_paths in grouped_videos.items():
        event_data = VideoEventData()
        event_data._timestamp = timestamp
        event_data.update_camera_files_dict(video_file_paths)
        event_data_objs.append(event_data)
    return event_data_objs
