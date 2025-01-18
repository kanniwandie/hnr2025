from ctypes import windll
from PIL import ImageGrab
from datetime import datetime
import os
from ctypes import windll, wintypes

def take_screenshot():
    """Take a screenshot and save it."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = f"screenshots/screenshot_{timestamp}.png"
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_path)
    return screenshot_path
