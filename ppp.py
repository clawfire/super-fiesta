#!/usr/bin/env python3

import os
import subprocess
import sys
from datetime import datetime
from configparser import ConfigParser
from PIL import Image, ImageEnhance
from tqdm import tqdm


def get_files_with_tag(folder_path, tag):
    """Use mdfind to retrieve files with a specific tag within a folder."""
    query = f"kMDItemUserTags == '{tag}'"
    cmd = ['mdfind', '-onlyin', folder_path, query]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            files = result.stdout.split('\n')[:-1]
            # Filter to only image files
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            return image_files
        else:
            print(f"❌ Error while searching for tags in the folder: {folder_path}")
            print(f"❌ Command output: {result.stderr}")
            return []
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout while searching for tags in the folder: {folder_path}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error while searching for tags: {e}")
        return []


def save_config(config, config_file):
    print(f"Saving configuration to {config_file}")
    with open(config_file, 'w') as f:
        config.write(f)


def load_config(config_file):
    config = ConfigParser()
    print(f"Loading configuration from {config_file}")
    if os.path.exists(config_file):
        config.read(config_file)
    return config


def print_header():
    """Print a welcome header with branding."""
    print("\n" + "="*60)
    print("🎉 SUPER FIESTA - Party Picture Processor 🎉")
    print("Transform your photos into perfect social media squares!")
    print("="*60 + "\n")


def print_section(title):
    """Print a section header."""
    print(f"\n{'─'*50}")
    print(f"📋 {title}")
    print("─"*50)


def print_settings_summary(settings):
    """Display current settings in a formatted table."""
    print("\n📊 Current Settings:")
    print("┌─────────────────────┬──────────────────────────┐")
    print(f"│ Image Size          │ {settings['side_length']}% of square          │")
    print(f"│ Background Color    │ RGB({settings['background_color']})     │")
    print(f"│ JPEG Quality        │ {settings['jpeg_quality']}/100                   │")
    print(f"│ Tag Filtering       │ {'Enabled' if settings['use_tags'] == 'yes' else 'Disabled':25} │")
    if settings['use_tags'] == 'yes':
        print(f"│ Tag Name            │ '{settings.get('tag', 'To Publish')}'{' '*(25-len(settings.get('tag', 'To Publish'))-2)}│")
    print(f"│ Watermark           │ {'Enabled' if settings.get('use_watermark') == 'yes' else 'Disabled':25} │")
    if settings.get('use_watermark') == 'yes':
        watermark_file = os.path.basename(settings.get('watermark_path', ''))
        print(f"│ Watermark File      │ {watermark_file[:25]:25} │")
        print(f"│ Watermark Position  │ {settings.get('watermark_position', 'bottom-right'):25} │")
        print(f"│ Watermark Size      │ {settings.get('watermark_size', '10')}% of image width{' '*(10-len(settings.get('watermark_size', '10')))} │")
        print(f"│ Watermark Opacity   │ {settings.get('watermark_opacity', '80')}%{' '*(23-len(settings.get('watermark_opacity', '80')))} │")
    
    # Renaming settings
    naming_pattern = settings.get('naming_pattern', 'original')
    print(f"│ Naming Pattern      │ {naming_pattern:25} │")
    if naming_pattern == 'sequential':
        prefix = settings.get('naming_prefix', 'Photo')
        padding = settings.get('naming_padding', '3')
        print(f"│ Naming Prefix       │ {prefix:25} │")
        print(f"│ Number Padding      │ {padding} digits{' '*(18-len(padding))} │")
    elif naming_pattern == 'event-based':
        event = settings.get('naming_event', 'Event')
        include_date = settings.get('naming_include_date', 'yes')
        padding = settings.get('naming_padding', '3')
        print(f"│ Event Name          │ {event:25} │")
        print(f"│ Include Date        │ {'Yes' if include_date == 'yes' else 'No':25} │")
        print(f"│ Number Padding      │ {padding} digits{' '*(18-len(padding))} │")
    
    print("└─────────────────────┴──────────────────────────┘\n")


