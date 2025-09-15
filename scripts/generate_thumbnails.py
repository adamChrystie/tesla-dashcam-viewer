#!/usr/bin/env python3
"""
FFmpeg thumbnail generation script for Tesla Dashcam Viewer.

This script demonstrates how to pre-generate thumbnails and low-resolution
proxy files for improved performance, as suggested in the UI optimization plan.
"""

import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


def generate_thumbnail(video_path: str, output_path: str, timestamp: str = "00:00:01") -> bool:
    """
    Generate a thumbnail from a video file using ffmpeg.
    
    Args:
        video_path: Path to the input video file
        output_path: Path for the output thumbnail image
        timestamp: Timestamp to extract thumbnail from (default: 1 second)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', timestamp,
            '-vframes', '1',
            '-vf', 'scale=320:180',  # Thumbnail size
            '-q:v', '2',  # High quality
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error generating thumbnail for {video_path}: {e}")
        return False


def generate_proxy_video(video_path: str, output_path: str) -> bool:
    """
    Generate a low-resolution proxy video for fast scrubbing.
    
    Args:
        video_path: Path to the input video file
        output_path: Path for the output proxy video
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', 'scale=640:360',  # Lower resolution
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '28',  # Higher compression
            '-c:a', 'aac',
            '-b:a', '64k',  # Lower audio bitrate
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error generating proxy for {video_path}: {e}")
        return False


def process_video_directory(input_dir: str, output_dir: str, generate_proxies: bool = False) -> None:
    """
    Process all video files in a directory to generate thumbnails and optionally proxy videos.
    
    Args:
        input_dir: Directory containing Tesla dashcam videos
        output_dir: Directory to store generated thumbnails and proxies
        generate_proxies: Whether to generate proxy videos for fast scrubbing
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directories
    thumbnails_dir = output_path / "thumbnails"
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    if generate_proxies:
        proxies_dir = output_path / "proxies"
        proxies_dir.mkdir(parents=True, exist_ok=True)
    
    # Supported video extensions
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv'}
    
    # Find all video files
    video_files = []
    for ext in video_extensions:
        video_files.extend(input_path.glob(f"**/*{ext}"))
    
    print(f"Found {len(video_files)} video files to process...")
    
    for i, video_file in enumerate(video_files):
        print(f"Processing {i+1}/{len(video_files)}: {video_file.name}")
        
        # Generate thumbnail
        thumbnail_name = video_file.stem + "_thumb.jpg"
        thumbnail_path = thumbnails_dir / thumbnail_name
        
        if not thumbnail_path.exists():
            success = generate_thumbnail(str(video_file), str(thumbnail_path))
            if success:
                print(f"  ✓ Generated thumbnail: {thumbnail_name}")
            else:
                print(f"  ✗ Failed to generate thumbnail for {video_file.name}")
        else:
            print(f"  → Thumbnail already exists: {thumbnail_name}")
        
        # Generate proxy video if requested
        if generate_proxies:
            proxy_name = video_file.stem + "_proxy.mp4"
            proxy_path = proxies_dir / proxy_name
            
            if not proxy_path.exists():
                success = generate_proxy_video(str(video_file), str(proxy_path))
                if success:
                    print(f"  ✓ Generated proxy: {proxy_name}")
                else:
                    print(f"  ✗ Failed to generate proxy for {video_file.name}")
            else:
                print(f"  → Proxy already exists: {proxy_name}")
    
    print(f"\nProcessing complete! Check {output_dir} for generated files.")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate thumbnails and proxy videos for Tesla dashcam footage"
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing Tesla dashcam videos"
    )
    parser.add_argument(
        "output_dir",
        help="Directory to store generated thumbnails and proxies"
    )
    parser.add_argument(
        "--proxies",
        action="store_true",
        help="Also generate low-resolution proxy videos for fast scrubbing"
    )
    parser.add_argument(
        "--check-ffmpeg",
        action="store_true",
        help="Check if ffmpeg is available and exit"
    )
    
    args = parser.parse_args()
    
    # Check if ffmpeg is available
    if args.check_ffmpeg:
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
            if result.returncode == 0:
                print("✓ ffmpeg is available")
                return
            else:
                print("✗ ffmpeg is not working properly")
                return
        except FileNotFoundError:
            print("✗ ffmpeg is not installed or not in PATH")
            return
    
    # Check if ffmpeg is available before processing
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: ffmpeg is not installed or not working properly.")
        print("Please install ffmpeg: https://ffmpeg.org/download.html")
        return
    
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        return
    
    # Process videos
    process_video_directory(args.input_dir, args.output_dir, args.proxies)


if __name__ == "__main__":
    main()