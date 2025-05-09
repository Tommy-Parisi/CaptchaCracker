from PIL import Image
import pyautogui
import time
import argparse
from u_captcha_utils import get_captcha_path

# BEWARE:DOES NOT PERFORM WELL ON ANYTHING OTHER THEN 3X3 GRID

def crop_image(image_path, top_section_height, bottom_section_height):
    """
    Crops a full CAPTCHA image into the top text section and the body grid (as one image).

    Saves the body as 'cropped_image.png' and the top section as 'captcha_top.png'.

    :param image_path: Path to the input CAPTCHA image.
    :param top_section_height: Height in pixels of the top text section.
    :param bottom_section_height: Height to remove from the bottom of the image.
    :return: None
    """
    image = Image.open(get_captcha_path(image_path))
    width, height = image.size 
    usable_height = height - top_section_height - bottom_section_height
    topImage = image.crop((0, 0, width, top_section_height)) # Crop the top section which contains text
    image = image.crop((0, top_section_height, width, usable_height + top_section_height))
    image.save(get_captcha_path("cropped_image.png")) # Saves the cropped image as cropped_image.png
    topImage.save(get_captcha_path("captcha_top.png"))

def manipulate_image(image_path, is_one_image, rows=None, columns=None):
    """
    Crop or split a CAPTCHA image depending on the is_grid flag.
    Decided we dont need to crop into a grid so this will never be called with is_one_image set to false

    :param image_path: Path to the image
    :param is_grid: True if the image is a grid (e.g. 3x3 CAPTCHA)
    :param rows: Number of rows (required if is_grid is True)
    :param columns: Number of columns (required if is_grid is True)
    """
    top_section_height = 250
    bottom_section_height = 120

    crop_image(image_path, top_section_height, bottom_section_height)
