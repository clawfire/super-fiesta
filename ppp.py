#!/usr/bin/env python3

import os
import subprocess
import sys
from configparser import ConfigParser
from PIL import Image
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
    
    save_config(config, config_file)
    print("\n✅ Configuration saved!")
    
    return config


def batch_square(folder_path, output_folder, side_length, background_color, use_tags, tag, jpeg_quality):
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
    
    for file_path in tqdm(files_to_process, desc="Processing Images", unit="file"):
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
                
                output_path = os.path.join(output_folder, os.path.basename(file_path))
                # Ensure output is always JPEG
                if not output_path.lower().endswith('.jpg'):
                    base_name = os.path.splitext(output_path)[0]
                    output_path = base_name + '.jpg'
                
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
    
    # Confirm processing
    if not confirm_processing(input_folder, output_folder, len(files_to_process)):
        print("\n❌ Processing cancelled by user.")
        return
    
    # Start processing
    print_section("Processing Images")
    batch_square(
        input_folder,
        output_folder,
        int(settings['side_length']),
        tuple(map(int, settings['background_color'].split(','))),
        settings['use_tags'] == 'yes',
        settings.get('tag', 'To Publish'),
        int(settings['jpeg_quality'])
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

