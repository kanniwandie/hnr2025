import tkinter as tk
import random
import os
from utils.helpers import take_screenshot
from pets.behaviors.interactions import generate_roast_from_image_sequence
from gui.overlay import display_response_above_pet
from gui.utils import load_gif

class Pet:
    DIRECTIONS = {"horizontal": "horizontal", "vertical": "vertical"}

    def __init__(self, window, name="Pet", width=1000, height=1000):
        self.window = window
        self.name = name
        self.width = width
        self.height = height
        self.is_grounded = False
        self.moving = True
        self.canvas = None
        self.facing_right = True  # Track the pet's facing direction

        # Animation placeholders
        self.frames = []
        self.current_frame_index = 0
        self.image_id = None

        # Animation poses
        self.poses = {
            "idle": "assets/pets/duck/animations/Idle.gif",
            "crouch": "assets/pets/duck/animations/Crouching.gif",
            "jump": "assets/pets/duck/animations/Jumping.gif",
            "walk": "assets/pets/duck/animations/Walking.gif",
            "dead": "assets/pets/duck/animations/Dead.gif",
            "run": "assets/pets/duck/animations/Running.gif",
        }

        # Screenshot management
        self.screenshots = []
        self.max_screenshots = 5

        # Set initial position
        self.set_starting_position()

    def set_starting_position(self):
        """Set the pet's starting position to the bottom-middle of the screen."""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = screen_height - self.height
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def set_pose(self, pose_name):
        """Switch the pet's animation to the given pose."""
        if pose_name in self.poses:
            self.load_and_display_gif(self.poses[pose_name])
        else:
            print(f"Pose '{pose_name}' not found!")

    def apply_gravity(self):
        """Apply gravity to make the pet fall."""
        if self.is_grounded:
            return

        screen_height = self.window.winfo_screenheight()
        current_x, current_y = self.window.winfo_x(), self.window.winfo_y()

        if current_y + self.height < screen_height:
            self.window.geometry(f"{self.width}x{self.height}+{current_x}+{current_y + 10}")  # Stronger gravity (10 pixels)
            self.window.after(30, self.apply_gravity)  # Faster updates (30 ms)
        else:
            self.is_grounded = True
            self.window.geometry(f"{self.width}x{self.height}+{current_x}+{screen_height - self.height}")

    def draw(self):
        """Draw the pet on the screen with its idle animation."""
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.pack()
        self.set_pose("idle")
        self.canvas.bind("<Button-1>", self.interact)

    def load_and_display_gif(self, file_path):
        """Load a GIF and start animating it."""
        self.frames = load_gif(file_path, self.width, self.height)
        if not self.frames:
            print("Error: No frames loaded from GIF!")
            return

        # Mirror frames if facing left
        if not self.facing_right:
            self.frames = [frame.transpose(method="flip") for frame in self.frames]

        self.image_id = self.canvas.create_image(self.width // 2, self.height // 2, image=self.frames[0])
        self.animate_gif()

    def animate_gif(self):
        """Cycle through the GIF frames."""
        if self.frames:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame_index])
            self.window.after(100, self.animate_gif)

    def move_horizontally(self, n):
        """Move the pet horizontally by n pixels."""
        self.set_pose("walk")

        screen_width = self.window.winfo_screenwidth()
        current_x, current_y = self.window.winfo_x(), self.window.winfo_y()
        new_x = max(0, min(current_x + n, screen_width - self.width))

        # Update facing direction
        if n > 0 and not self.facing_right:
            self.facing_right = True
            self.load_and_display_gif(self.poses["walk"])  # Reload GIF to face right
        elif n < 0 and self.facing_right:
            self.facing_right = False
            self.load_and_display_gif(self.poses["walk"])  # Reload GIF to face left

        self.window.geometry(f"{self.width}x{self.height}+{new_x}+{current_y}")
        self.set_pose("idle")

    def jump(self, n):
        """Make the pet jump by n pixels."""
        self.is_grounded = False
        self.set_pose("jump")

        current_x, current_y = self.window.winfo_x(), self.window.winfo_y()
        new_y = max(0, current_y - n)

        self.window.geometry(f"{self.width}x{self.height}+{current_x}+{new_y}")
        self.window.after(300, self.apply_gravity)
        self.window.after(500, lambda: self.set_pose("idle"))

    def move_randomly(self):
        """Move the pet randomly on the screen."""
        direction, distance = self.randomize_direction()

        if direction == self.DIRECTIONS["horizontal"]:
            self.move_horizontally(distance)
        elif direction == self.DIRECTIONS["vertical"]:
            self.jump(abs(distance))  # Ensure positive distance for jumping

        random_interval = random.randint(1000, 2000)
        self.window.after(random_interval, self.move_randomly)

    def randomize_direction(self):
        """Randomly choose the direction and distance to move. With more probability for horizontal movement."""
        direction = random.choices(list(self.DIRECTIONS.values()), weights=[0.7, 0.3], k=1)[0]

        # vertical movement distance is longer for more visible effect
        distance = random.randint(50, 100) if direction == self.DIRECTIONS["horizontal"] else random.randint(100, 200)

        return direction, distance

    def interact(self, event):
        """Handle interactions."""
        action = random.choice(["jump", "roast", "say_hi", "grow_shrink"])
        if action == "jump":
            self.jump(50)
        elif action == "roast":
            self.roast_user()
        elif action == "say_hi":
            display_response_above_pet(self.window, f"Hi! I'm {self.name}!")
        elif action == "grow_shrink":
            self.grow_and_shrink()

    def roast_user(self):
        """Generate a roast based on screenshots."""
        roast = generate_roast_from_image_sequence("screenshots")
        display_response_above_pet(self.window, roast)

    def start_screenshot_task(self):
        """Start the periodic screenshot task."""
        try:
            screenshot_path = take_screenshot()
            self.screenshots.append(screenshot_path)

            if len(self.screenshots) > self.max_screenshots:
                old_screenshot = self.screenshots.pop(0)
                os.remove(old_screenshot)

            print(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
        self.window.after(5000, self.start_screenshot_task)


    def grow_and_shrink(self):
        """Make the pet grow for a while then shrink."""

        def grow():
            self.window.geometry(f"{self.width * 2}x{self.height * 2}")
            self.window.after(1000, shrink)

        def shrink():
            self.window.geometry(f"{self.width}x{self.height}")

        grow()


