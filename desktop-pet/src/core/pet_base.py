import tkinter as tk
import random
import os
from utils.helpers import take_screenshot
from pets.behaviors.interactions import generate_roast_from_image_sequence
from gui.overlay import display_response_above_pet
from gui.utils import load_gif


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

        # Placeholder for animation
        self.frames = []  # List of frames
        self.current_frame_index = 0
        self.image_id = None  # Canvas image ID

        # Mapping of pose to image/gif file
        self.current_pose = "idle"
        self.poses = {
            "idle": "assets/pets/duck/animations/Idle.gif",
            "crouch": "assets/pets/duck/animations/Crouching.gif",
            "jump": "assets/pets/duck/animations/Jumping.gif",
            "walk": "assets/pets/duck/animations/Walking.gif",
            "dead": "assets/pets/duck/animations/Dead.gif",
            "run": "assets/pets/duck/animations/Running.gif",
        }

        # Screenshot management
        self.screenshots = []  # List to store file paths of the latest screenshots
        self.max_screenshots = 5  # Maximum number of screenshots to store

    def draw(self):
        """Draw the pet on the screen with its idle animation."""
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="blue", highlightthickness=0)
        self.canvas.pack()

        self.load_and_display_gif(self.poses["idle"])

        # Bind interaction event
        self.canvas.bind("<Button-1>", self.interact)


    def load_and_display_gif(self, file_path):
        """Load a GIF and start animating it."""
        self.frames = load_gif(file_path, self.width, self.height)
        if not self.frames:
            print("Error: No frames loaded from GIF!")
            return

        # Display the first frame
        self.image_id = self.canvas.create_image(self.width // 2, self.height // 2, image=self.frames[0])
        self.animate_gif()

    def animate_gif(self):
        """Cycle through the GIF frames."""
        if self.frames:
            # Update the canvas with the current frame
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame_index])

            # Schedule the next frame update
            self.window.after(100, self.animate_gif)  # Adjust the frame rate as needed


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
        display_response_above_pet(self.window, f"Hi! I'm {self.name}!")

    def roast_user(self):
        """Generate a roast based on screenshots."""
        roast = generate_roast_from_image_sequence("screenshots")
        display_response_above_pet(self.window, roast)

    def randomize_direction(self):
        """Randomize movement direction."""
        self.x_direction = random.choice([-1, 1])
        self.y_direction = random.choice([-1, 1])
