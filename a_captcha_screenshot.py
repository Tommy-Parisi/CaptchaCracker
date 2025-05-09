import pyautogui
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image
import cv2
import numpy as np
from u_captcha_utils import get_captcha_path

# --- Edge Locate Method ---
def edgeLocate(reference_path, screen_image, debug=False):
    """
    Thomas Parisi
    Locates the position of a reference image within a screenshot using Canny edge detection and template matching.
    This method is not recommended, it is not as consistent as templateLocate method but serves as an alternative.
    *** I recommend using the templateLocate method instead, or improving this one before use! ***

    :param reference_path: Path to the reference image file.
    :param screen_image: Screenshot image (as a PIL Image) to search within.
    :param debug: If True, displays a debug visualization of the match.
    :return: Tuple (x, y, width, height) of the top-left corner and dimensions of the matched region,
             or None if no good match was found.
    """
    ref_gray = cv2.imread(get_captcha_path(reference_path), cv2.IMREAD_GRAYSCALE)
    if ref_gray is None:
        print("[Error] Could not load reference image.")
        return None

    ref_edges = cv2.Canny(ref_gray, 100, 200)
    screen_gray = cv2.cvtColor(np.array(screen_image), cv2.COLOR_RGB2GRAY)
    screen_edges = cv2.Canny(screen_gray, 100, 200)

    sobel_x = cv2.Sobel(screen_edges, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(screen_edges, cv2.CV_64F, 0, 1, ksize=3)
    screen_edges = cv2.convertScaleAbs(cv2.magnitude(sobel_x, sobel_y))

    result = cv2.matchTemplate(screen_edges, ref_edges, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val <= 0.12:
        print(f"[EdgeMatch] No strong match found (max_val={max_val:.2f})")
        return None

    top_left = max_loc
    h, w = ref_edges.shape
    bottom_right = (top_left[0] + w, top_left[1] + h)

    print(f"[EdgeMatch] Match found at {top_left} with score {max_val:.2f}")

    if debug:
        vis = cv2.cvtColor(screen_gray, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(vis, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imshow("Edge Locate Match", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return (top_left[0], top_left[1], w, h)

# --- Template Matching Method ---
def templateLocate(reference_path, min_conf=0.3, max_conf=0.9, step=0.1):
    """
    Uses PyAutoGUI's image recognition to locate a reference image on the screen with decreasing confidence levels.

    :param reference_path: Path to the reference image file.
    :param min_conf: Minimum confidence threshold to attempt matching.
    :param max_conf: Starting confidence threshold.
    :param step: Step size to decrement confidence per iteration.
    :return: Tuple (x, y, width, height) of the matched region if found, or None if not found.
    """
    print("[PyAutoGUI] Starting template matching...")
    conf = max_conf
    while round(conf, 2) >= min_conf:
        try:
            print(f"[PyAutoGUI] Trying confidence: {conf:.2f}")
            location = pyautogui.locateOnScreen(get_captcha_path(reference_path), confidence=conf)
            if location and not (location.left == 0 and location.top == 0):
                print(f"[PyAutoGUI] Match found at {location} with confidence {conf:.2f}")
                return (location.left, location.top, location.width, location.height)
        except pyautogui.ImageNotFoundException:
            print(f"[PyAutoGUI] No match at confidence {conf:.2f}")
        conf = round(conf - step, 2)
    return None

def get_captcha():
    """
    Automates the testbed CAPTCHA form using Selenium and PyAutoGUI, captures the CAPTCHA image, and saves it locally.

    - Opens a browser to the local CAPTCHA HTML form.
    - Fills out example form fields.
    - Injects JavaScript to prevent auto-submission and page reloads.
    - Clicks the CAPTCHA widget and waits for it to render.
    - Uses template matching to find and crop the CAPTCHA area from a full-screen screenshot.
    - Saves the cropped image as 'captcha_image.png' in the configured path.

    :return: Tuple (x, y, width, height) of the detected CAPTCHA area, or None if not found.
    """
    # --- Selenium Setup ---
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)

    driver.get("http://127.0.0.1:5500/Captcha/Replit%20HTML%20file.html")
    print("Application title is", driver.title)
    print("Application url is", driver.current_url)

    # --- Fill in form ---
    inputBox = driver.find_element(By.XPATH, "//form//input")
    inputBox.send_keys("Roberto")
    inputBox = driver.find_element(By.XPATH, "//form//input[2]")
    inputBox.send_keys("1234")

    # Block reloads and auto-submit / only works when the website does not have a CSP restriction
    driver.execute_script("""
        const form = document.querySelector("form");
        if (form) {
            form.addEventListener("submit", (e) => {
                console.log("[JS] Preventing form submit...");
                e.preventDefault();
            }, true);
        }

        const recaptcha = document.querySelector(".g-recaptcha");
        if (recaptcha) {
            recaptcha.removeAttribute("data-callback");
        }

        window.onbeforeunload = function() {
            return "Blocked reload";
        };
    """)
    print("[✔] JS protection injected to block reloads and callbacks.")

    # --- Click on CAPTCHA ---
    capBtn = driver.find_element(By.CLASS_NAME, 'g-recaptcha')
    capBtn.click()
    print("[✔] CAPTCHA clicked.")

    # --- Wait for the CAPTCHA to fully render ---
    time.sleep(3)
    print('Waiting Complete\n')

    # --- Locate CAPTCHA ---
    reference_image = 'reference-image2.png'
    screenshot = pyautogui.screenshot()

    captcha_coords = templateLocate(reference_image)
    #captcha_coords = edgeLocate(reference_image, screenshot) #toggle which implementation to use 

    if captcha_coords:
        left, top, width, height = captcha_coords
        right = left + width
        bottom = top + height

        captcha_image = screenshot.crop((left, top, right, bottom))
        captcha_image.save(get_captcha_path('captcha_image.png'))
        print("Captcha image saved as 'captcha_image.png'")
    else:
        print("Captcha not found on the screen.")

    return captcha_coords