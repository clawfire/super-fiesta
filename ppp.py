#!/usr/bin/env python3

import os
import subprocess
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
        print("Error while searching for tags")
        return []


def batch_square(folder_path, output_folder, side_length=95, background_color=(100, 0, 180), use_tags=False, tag=None, jpeg_quality=95):
    # Check if the input folder exists
    if not os.path.exists(folder_path):
        print("❌ Folder doesn't exist")
        return  # Exit the function if the folder does not exist

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder or filtered by tags
    if not use_tags:
        files_to_process = [os.path.join(folder_path, f) for f in os.listdir(
            folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    else:
        files_to_process = get_files_with_tag(folder_path, tag)

    # Check if there are any files to process
    if not files_to_process:
        print("❌ Folder is empty or contains no images")
        return  # Exit the function if there are no images to process

    # Fixed size of the output image
    output_size = 1080
    # Calculate the new target size
    target_size = int(output_size * (side_length / 100))

    # Process all files in the specified folder with a progress bar
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


# Request parameters from the user with default values
current_directory = os.getcwd()
input_folder = input(f"Enter the path to the source folder ({
                     current_directory} by default): ") or current_directory
output_folder = input("Enter the path to the output folder ('output' by default): ") or os.path.join(
    current_directory, "output")
side_length = input(
    "Enter the percentage size for the embedded image (95 by default): ")
background_color_input = input(
    "Enter the background color in RGB format (100,0,180 by default): ")
jpeg_quality = input(
    "Enter the JPEG quality (1-100, where 100 is the best quality, 95 by default): ")
use_tags = input(
    "Do you want to filter images by tag? (yes/no): ").lower() == 'yes'
tag = input("Enter the tag to use (default 'To Publish'): ") or "To Publish"

# Process the inputs with default values
side_length = int(side_length) if side_length else 95
background_color = tuple(map(int, background_color_input.split(
    ','))) if background_color_input else (100, 0, 180)
jpeg_quality = int(jpeg_quality) if jpeg_quality else 95

batch_square(input_folder, output_folder, side_length,
             background_color, use_tags, tag, jpeg_quality)