def get_user_choice(prompt, choices, default=None):
    """Get user choice with validation and clear options display."""
    choice_str = "/".join([f"[{c.upper()}]" if c == default else c.lower() for c in choices])
    while True:
        response = input(f"{prompt} ({choice_str}): ").strip().lower()
        if not response and default:
            return default
        if response in [c.lower() for c in choices]:
            return response
        print(f"❌ Please enter one of: {', '.join(choices)}")


def get_folder_path(prompt, default=None, create_if_missing=False):
    """Get folder path with validation and default handling."""
    while True:
        if default:
            path = input(f"{prompt} (default: {default}): ").strip() or default
        else:
            path = input(f"{prompt}: ").strip()
        
        if os.path.exists(path) and os.path.isdir(path):
            return path
        elif not os.path.exists(path):
            if create_if_missing:
                create = get_user_choice(f"Directory '{path}' doesn't exist. Create it?", ["y", "n"], "y")
                if create == "y":
                    try:
                        os.makedirs(path, exist_ok=True)
                        print(f"✅ Created directory: {path}")
                        return path
                    except OSError as e:
                        print(f"❌ Failed to create directory: {e}")
                        retry = get_user_choice("Would you like to try a different path?", ["y", "n"], "y")
                        if retry == "n":
                            sys.exit("Operation cancelled by user.")
                else:
                    retry = get_user_choice("Would you like to try a different path?", ["y", "n"], "y")
                    if retry == "n":
                        sys.exit("Operation cancelled by user.")
            else:
                print(f"❌ Directory not found: {path}")
                retry = get_user_choice("Would you like to try again?", ["y", "n"], "y")
                if retry == "n":
                    sys.exit("Operation cancelled by user.")
        else:
            print(f"❌ Path exists but is not a directory: {path}")
            retry = get_user_choice("Would you like to try again?", ["y", "n"], "y")
            if retry == "n":
                sys.exit("Operation cancelled by user.")


def confirm_processing(input_folder, output_folder, file_count):
    """Show processing confirmation with file count."""
    print(f"\n🚀 Ready to Process:")
    print(f"   📁 Source: {input_folder}")
    print(f"   📁 Output: {output_folder}")
    print(f"   📸 Files: {file_count} images")
    
    confirm = get_user_choice("\nStart processing?", ["y", "n"], "y")
    return confirm == "y"


def validate_config_value(value, value_type, min_val=None, max_val=None, valid_values=None):
    """Validate and convert configuration values."""
    try:
        if value_type == int:
            val = int(value)
            if min_val is not None and val < min_val:
                raise ValueError(f"Value must be >= {min_val}")
            if max_val is not None and val > max_val:
                raise ValueError(f"Value must be <= {max_val}")
            return val
        elif value_type == 'rgb':
            rgb_parts = [int(x.strip()) for x in value.split(',')]
            if len(rgb_parts) != 3:
                raise ValueError("RGB must have exactly 3 values")
            for part in rgb_parts:
                if not 0 <= part <= 255:
                    raise ValueError("RGB values must be between 0-255")
            return value
        elif value_type == 'file_path':
            if value and not os.path.exists(value):
                raise ValueError(f"File not found: {value}")
            return value
        elif value_type == 'position':
            valid_positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'bottom-center', 'center']
            if value not in valid_positions:
                raise ValueError(f"Position must be one of: {', '.join(valid_positions)}")
            return value
        elif value_type == 'naming_pattern':
            valid_patterns = ['original', 'sequential', 'event-based']
            if value not in valid_patterns:
                raise ValueError(f"Naming pattern must be one of: {', '.join(valid_patterns)}")
            return value
        elif value_type == 'png_file':
            if not value.lower().endswith('.png'):
                raise ValueError("Watermark must be a PNG file with transparency")
            if value and not os.path.exists(value):
                raise ValueError(f"File not found: {value}")
            # Check if PNG has transparency
            try:
                with Image.open(value) as img:
                    if img.mode not in ('RGBA', 'LA') and 'transparency' not in img.info:
                        raise ValueError("PNG file must have transparency (alpha channel)")
            except Exception as e:
                raise ValueError(f"Invalid PNG file: {e}")
            return value
        elif valid_values and value not in valid_values:
            raise ValueError(f"Value must be one of: {valid_values}")
        return value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid value '{value}': {e}")


