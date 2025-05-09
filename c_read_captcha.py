import pytesseract
import cv2
import numpy as np
from u_captcha_utils import get_captcha_path

def modelize_text(text):
    """
    Maps a given OCR-extracted keyword or phrase to a canonical object class name.

    Handles normalization of common variations or phrasing of supported target labels 
    such as 'motorcycle', 'car', 'truck', 'bus', etc.

    We must do this to ensure that the text we get from the OCR is in a format that the YOLO model can understand,
    so we can not simply strip() or lower().

    :param text: The raw text extracted from the CAPTCHA (e.g., 'motor cycle', 'a bus', etc.)
    :return: Canonical object class (e.g., 'car', 'motorcycle', 'fire hydrant'), or original text if no match is found.
    """
    motorcycle = ['motorcycles', 'motorcycle', 'motor cycle', 'motor cycles', 'a motorcycle']
    car = ['cars', 'car', 'a car']
    truck = ['trucks', 'truck', 'a truck']
    bicycle = ['bicycles', 'bicycle', 'a bicycle']
    bus = ['buses', 'bus', 'a bus']
    fire_hydrant = ['fire hydrant', 'fire hydrants', 'a fire hydrant', 'hydrant', 'fire']

    if text in motorcycle:
        return 'motorcycle'
    elif text in car:
        return 'car'
    elif text in truck:
        return 'truck'
    elif text in bicycle:
        return 'bicycle'
    elif text in bus:
        return 'bus'
    elif text in fire_hydrant:
        return 'fire hydrant'
    else:
        return text

def extractObjectText(imagePath):
    """
    Extracts the main instruction text from the top section of a CAPTCHA image using OCR.

    - Converts the image to grayscale and applies binary thresholding to enhance text detection.
    - Uses Tesseract OCR to extract all detected words and their bounding box heights.
    - Selects the word with the largest text height, assuming it's the most prominent instruction.
    - Substitutes 'images' with 'error, found images'. <<<<<<<<<<<<< *** This is a bug!!!! about 1/5 of the time it reads 'images' instead of our object ***
    - Maps the result through `modelize_text` for normalization.

    :param imagePath: Path to the CAPTCHA image file (relative to configured CAPTCHA directory).
    :return: Normalized object class name (e.g., 'bus', 'bicycle') or raw text if unrecognized.
    """
    image = cv2.imread(get_captcha_path(imagePath))
    if image is None:
        print(f"Error: Could not load image from {imagePath}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    config = '--psm 6'
    all_text = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=config)

    max_height = 0
    large_text = ""

    for i in range(len(all_text['text'])):
        text = all_text['text'][i].strip()
        height = all_text['height'][i]
        if text and height > max_height:
            max_height = height
            large_text = text

    if large_text == "images": # Fix this bug in the future, you can compare the word to our dictionary or figure out a better way to do this
        large_text = "error, found images"

    return modelize_text(large_text)