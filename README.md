# Super Fiesta: Your Party Picture Butler

Welcome to Super Fiesta, the ultimate tool designed to enhance your party pictures for social media sharing! This easy-to-use script transforms your images into perfectly square formats, ensuring they're primed for platforms like Instagram. Whether you're handling a batch of photos from a recent event or preparing images in advance, Super Fiesta streamlines the process, allowing you to customize size, background color, and more, all from your local folder.

Get started today and make your party pictures pop!

## Prerequisites

1. Clone the repository
2. Install the dependencies with `pip install -r requirements.txt`

## Usage

Run the script with `python party_picture_preparator.py` and follow the instructions. The script will ask you for the folder where the pictures are and will create a new folder with the edited pictures. It will also ask you for the maximum size of the pictures and the background color.

## Features

* Contain pictures in a square format easy to share on social media
* Can filter the pictures to edit by using macOS tags
* Can specify the folder where the pictures are when running the script
* Can specify the folder where the edited pictures will be saved when running the script
* Can specify the percent of the square size you want to use (for the longest side of the original picture)
* Can specify the background color when running the script
* Can specify the quality of the edited pictures when running the script

## Planned features / TODO

- [ ] Add a better GUI
- [ ] Add the possibility to add a watermark
- [ ] Add the possibility to specify the watermark position
- [ ] Add the possibility to specify the watermark size
- [ ] Add the possibility to specify the watermark transparency
- [ ] Add resizing options to also generate original ratio pictures but with lower size, optimized for web sharing in terms of quality and weight, including watermark
- [x] Persist the user preferences in a configuration file

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contact
Thibault Milan - hello@thibaultmilan.com

## Acknowledgments
* Thanks to [ROAST](https://dice.fm/promoters/roast-p9ky) London for the design inspiration
* Thanks to the Python community for the great libraries
