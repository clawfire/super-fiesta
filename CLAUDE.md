# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Super Fiesta is a Python script that transforms party pictures into perfectly square formats for social media sharing. The main script `ppp.py` processes images by resizing them to fit within a colored square background, with optional macOS tag-based filtering.

## Commands

### Running the Application
```bash
python ppp.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

The application is a single-file Python script with the following key components:

### Core Functions
- `batch_square()` - Main image processing function that handles resizing, centering, and saving images
- `get_files_with_tag()` - macOS-specific function using `mdfind` to filter files by Finder tags
- `ask_or_load_config()` - Configuration management with persistent storage in `sf_config.ini`

### Configuration System
The application uses ConfigParser to manage user preferences in `sf_config.ini`:
- `side_length` - Percentage of square size for the longest side (default: 95)
- `background_color` - RGB values for background (default: 100,0,180)
- `jpeg_quality` - Output quality 1-100 (default: 95)
- `use_tags` - Whether to filter by macOS tags (default: yes)
- `tag` - Tag name to filter by (default: "To Publish")

### Image Processing Pipeline
1. Load configuration or prompt user for settings
2. Get source and output folder paths from user
3. Retrieve files (either all images or tagged files using macOS Spotlight)
4. For each image: resize proportionally to fit within 1080x1080 square, center on colored background
5. Save as JPEG with specified quality

### Dependencies
- **Pillow**: Image manipulation and processing
- **tqdm**: Progress bars for batch operations
- **ConfigParser**: Configuration file management (built-in)
- **subprocess**: For macOS tag filtering via `mdfind`

## Development Notes

- The script is designed specifically for macOS (uses `mdfind` for tag filtering)
- Output images are always 1080x1080 pixels regardless of input size
- Configuration persists between runs in `sf_config.ini`
- The script handles missing folders and empty directories gracefully
- Uses LANCZOS resampling for high-quality image resizing