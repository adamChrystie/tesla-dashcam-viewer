# Copilot instructions (tesla-dashcam-viewer)

## Big picture
- This is a small PySide6 (Qt) desktop app for reviewing Tesla dashcam footage.
- App entry point is [tesla_dashcam_viewer.py](../tesla_dashcam_viewer.py): `MainWindow(QMainWindow)` wires the entire UI, playback, and update-check logic.
- Core modules:
  - [ui/](../ui/): Qt widgets composing the UI (event list, video grid, slider, popups).
  - [file_utils/](../file_utils/): non-UI helpers (settings persistence, update checks, video event discovery).
  - [constants.py](../constants.py): app version, camera names, update API endpoint.

## Developer workflow (what to run)
- Run locally: `python tesla_dashcam_viewer.py`
- Key runtime deps are implied by imports: `PySide6` (including `QtMultimedia`), `requests`, and `packaging`.
- Packaging: there is a PyInstaller spec at `tesla_dashcam_viewer.spec` (note: `*.spec` is ignored by .gitignore). Typical builds use PyInstaller with that spec.

## Video/event model and file conventions
- Events are discovered by scanning a user-chosen directory (and subdirectories) for `*.mp4`:
  - Discovery is in `file_utils/video_events.py` via `make_event_data_objects_for_a_dir_path()`.
  - Files are grouped by a leading timestamp in the filename: `YYYY-MM-DD_HH-MM-SS`.
- The app assumes four Tesla camera streams whose names appear in filenames:
  - `TESLAS_CAMERA_NAMES = ['back', 'front', 'left_repeater', 'right_repeater']` in [constants.py](../constants.py).
- `VideoEventData.video_files` ordering matters: `VideoEventWidget.toggle_play_pause()` indexes `[0..3]` and expects that same camera order.
  - If you change camera naming/order, update both [constants.py](../constants.py) and the widget playback wiring.

## Playback architecture (keep streams in sync)
- `MainWindow` constructs a `media_player_video_widget_dict` mapping camera name → `{ video_widget, media_player, audio_output }`.
  - The `front` player is treated as the “main” player (`self._main_player`) and drives the slider range/position.
- `ui/timeline_slider.py` (`TimelineSliderWidget`) seeks *all* camera players together.
  - When dragging: pauses all players on press, seeks on move, and resumes play on release.
- Only one event should play at a time:
  - `VideoEventWidget.play_pressed` is connected to `MainWindow.pause_others()`.
  - If you add new playback controls, preserve this “single active event” behavior to keep UI responsive.

## Settings + updates
- Settings are persisted via `QSettings` subclass `AppSettings` in `file_utils/settings.py`.
  - On Windows: stored as INI under `%APPDATA%/tesla_dashcam_viewer/tesla_dashcam_viewer_settings.ini`.
- Update checks:
  - `file_utils/updates.py` uses `API_URL` from [constants.py](../constants.py) and stores last-check time under `SETTINGS_KEY_DATETIME_OF_LAST_CHECK_FOR_UPDATE`.
  - `MainWindow` shows an `InfoPopup` when a newer `APP_VERSION` is available.

## UI patterns/conventions in this repo
- Styling is done inline via `setStyleSheet()` strings (see `ui/video_widget.py` and `ui/main_window_widgets.py`). Prefer extending those styles rather than introducing a new styling system.
- UI composition is “thin widgets”: small files per widget, constructed and connected by `MainWindow`.
- Logging is configured at `INFO` level in multiple modules; if you add noisy logs, keep them `logger.debug()` by default.