def ask_or_load_config(script_dir):
    config_file = os.path.join(script_dir, 'sf_config.ini')
    config = load_config(config_file)
    
    # Check if we have existing valid config
    config_exists = False
    if 'SETTINGS' in config:
        try:
            validate_config_value(config['SETTINGS']['side_length'], int, 1, 100)
            validate_config_value(config['SETTINGS']['background_color'], 'rgb')
            validate_config_value(config['SETTINGS']['jpeg_quality'], int, 1, 100)
            # Validate watermark settings if they exist
            if config['SETTINGS'].get('use_watermark') == 'yes':
                validate_config_value(config['SETTINGS'].get('watermark_path', ''), 'png_file')
                validate_config_value(config['SETTINGS'].get('watermark_position', 'bottom-center'), 'position')
                validate_config_value(config['SETTINGS'].get('watermark_size', '14'), int, 1, 50)
                validate_config_value(config['SETTINGS'].get('watermark_opacity', '100'), int, 10, 100)
                validate_config_value(config['SETTINGS'].get('watermark_margin', '17'), int, 0, 100)
            # Validate renaming settings if they exist
            if config['SETTINGS'].get('naming_pattern', 'original') != 'original':
                validate_config_value(config['SETTINGS'].get('naming_pattern', 'original'), 'naming_pattern')
                validate_config_value(config['SETTINGS'].get('naming_padding', '3'), int, 1, 5)
            config_exists = True
            print("✅ Found existing configuration")
        except (ValueError, KeyError) as e:
            print(f"❌ Invalid configuration found: {e}")
            config.clear()
    
    if config_exists:
        print_settings_summary(config['SETTINGS'])
        reconfigure = get_user_choice("Would you like to reconfigure settings?", ["y", "n"], "n")
        if reconfigure == "n":
            return config
    
    # Configuration needed
    print_section("Configuration Setup")
    print("Let's configure your image processing preferences.\n")
    
    config['SETTINGS'] = {}
    
    # Image size configuration
    print("🖼️  Image Size Configuration:")
    print("   This controls how much of the square your image fills.")
    print("   95% leaves a small border, 100% fills the entire square.")
    while True:
        try:
            side_length = input("   Enter percentage (1-100, default 95): ") or '95'
            config['SETTINGS']['side_length'] = str(validate_config_value(side_length, int, 1, 100))
            break
        except ValueError as e:
            print(f"   ❌ {e}")
    
    # Background color configuration
    print("\n🎨 Background Color Configuration:")
    print("   Enter RGB values separated by commas (0-255 each).")
    print("   Examples: 100,0,180 (purple), 255,255,255 (white), 0,0,0 (black)")
    while True:
        try:
            bg_color = input("   Enter RGB values (default 100,0,180): ") or '100,0,180'
            config['SETTINGS']['background_color'] = validate_config_value(bg_color, 'rgb')
            break
        except ValueError as e:
            print(f"   ❌ {e}")
    
    # JPEG quality configuration
    print("\n📷 JPEG Quality Configuration:")
    print("   Higher values = better quality but larger files.")
    print("   95 is recommended for social media sharing.")
    while True:
        try:
            quality = input("   Enter quality (1-100, default 95): ") or '95'
            config['SETTINGS']['jpeg_quality'] = str(validate_config_value(quality, int, 1, 100))
            break
        except ValueError as e:
            print(f"   ❌ {e}")
    
    # Tag filtering configuration
    print("\n🏷️  Tag Filtering Configuration:")
    print("   Use macOS Finder tags to process only selected photos.")
    print("   Useful for marking specific photos before batch processing.")
    use_tags = get_user_choice("   Enable tag filtering?", ["y", "n"], "y")
    config['SETTINGS']['use_tags'] = 'yes' if use_tags == 'y' else 'no'
    
    if config['SETTINGS']['use_tags'] == 'yes':
        print("   Tag photos in Finder with this tag before processing.")
        tag = input("   Enter tag name (default 'To Publish'): ") or 'To Publish'
        config['SETTINGS']['tag'] = tag
    
    # Watermark configuration
    print("\n💧 Watermark Configuration:")
    print("   Add a logo or text watermark to your processed images.")
    use_watermark = get_user_choice("   Enable watermark?", ["y", "n"], "n")
    config['SETTINGS']['use_watermark'] = 'yes' if use_watermark == 'y' else 'no'
    
    if config['SETTINGS']['use_watermark'] == 'yes':
        print("   Select a PNG image file with transparency (alpha channel required).")
        while True:
            try:
                watermark_path = input("   Watermark PNG path: ").strip()
                if not watermark_path:
                    raise ValueError("Watermark path cannot be empty")
                validate_config_value(watermark_path, 'png_file')
                config['SETTINGS']['watermark_path'] = watermark_path
                break
            except ValueError as e:
                print(f"   ❌ {e}")
        
        print("   \n   Position options: top-left, top-right, bottom-left, bottom-right, bottom-center, center")
        while True:
            try:
                position = input("   Watermark position (default bottom-center): ") or 'bottom-center'
                validate_config_value(position, 'position')
                config['SETTINGS']['watermark_position'] = position
                break
            except ValueError as e:
                print(f"   ❌ {e}")
        
        while True:
            try:
                size = input("   Watermark size as % of image width (1-50, default 14): ") or '14'
                config['SETTINGS']['watermark_size'] = str(validate_config_value(size, int, 1, 50))
                break
            except ValueError as e:
                print(f"   ❌ {e}")
        
        while True:
            try:
                opacity = input("   Watermark opacity (10-100, default 100): ") or '100'
                config['SETTINGS']['watermark_opacity'] = str(validate_config_value(opacity, int, 10, 100))
                break
            except ValueError as e:
                print(f"   ❌ {e}")
        
        while True:
            try:
                margin = input("   Margin from edges as % of image (0-100, default 17): ") or '17'
                config['SETTINGS']['watermark_margin'] = str(validate_config_value(margin, int, 0, 100))
                break
            except ValueError as e:
                print(f"   ❌ {e}")
    
    # Batch renaming configuration
    print("\n🏷️  Batch Renaming Configuration:")
    print("   Choose how to name your processed images.")
    print("   Options: original (keep names), sequential (Party_001), event-based (Birthday_2024-01-15_001)")
    while True:
        try:
            pattern = input("   Naming pattern (default original): ") or 'original'
            validate_config_value(pattern, 'naming_pattern')
            config['SETTINGS']['naming_pattern'] = pattern
            break
        except ValueError as e:
            print(f"   ❌ {e}")
    
    if config['SETTINGS']['naming_pattern'] == 'sequential':
        prefix = input("   Enter prefix for filenames (default 'Photo'): ") or 'Photo'
        config['SETTINGS']['naming_prefix'] = prefix
        
        while True:
            try:
                padding = input("   Number padding (1=1, 2=01, 3=001, default 3): ") or '3'
                config['SETTINGS']['naming_padding'] = str(validate_config_value(padding, int, 1, 5))
                break
            except ValueError as e:
                print(f"   ❌ {e}")
    
    elif config['SETTINGS']['naming_pattern'] == 'event-based':
        event_name = input("   Enter event name (default 'Event'): ") or 'Event'
        config['SETTINGS']['naming_event'] = event_name
        
        use_date = get_user_choice("   Include date in filename?", ["y", "n"], "y")
        config['SETTINGS']['naming_include_date'] = 'yes' if use_date == 'y' else 'no'
        
        while True:
            try:
                padding = input("   Number padding (1=1, 2=01, 3=001, default 3): ") or '3'
                config['SETTINGS']['naming_padding'] = str(validate_config_value(padding, int, 1, 5))
                break
            except ValueError as e:
                print(f"   ❌ {e}")
    
    save_config(config, config_file)
    print("\n✅ Configuration saved!")
    
    return config


