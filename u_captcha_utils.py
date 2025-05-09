import os
from pathlib import Path

CAPTCHAS_DIR = Path('./captchas')

def get_captcha_path(filename):
    """Get the full path for a file in the captchas directory."""
    return str(CAPTCHAS_DIR / filename) 