import tkinter as tk
from core.pet_base import Pet  # Import the Pet class from your project structure
from utils.helpers import make_window_transparent  # For transparency
from pets.goose import Goose  # Import the Goose pet class from your project structure

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-transparentcolor", "black")
    root.geometry("100x100+200+200")
    root.overrideredirect(True)

    pet = Pet(root, name="Roasty")


    pet.draw()

    # Randomly move horizontally or vertically after a random time using move_horizontally or move_vertically methods
    pet.move_randomly()

    pet.start_screenshot_task()  # Start periodic screenshot task

    root.mainloop()


