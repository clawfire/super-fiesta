# Super Fiesta: Party Picture Processor

A Python tool that transforms your party photos into perfectly square formats optimized for social media platforms like Instagram.

## What it does

Super Fiesta takes your party pictures and:
- **Resizes them into perfect squares** (1080x1080px) with colored backgrounds
- **Preserves aspect ratios** by centering images within the square
- **Batch processes** entire folders of images
- **Filters by macOS tags** (optional) to process only selected photos
- **Maintains high quality** with customizable JPEG compression

Perfect for event photographers, party organizers, or anyone preparing photos for social media!

## Quick Start

### Option 1: Using Virtual Environment (Recommended)

1. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python3 -m venv super-fiesta
   
   # Activate it (macOS/Linux)
   source super-fiesta/bin/activate
   
   # On Windows, use:
   # super-fiesta\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the script:**
   ```bash
   python ppp.py
   ```

4. **When finished, deactivate:**
   ```bash
   deactivate
   ```

### Option 2: System-wide Installation

1. **Install dependencies globally:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the script:**
   ```bash
   python ppp.py
   ```

### Why Use Virtual Environments?

Virtual environments isolate your project dependencies and prevent conflicts with other Python projects. This is especially important for:
- **Avoiding dependency conflicts** between different projects
- **Ensuring consistent behavior** across different machines
- **Easy cleanup** - just delete the folder to remove all dependencies

## How to use

### First run
The script will ask you to configure:
- **Image size**: Percentage of the square to fill (default: 95%)
- **Background color**: RGB values like `100,0,180` (purple)
- **JPEG quality**: 1-100 scale (default: 95)
- **Tag filtering**: Use macOS Finder tags to select specific photos
- **Watermark settings**: Logo/image overlay with position, size, and opacity controls
- **Batch renaming**: Choose from multiple naming patterns for organized output

### Subsequent runs
Your preferences are saved automatically. The script will only ask for:
- **Source folder**: Where your original photos are located
- **Output folder**: Where processed photos will be saved

### macOS Tag Filtering
If enabled, only photos tagged with your specified tag (default: "To Publish") will be processed. This is perfect for marking specific photos in Finder before batch processing.

### Watermark System
Add your logo or branding to processed images:
- **Support for PNG images** with transparency for professional results
- **Flexible positioning**: top-left, top-right, bottom-left, bottom-right, or center
- **Adjustable size**: 1-50% of image width
- **Opacity control**: 10-100% transparency
- **Margin settings**: Distance from edges (0-100 pixels)
- **Automatic scaling**: Watermarks resize proportionally to maintain aspect ratio

### Batch Renaming System
Organize your processed images with intelligent naming patterns:
- **Original**: Keep original filenames (default behavior)
- **Sequential**: Clean numbered sequence (e.g., `Party_001.jpg`, `Party_002.jpg`)
- **Event-based**: Include event name and date (e.g., `Birthday_2024-01-15_001.jpg`)
- **Customizable options**: Set your own prefix, date format, and number padding
- **Conflict detection**: Warns about existing files and asks for confirmation
- **Renaming preview**: Shows exactly how files will be renamed before processing

## Key Features

✅ **Smart resizing** - Images are proportionally scaled to fit perfectly within squares  
✅ **Batch processing** - Handle hundreds of photos at once with progress tracking  
✅ **Tag filtering** - Use macOS Finder tags to select specific photos  
✅ **Persistent settings** - Your preferences are remembered between sessions  
✅ **Error handling** - Skips corrupted files and continues processing  
✅ **Quality control** - Customizable JPEG compression for optimal file sizes  
✅ **Format conversion** - Outputs consistent JPEG files regardless of input format  
✅ **User-friendly interface** - Clean terminal interface with visual formatting and helpful prompts  
✅ **Professional watermarks** - Add logos with customizable position, size, and transparency  
✅ **Smart batch renaming** - Organize files with sequential, event-based, or custom naming patterns

## Roadmap

### 🎯 Next Up
- **Multi-format Output** - Generate web-optimized versions alongside squares
- **Batch size options** - Configure custom output dimensions beyond 1080x1080
- **Preview mode** - Show sample processed image before batch processing
- **Drag & Drop Interface** - Desktop app with drag-and-drop functionality

### ✅ Recently Added
- **Smart batch renaming system** with sequential, event-based, and custom naming patterns
- **Professional watermark system** with flexible positioning, sizing, and opacity controls
- Enhanced terminal interface with visual formatting and better user experience
- Persistent user preferences via configuration file
- Robust error handling and input validation
- Progress tracking with success/error counts

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact
Thibault Milan - hello@thibaultmilan.com

## Acknowledgments
* Thanks to [ROAST](https://dice.fm/promoters/roast-p9ky) London for the design inspiration
* Thanks to the Python community for the great libraries
