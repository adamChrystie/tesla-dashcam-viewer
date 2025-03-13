"""Module related to handling video events on disk."""
import re
from collections import defaultdict
from pathlib import Path
from typing import Union, List

from constants import TESLAS_CAMERA_NAMES
import opentimelineio as otio

def get_all_videos_in_dir(dir_path: Union[Path, str]) -> List[str]:
    """
    Given a directory return all the mp4 files in the directory & subdirectories.
    Args:
        dir_path (Path|str): A parent directory path to start searching from.
    Returns:
        list of str: A list of file paths.
    """
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    files = []
    for f in dir_path.glob('**/*.mp4'):
        files.append(f)
    return files

def group_videos_by_timestamp(fpath_list: List[str]) -> dict:
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

class VideoEventData(object):
    """A class which describes a video event."""
    def __init__(self):
        self._back_fpath = None
        self._front_fpath = None
        self._left_repeater_fpath = None
        self._right_repeater_fpath = None
        self._timestamp = None
        self._event_name = None
        self._fps = 30
        self._duration = None # We'll use front camera's duration.
        self._camera_files_dict = defaultdict(Path)

    @property
    def camera_files_dict(self) -> dict:
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

    def update_camera_files_dict(self, video_file_paths: dict) -> None:
        """
        Set up mapping camera names to their video file paths.
        Args:
            video_file_paths (dict): A dictionary mapping camera names to their video file paths.
        """
        for cam_name in TESLAS_CAMERA_NAMES:
            for video_fpath in video_file_paths:
                if cam_name in video_fpath.name:
                    self._camera_files_dict[cam_name] = video_fpath

class CompoundVideoEvent(object):
    def __init__(self, sub_events):
        self.sub_events = sub_events  # List of VideoEventData
        self.timeline = self.create_timeline()

    def create_timeline(self):
        timeline = otio.schema.Timeline(name="Compound Event")
        track = otio.schema.Track(
            name="Dashcam Events", kind=otio.schema.TrackKind.Video)

        for event in self.sub_events:
            for cam, video_path in event.camera_files_dict.items():
                clip = otio.schema.Clip(
                    name=f"{event.timestamp}_{cam}",
                    media_reference=otio.schema.ExternalReference(target_url=video_path.as_posix()),
                    source_range=otio.opentime.TimeRange(
                        otio.opentime.RationalTime(0, 30),  # Assuming 30 FPS
                        otio.opentime.RationalTime(10, 30)  # Dummy duration; replace with actual
                    )
                )
                track.append(clip)

        timeline.tracks.append(track)
        return timeline

    def get_duration(self):
        return self.timeline.duration().to_seconds()
