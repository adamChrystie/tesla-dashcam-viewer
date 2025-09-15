# Tesla-dashcam-viewer
A Python / PySide6 app for viewing Tesla dashcam footage.

## Recent UI Optimizations

This version includes significant UI performance optimizations:

- **Lazy Loading**: Video sources load only when needed, improving startup time
- **Smooth Animations**: Modern hover effects and transitions
- **Keyboard Shortcuts**: Full keyboard navigation support (Space, Arrow keys, Ctrl+O)
- **Loading Indicators**: Clear feedback during operations with skeleton UI
- **Memory Management**: Automatic cleanup of off-screen video sources
- **Batched Updates**: Reduced UI jank when loading many videos

See `UI_OPTIMIZATIONS.md` for detailed information about implemented optimizations.

## Performance Tools

- `scripts/generate_thumbnails.py`: Pre-generate thumbnails and proxy videos for improved performance
