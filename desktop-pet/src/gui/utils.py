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

from PIL import Image, ImageTk

def load_gif(file_path, width, height):
    """
    Load a GIF and return a list of ImageTk.PhotoImage frames.
    If the file is a static image (e.g., PNG), it returns a list with one frame.
    """
    frames = []
    try:
        gif = Image.open(file_path)
        while True:
            frame = ImageTk.PhotoImage(gif.resize((width, height), Image.Resampling.LANCZOS))
            frames.append(frame)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass  # End of GIF
    return frames

