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

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the script:**
   ```bash
   python ppp.py
   ```

3. **Follow the prompts** to configure your settings and select folders

## How to use

### First run
The script will ask you to configure:
- **Image size**: Percentage of the square to fill (default: 95%)
- **Background color**: RGB values like `100,0,180` (purple)
- **JPEG quality**: 1-100 scale (default: 95)
- **Tag filtering**: Use macOS Finder tags to select specific photos

### Subsequent runs
Your preferences are saved automatically. The script will only ask for:
- **Source folder**: Where your original photos are located
- **Output folder**: Where processed photos will be saved

### macOS Tag Filtering
If enabled, only photos tagged with your specified tag (default: "To Publish") will be processed. This is perfect for marking specific photos in Finder before batch processing.

## Key Features

✅ **Smart resizing** - Images are proportionally scaled to fit perfectly within squares  
✅ **Batch processing** - Handle hundreds of photos at once with progress tracking  
✅ **Tag filtering** - Use macOS Finder tags to select specific photos  
✅ **Persistent settings** - Your preferences are remembered between sessions  
✅ **Error handling** - Skips corrupted files and continues processing  
✅ **Quality control** - Customizable JPEG compression for optimal file sizes  
✅ **Format conversion** - Outputs consistent JPEG files regardless of input format  
✅ **User-friendly interface** - Clean terminal interface with visual formatting and helpful prompts

## Roadmap

### 🎯 Next Up
- **Watermark System** - Add logos/text with customizable position, size, and transparency
- **Multi-format Output** - Generate web-optimized versions alongside squares
- **Drag & Drop Interface** - Desktop app with drag-and-drop functionality

### ✅ Recently Added
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
