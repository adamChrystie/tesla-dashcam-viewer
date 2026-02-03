"""Module related to handling video events on disk."""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Union

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
        self._camera_files_dict: Dict[str, Path] = {}

    @property
    def camera_files_dict(self) -> Dict[str, Path]:
        """
        Get the dictionary mapping camera names to their video file paths.
        Returns:
            dict: A dictionary mapping camera names to their video file paths.
        """
        return self._camera_files_dict

    @property
    def timestamp(self) -> str:
        """
        Get the timestamp of the video event.
        Returns:
            str: The timestamp of the video event.
        """
        return self._timestamp

    def update_camera_files_dict(self, video_file_paths: List[Path]) -> None:
        """
        Set up mapping camera names to their video file paths.
        Args:
            video_file_paths (List[Path]): A list of video file paths for a single event.
        """
        for cam_name in TESLAS_CAMERA_NAMES:
            for video_fpath in video_file_paths:
                if cam_name in video_fpath.name:
                    self._camera_files_dict[cam_name] = video_fpath
                    break

    def missing_camera_names(self) -> List[str]:
        """Return camera names that are missing for this event."""
        return [cam for cam in TESLAS_CAMERA_NAMES if cam not in self._camera_files_dict]

def get_all_videos_in_dir(dir_path: Union[Path, str]) -> List[Path]:
    """
    Given a directory return all the mp4 files in the directory & subdirectories.
    Args:
        dir_path (Path|str): A parent directory path to start searching from.
    Returns:
        List[Path]: A list of file paths.
    """
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    files = []
    for f in dir_path.glob('**/*.mp4'):
        files.append(f)
    return files

def group_videos_by_timestamp(fpath_list: List[Path]) -> Dict[str, List[Path]]:
    """
    Groups video files based on their starting timestamp in the filename.
    Args:
        fpath_list (List[Path]): List of video file paths.
    Returns:
        Dict[str, List[Path]]: keys are timestamps and values are lists of file paths.
    """
    # Regular expression to extract the timestamp at the start of the filename
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})')
    grouped_files: Dict[str, List[Path]] = defaultdict(list)
    for f_path in fpath_list:
        file_name = f_path.name
        match = timestamp_pattern.match(file_name)
        if match:
            timestamp = match.group(1)
            grouped_files[timestamp].append(f_path)
    return dict(grouped_files)

def make_event_data_objects_for_a_dir_path(dir_path: Union[Path, str]) -> List[VideoEventData]:
    """
    Given a directory, make a list of event data objects for each timestamp event. Subdirectories
    are also searched for events.
    Args:
        dir_path (Path|str): A parent directory path to start searching from.
    Returns:
        list of VideoEventData: A list of VideoEventData objects.
    """

    video_files = get_all_videos_in_dir(dir_path)
    grouped_videos = group_videos_by_timestamp(video_files)
    event_data_objs = []
    for timestamp, video_file_paths in grouped_videos.items():
        event_data = VideoEventData()
        event_data._timestamp = timestamp
        event_data.update_camera_files_dict(video_file_paths)
        event_data_objs.append(event_data)
    return event_data_objs
