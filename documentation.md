Tesla Dashcam Documentation
1/21/2025

How to Use Tesla Dashcam Viewer
1. Main Window Overview
Upon launching the tool, the Main Window will appear. This contains the video display area, timeline slider, event list, and control buttons.
2. Navigating Video Events
- Video Screens: You can see video feeds from the front, back, left repeater, and right repeater cameras. These are displayed in a grid layout (up to 4 screens).
- Timeline Slider: The timeline slider allows you to scrub through the video events. You can drag the slider handle or use the arrow keys to navigate.
- Playback Controls: Each video event has playback controls, including play, pause, and stop.
3. Adding and Managing Video Events
- Use the "Scan A Directory For Videos" button in the control panel to scan for new video events.
- The video events will appear in the event list, which can be scrolled for easy browsing.
- Clicking on an event will load the video feeds and display the corresponding cameras.
4. Popup Information Windows
- Information popups will appear in the top-right corner to show event-related data, such as the event name and timestamp.
- These popups close automatically after a predefined timeout, which can be customized.
5. Likes and Favorites
- You can like specific video events. These events can be saved to a liked folder for later review.
- Use the "Copy Liked Videos" button to copy these events to another directory.

Troubleshooting & FAQs

Q1: The video is not playing correctly.
- Ensure your system has the necessary multimedia libraries installed (PySide6 with multimedia support).
- Check if the media player is correctly initialized with valid video file paths. 
Q2: The timeline slider is not responsive.
- Ensure the video feed is properly loaded and playing. The slider might not function without an active video feed.
- Try restarting the application to reset any temporary glitches.
Q3: How do I add a new video folder?
- Use the "Scan A Directory For Videos" button to open a directory chooser and select the folder containing video files. This will scan the folder for new events.
Q4: How can I remove a video event from the list?
- Currently, video events are displayed dynamically based on the scanned directory. You can remove unwanted files by simply deleting them from the source folder.
