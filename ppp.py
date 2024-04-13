from PIL import Image
import os


def batch_square(folder_path, output_folder, side_length=95, background_color=(100, 0, 180)):
    # Assurez-vous que le dossier de sortie existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Taille fixe de l'image de sortie
    output_size = 1080
    # Calcul de la nouvelle taille cible
    target_size = int(output_size * (side_length / 100))

    # Parcourez tous les fichiers dans le dossier spécifié
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, filename)
            img = Image.open(file_path)

            # Calculer la nouvelle taille de l'image pour que le côté le plus long corresponde à target_size
            scale = target_size / max(img.width, img.height)
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)

            # Redimensionner l'image en conservant les proportions
            resized_img = img.resize(
                (new_width, new_height), Image.Resampling.LANCZOS)

            # Créer une nouvelle image avec le fond de couleur et centrer l'image redimensionnée
            new_img = Image.new(
                'RGB', (output_size, output_size), color=background_color)
            position = ((output_size - new_width) // 2,
                        (output_size - new_height) // 2)
            new_img.paste(resized_img, position)

            # Sauvegarder l'image
            new_img.save(os.path.join(output_folder, filename))


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

# Traitement des entrées avec des valeurs par défaut
side_length = int(side_length) if side_length else 95
if background_color_input:
    background_color = tuple(map(int, background_color_input.split(',')))
else:
    background_color = (100, 0, 180)

batch_square(input_folder, output_folder, side_length, background_color)
