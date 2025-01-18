import tkinter as tk
import random
from core.pet_base import Pet  # Inherits from the Pet class


class Goose(Pet):
    def __init__(self, window, name="Goose", width=120, height=120):
        super().__init__(window, name, width, height)  # Initialize base Pet class attributes
        self.goose_honk_count = 0  # Number of times the goose has honked
        self.is_angry = False  # Track whether the goose is angry
        self.steal_items = []  # List of items the goose has "stolen"

    def honk(self, event=None):
        """Make the goose honk and display a response above it."""
        self.goose_honk_count += 1
        from gui.overlay import display_response_above_pet
        display_response_above_pet(self.window, self, f"HONK! I'm a goose! ({self.goose_honk_count} honks)")

    def steal_mouse(self):
        """Simulate stealing the mouse by moving the goose to the cursor's position."""
        current_x, current_y = self.window.winfo_pointerx(), self.window.winfo_pointery()
        self.window.geometry(f"{self.width}x{self.height}+{current_x - self.width//2}+{current_y - self.height//2}")
        from gui.overlay import display_response_above_pet
        display_response_above_pet(self.window, "Honk! I've stolen your mouse!")

    def steal_item(self, item):
        """Add an item to the goose's stolen list."""
        self.steal_items.append(item)
        from gui.overlay import display_response_above_pet
        display_response_above_pet(self.window, f"I stole your {item}! HONK!")

    def random_prank(self):
        """Perform a random prank."""
        pranks = [self.honk, self.steal_mouse, lambda: self.steal_item("keyboard")]
        prank = random.choice(pranks)
        prank()  # Perform the randomly chosen prank

    def draw(self):
        """Override the draw method to make the goose look different."""
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_oval(10, 10, self.width - 10, self.height - 10, fill="gray", outline="black")  # A gray goose
        self.canvas.bind("<Button-1>", self.honk)  # Bind left-click to honk