def load_and_prepare_watermark(watermark_path, target_width, watermark_size, opacity):
    """Load watermark image and prepare it for application."""
    try:
        watermark = Image.open(watermark_path)
        
        # Convert to RGBA if not already
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        
        # Calculate watermark size
        watermark_width = int(target_width * (watermark_size / 100))
        watermark_height = int((watermark.height * watermark_width) / watermark.width)
        
        # Resize watermark
        watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
        
        # Apply opacity
        if opacity < 100:
            # Create alpha mask for opacity
            alpha = watermark.split()[-1]  # Get alpha channel
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 100)
            watermark.putalpha(alpha)
        
        return watermark
    except Exception as e:
        print(f"\n❌ Error loading watermark: {e}")
        return None


def calculate_watermark_position(image_size, watermark_size, position, margin):
    """Calculate watermark position coordinates."""
    img_width, img_height = image_size
    wm_width, wm_height = watermark_size
    
    positions = {
        'top-left': (margin, margin),
        'top-right': (img_width - wm_width - margin, margin),
        'bottom-left': (margin, img_height - wm_height - margin),
        'bottom-right': (img_width - wm_width - margin, img_height - wm_height - margin),
        'bottom-center': ((img_width - wm_width) // 2, img_height - wm_height - margin),
        'center': ((img_width - wm_width) // 2, (img_height - wm_height) // 2)
    }
    
    return positions.get(position, positions['bottom-right'])


def generate_filename(original_path, index, naming_settings):
    """Generate new filename based on naming pattern settings."""
    original_name = os.path.basename(original_path)
    original_base = os.path.splitext(original_name)[0]
    
    pattern = naming_settings.get('naming_pattern', 'original')
    
    if pattern == 'original':
        # Keep original name but ensure .jpg extension
        return f"{original_base}.jpg"
    
    elif pattern == 'sequential':
        prefix = naming_settings.get('naming_prefix', 'Photo')
        padding = int(naming_settings.get('naming_padding', '3'))
        number = str(index).zfill(padding)
        return f"{prefix}_{number}.jpg"
    
    elif pattern == 'event-based':
        event = naming_settings.get('naming_event', 'Event')
        include_date = naming_settings.get('naming_include_date', 'yes') == 'yes'
        padding = int(naming_settings.get('naming_padding', '3'))
        number = str(index).zfill(padding)
        
        if include_date:
            today = datetime.now().strftime('%Y-%m-%d')
            return f"{event}_{today}_{number}.jpg"
        else:
            return f"{event}_{number}.jpg"
    
    # Fallback to original
    return f"{original_base}.jpg"


def check_filename_conflicts(output_folder, filenames):
    """Check for filename conflicts and return list of conflicts."""
    conflicts = []
    for filename in filenames:
        full_path = os.path.join(output_folder, filename)
        if os.path.exists(full_path):
            conflicts.append(filename)
    return conflicts


def preview_renaming(files_to_process, naming_settings):
    """Show preview of how files will be renamed."""
    print("\n📋 Renaming Preview:")
    print("┌─────────────────────────┬─────────────────────────┐")
    print("│ Original Name           │ New Name                │")
    print("├─────────────────────────┼─────────────────────────┤")
    
    preview_count = min(5, len(files_to_process))
    for i in range(preview_count):
        original = os.path.basename(files_to_process[i])
        new_name = generate_filename(files_to_process[i], i + 1, naming_settings)
        print(f"│ {original[:23]:23} │ {new_name[:23]:23} │")
    
    if len(files_to_process) > preview_count:
        remaining = len(files_to_process) - preview_count
        print(f"│ ... and {remaining} more files     │ ... and {remaining} more files     │")
    
    print("└─────────────────────────┴─────────────────────────┘")


def apply_watermark(image, watermark_path, watermark_size, position, opacity, margin_percent):
    """Apply watermark to an image."""
    try:
        # Load and prepare watermark
        watermark = load_and_prepare_watermark(
            watermark_path, 
            image.width, 
            watermark_size, 
            opacity
        )
        
        if watermark is None:
            return image  # Return original image if watermark failed
        
        # Calculate margin in pixels (percentage of smaller image dimension)
        margin_pixels = int(min(image.width, image.height) * (margin_percent / 100))
        
        # Calculate position
        wm_position = calculate_watermark_position(
            (image.width, image.height),
            (watermark.width, watermark.height),
            position,
            margin_pixels
        )
        
        # Create a copy of the image to avoid modifying the original
        result_image = image.copy()
        
        # Apply watermark
        result_image.paste(watermark, wm_position, watermark)
        
        return result_image
        
    except Exception as e:
        print(f"\n❌ Error applying watermark: {e}")
        return image  # Return original image on error


def batch_square(folder_path, output_folder, side_length, background_color, use_tags, tag, jpeg_quality, watermark_settings=None, naming_settings=None):
    if not os.path.exists(folder_path):
        print(f"❌ Folder doesn't exist: {folder_path}")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files_to_process = get_files_with_tag(folder_path, tag) if use_tags else [os.path.join(
        folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files_to_process:
        print(f"❌ Folder is empty or contains no images: {folder_path}")
        return

    output_size = 1080
    target_size = int(output_size * (side_length / 100))

    processed_count = 0
    error_count = 0
    
    for i, file_path in enumerate(tqdm(files_to_process, desc="Processing Images", unit="file"), 1):
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (handles RGBA, P mode, etc.)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                scale = target_size / max(img.width, img.height)
                new_width = int(img.width * scale)
                new_height = int(img.height * scale)
                
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                new_img = Image.new('RGB', (output_size, output_size), background_color)
                position = ((output_size - new_width) // 2, (output_size - new_height) // 2)
                new_img.paste(resized_img, position)
                
                # Apply watermark if enabled
                if watermark_settings and watermark_settings.get('use_watermark') == 'yes':
                    new_img = apply_watermark(
                        new_img,
                        watermark_settings['watermark_path'],
                        int(watermark_settings['watermark_size']),
                        watermark_settings['watermark_position'],
                        int(watermark_settings['watermark_opacity']),
                        int(watermark_settings['watermark_margin'])
                    )
                
                # Generate filename based on naming settings
                if naming_settings:
                    new_filename = generate_filename(file_path, i, naming_settings)
                else:
                    # Default behavior: keep original name with .jpg extension
                    original_base = os.path.splitext(os.path.basename(file_path))[0]
                    new_filename = f"{original_base}.jpg"
                
                output_path = os.path.join(output_folder, new_filename)
                
                new_img.save(output_path, 'JPEG', quality=jpeg_quality, optimize=True)
                processed_count += 1
                
        except Exception as e:
            error_count += 1
            print(f"\n❌ Error processing {os.path.basename(file_path)}: {e}")
            continue
    
    print(f"\n✅ Processing complete: {processed_count} images processed, {error_count} errors")


# Main execution logic
def main():
    print_header()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = ask_or_load_config(script_dir)
    settings = config['SETTINGS']
    
    print_section("Folder Selection")
    current_directory = os.getcwd()
    
    print("📁 Select your source folder containing the photos to process:")
    input_folder = get_folder_path("   Source folder", current_directory)
    
    print("\n📁 Select where to save the processed photos:")
    default_output = os.path.join(current_directory, "output")
    output_folder = get_folder_path("   Output folder", default_output, create_if_missing=True)
    
    # Preview files to be processed
    print_section("File Preview")
    print("🔍 Scanning for images...")
    
    # Get all image files first
    all_image_files = [
        os.path.join(input_folder, f) for f in os.listdir(input_folder) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    
    # Get files to process based on settings
    if settings['use_tags'] == 'yes':
        files_to_process = get_files_with_tag(input_folder, settings.get('tag', 'To Publish'))
        skipped_count = len(all_image_files) - len(files_to_process)
        
        if skipped_count > 0:
            print(f"ℹ️  Found {len(all_image_files)} total images, {skipped_count} skipped (not tagged with '{settings.get('tag', 'To Publish')}')")
    else:
        files_to_process = all_image_files
        skipped_count = 0
    
    if not files_to_process:
        if settings['use_tags'] == 'yes':
            print(f"⚠️  No images found to process!")
            print(f"   Found {len(all_image_files)} total images, but none are tagged with '{settings.get('tag', 'To Publish')}'")
            print(f"   Tag some photos in Finder or disable tag filtering in configuration.")
        else:
            print("❌ No images found to process!")
            print(f"   Make sure the folder contains PNG, JPG, or JPEG files.")
        return
    
    # Prepare naming settings
    naming_settings = {
        'naming_pattern': settings.get('naming_pattern', 'original'),
        'naming_prefix': settings.get('naming_prefix', 'Photo'),
        'naming_event': settings.get('naming_event', 'Event'),
        'naming_include_date': settings.get('naming_include_date', 'yes'),
        'naming_padding': settings.get('naming_padding', '3')
    }
    
    # Show renaming preview if not using original names
    if naming_settings['naming_pattern'] != 'original':
        preview_renaming(files_to_process, naming_settings)
        
        # Check for filename conflicts
        new_filenames = [generate_filename(f, i+1, naming_settings) for i, f in enumerate(files_to_process)]
        conflicts = check_filename_conflicts(output_folder, new_filenames)
        if conflicts:
            print(f"\n⚠️  {len(conflicts)} filename conflicts detected:")
            for conflict in conflicts[:5]:  # Show first 5 conflicts
                print(f"   • {conflict}")
            if len(conflicts) > 5:
                print(f"   • ... and {len(conflicts)-5} more")
            
            overwrite = get_user_choice("Overwrite existing files?", ["y", "n"], "n")
            if overwrite == "n":
                print("\n❌ Processing cancelled to avoid overwriting files.")
                return
    
    # Confirm processing
    if not confirm_processing(input_folder, output_folder, len(files_to_process)):
        print("\n❌ Processing cancelled by user.")
        return
    
    # Start processing
    print_section("Processing Images")
    
    # Prepare watermark settings
    watermark_settings = None
    if settings.get('use_watermark') == 'yes':
        watermark_settings = {
            'use_watermark': settings['use_watermark'],
            'watermark_path': settings['watermark_path'],
            'watermark_position': settings.get('watermark_position', 'bottom-center'),
            'watermark_size': settings.get('watermark_size', '14'),
            'watermark_opacity': settings.get('watermark_opacity', '100'),
            'watermark_margin': settings.get('watermark_margin', '17')
        }
    
    batch_square(
        input_folder,
        output_folder,
        int(settings['side_length']),
        tuple(map(int, settings['background_color'].split(','))),
        settings['use_tags'] == 'yes',
        settings.get('tag', 'To Publish'),
        int(settings['jpeg_quality']),
        watermark_settings,
        naming_settings
    )
    
    print("\n🎉 All done! Your party pictures are ready for social media!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your inputs and try again.")

