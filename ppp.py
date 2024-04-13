#!/usr/bin/env python3

import os
import subprocess
from PIL import Image


def get_files_with_tag(folder_path, tag):
    """Utilise mdfind pour récupérer les fichiers avec un tag spécifique dans un dossier."""
    query = f"kMDItemUserTags == '{tag}'"
    cmd = ['mdfind', '-onlyin', folder_path, query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        # Split et ignorer la dernière ligne vide
        return result.stdout.split('\n')[:-1]
    else:
        print("Erreur lors de la recherche des tags")
        return []


def batch_square(folder_path, output_folder, side_length=95, background_color=(100, 0, 180), use_tags=False, tag=None, jpeg_quality=95):
    # Assurez-vous que le dossier de sortie existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Taille fixe de l'image de sortie
    output_size = 1080
    # Calcul de la nouvelle taille cible
    target_size = int(output_size * (side_length / 100))

    files_to_process = [os.path.join(folder_path, f) for f in os.listdir(
        folder_path)] if not use_tags else get_files_with_tag(folder_path, tag)
    total_files = len(files_to_process)

    # Parcourez tous les fichiers dans le dossier spécifié ou filtré par tags
    for index, file_path in enumerate(files_to_process):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
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
            print(f"Progression: {
                  index + 1}/{total_files} fichiers traités.", end='\r')

    print()  # Pour s'assurer qu'on passe à la ligne suivante à la fin du traitement


# Demande des paramètres à l'utilisateur avec des valeurs par défaut
current_directory = os.getcwd()
input_folder = input(f"Entrez le chemin du dossier source ({
                     current_directory} par défaut) : ") or current_directory
output_folder = input("Entrez le chemin du dossier de sortie ('output' par défaut) : ") or os.path.join(
    current_directory, "output")
side_length = input(
    "Entrez le pourcentage de la taille pour l'image intégrée (95 par défaut) : ")
background_color_input = input(
    "Entrez la couleur de fond en format RGB (100,0,180 par défaut) : ")
jpeg_quality = input(
    "Entrez la qualité JPEG (1-100, où 100 est la meilleure qualité, 95 par défaut) : ")
use_tags = input(
    "Voulez-vous filtrer les images par tag ? (oui/non) : ").lower() == 'oui'
tag = input(
    "Entrez le tag à utiliser (par défaut 'To Publish') : ") or "To Publish"

# Traitement des entrées avec des valeurs par défaut
side_length = int(side_length) if side_length else 95
background_color = tuple(map(int, background_color_input.split(
    ','))) if background_color_input else (100, 0, 180)
jpeg_quality = int(jpeg_quality) if jpeg_quality else 95

batch_square(input_folder, output_folder, side_length,
             background_color, use_tags, tag, jpeg_quality)
