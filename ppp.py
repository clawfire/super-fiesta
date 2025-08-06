#!/usr/bin/env python3

import os
import subprocess
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
    if 'SETTINGS' in config:
        print("Using existing configuration")
        # Validate existing config
        try:
            validate_config_value(config['SETTINGS']['side_length'], int, 1, 100)
            validate_config_value(config['SETTINGS']['background_color'], 'rgb')
            validate_config_value(config['SETTINGS']['jpeg_quality'], int, 1, 100)
        except (ValueError, KeyError) as e:
            print(f"❌ Invalid configuration: {e}")
            print("Please reconfigure:")
            config.clear()
    
    if 'SETTINGS' not in config:
        print("No configuration found, asking for user input")
        config['SETTINGS'] = {}
        
        while True:
            try:
                side_length = input("Enter the percentage size for the embedded image (95 by default): ") or '95'
                config['SETTINGS']['side_length'] = str(validate_config_value(side_length, int, 1, 100))
                break
            except ValueError as e:
                print(f"❌ {e}")
        
        while True:
            try:
                bg_color = input("Enter the background color in RGB format (100,0,180 by default): ") or '100,0,180'
                config['SETTINGS']['background_color'] = validate_config_value(bg_color, 'rgb')
                break
            except ValueError as e:
                print(f"❌ {e}")
        
        while True:
            try:
                quality = input("Enter the JPEG quality (1-100, where 100 is the best quality, 95 by default): ") or '95'
                config['SETTINGS']['jpeg_quality'] = str(validate_config_value(quality, int, 1, 100))
                break
            except ValueError as e:
                print(f"❌ {e}")
        
        use_tags = input("Do you want to filter images by tag? (Y/N, default Y): [Y/n] ").strip().lower() or 'y'
        config['SETTINGS']['use_tags'] = 'yes' if use_tags in ['y', 'yes', ''] else 'no'
        
        if config['SETTINGS']['use_tags'] == 'yes':
            config['SETTINGS']['tag'] = input("Enter the tag to use (default 'To Publish'): ") or 'To Publish'
        
        save_config(config, config_file)
    
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
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory is {script_dir}")
config = ask_or_load_config(script_dir)
settings = config['SETTINGS']
current_directory = os.getcwd()
input_folder = input(f"Enter the path to the source folder ({
                     current_directory} by default): ") or current_directory
output_folder = input(f"Enter the path to the output folder ('output' by default): ") or os.path.join(
    current_directory, "output")

batch_square(
    input_folder,
    output_folder,
    int(settings['side_length']),
    tuple(map(int, settings['background_color'].split(','))),
    settings['use_tags'] == 'yes',
    settings.get('tag', 'To Publish'),
    int(settings['jpeg_quality'])
)
