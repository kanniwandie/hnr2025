from ctypes import windll
from PIL import ImageGrab
from datetime import datetime
import os

import tkinter as tk

def make_window_transparent(window, alpha=0.5):
    """
    Configure the Tkinter window to be transparent and always on top.

    Parameters:
    - window: The Tkinter window to configure.
    - alpha: Transparency level (0.0 = fully transparent, 1.0 = fully opaque).
    """
    # Set the window to be always on top
    window.attributes('-topmost', True)
    # Remove window decorations (title bar, etc.)
    window.overrideredirect(True)
    # Set the window transparency level
    window.attributes('-alpha', alpha)

def take_screenshot():
    """Take a screenshot and save it."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = f"screenshots/screenshot_{timestamp}.png"
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_path)
    return screenshot_path
