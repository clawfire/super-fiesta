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
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        # Split and ignore the last empty line
        return result.stdout.split('\n')[:-1]
    else:
        print(f"❌ Error while searching for tags in the folder: {folder_path}")
        return []


def save_config(config, config_file='sf_config.ini'):
    with open(config_file, 'w') as f:
        config.write(f)


def load_config(config_file='sf_config.ini'):
    config = ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    return config


def ask_or_load_config():
    config = load_config()
    if 'SETTINGS' in config:
        return config
    else:
        config['SETTINGS'] = {
            'side_length': input("Enter the percentage size for the embedded image (95 by default): ") or '95',
            'background_color': input("Enter the background color in RGB format (100,0,180 by default): ") or '100,0,180',
            'jpeg_quality': input("Enter the JPEG quality (1-100, where 100 is the best quality, 95 by default): ") or '95',
            'use_tags': input("Do you want to filter images by tag? (Y/N, default Y): [Y/n] ").strip().lower() or 'y'
        }
        config['SETTINGS']['use_tags'] = 'yes' if config['SETTINGS']['use_tags'] in [
            'y', 'yes', ''] else 'no'
        if config['SETTINGS']['use_tags'] == 'yes':
            config['SETTINGS']['tag'] = input(
                "Enter the tag to use (default 'To Publish'): ") or 'To Publish'
        save_config(config)
        return config


def batch_square(folder_path, output_folder, side_length=95, background_color=(100, 0, 180), use_tags=False, tag=None, jpeg_quality=95):
    if not os.path.exists(folder_path):
        print(f"❌ Folder doesn't exist: {folder_path}")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not use_tags:
        files_to_process = [os.path.join(folder_path, f) for f in os.listdir(
            folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    else:
        files_to_process = get_files_with_tag(folder_path, tag)

    if not files_to_process:
        print(f"❌ Folder is empty or contains no images: {folder_path}")
        return

    output_size = 1080
    target_size = int(output_size * (side_length / 100))

    for file_path in tqdm(files_to_process, desc="Processing Images", unit="file"):
        img = Image.open(file_path)
        scale = target_size / max(img.width, img.height)
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        resized_img = img.resize(
            (new_width, new_height), Image.Resampling.LANCZOS)
        new_img = Image.new(
            'RGB', (output_size, output_size), background_color)
        position = ((output_size - new_width) // 2,
                    (output_size - new_height) // 2)
        new_img.paste(resized_img, position)
        new_img.save(os.path.join(output_folder, os.path.basename(
            file_path)), quality=jpeg_quality)


# Main execution logic
config = ask_or_load_config()
settings = config['SETTINGS']
current_directory = os.getcwd()
input_folder = input(f"Enter the path to the source folder ({
                     current_directory} by default): ") or current_directory
output_folder = input("Enter the path to the output folder ('output' by default): ") or os.path.join(
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
