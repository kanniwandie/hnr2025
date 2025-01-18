import tkinter as tk
import random
import os
from datetime import datetime
from PIL import ImageGrab  # For taking screenshots
from utils.helpers import take_screenshot


class Pet:
    def __init__(self, window, name="Pet", width=100, height=100):
        self.window = window
        self.name = name
        self.width = width
        self.height = height
        self.x_direction = random.choice([-1, 1])
        self.y_direction = random.choice([-1, 1])
        self.moving = True
        self.canvas = None

        # Screenshot management
        self.screenshots = []  # List to store file paths of the latest screenshots
        self.max_screenshots = 5  # Maximum number of screenshots to store

    def draw(self):
        """Draw the pet on the screen."""
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="blue", highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_oval(10, 10, self.width - 10, self.height - 10, fill="orange", outline="black")
        self.canvas.bind("<Button-1>", self.interact)

    def move(self):
        """Handle pet movement."""
        if self.moving:
            current_x, current_y = self.window.winfo_x(), self.window.winfo_y()
            new_x = current_x + self.x_direction * 5
            new_y = current_y + self.y_direction * 5

            # Check screen boundaries
            screen_width, screen_height = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
            if new_x < 0 or new_x > screen_width - self.width:
                self.x_direction *= -1
            if new_y < 0 or new_y > screen_height - self.height:
                self.y_direction *= -1

            # Update window position
            self.window.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")
            self.window.after(50, self.move)

    def start_screenshot_task(self):
        """Start the periodic screenshot task."""
        try:
            # Take a screenshot
            screenshot_path = take_screenshot()

            # Add the screenshot path to the list
            self.screenshots.append(screenshot_path)

            # Remove older screenshots if the limit is exceeded
            if len(self.screenshots) > self.max_screenshots:
                old_screenshot = self.screenshots.pop(0)
                os.remove(old_screenshot)  # Delete the oldest screenshot from disk

            print(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            
        self.window.after(5000, self.start_screenshot_task)  # Schedule the next screenshot in 5 seconds

    def interact(self, event):
        """Handle interactions."""
        from gui.overlay import display_response_above_pet
        display_response_above_pet(self.window, f"Hi! I'm {self.name}!")

    def roast_user(self):
        """Generate a roast based on screenshots."""
        if self.screenshots:
            roast = f"Nice desktop, but you should clean up your files. Check {self.screenshots[-1]}!"
        else:
            roast = "I have nothing to roast you about... yet!"
        from gui.overlay import display_response_above_pet
        display_response_above_pet(self.window, roast)

    def randomize_direction(self):
        """Randomize movement direction."""
        self.x_direction = random.choice([-1, 1])
        self.y_direction = random.choice([-1, 1])
