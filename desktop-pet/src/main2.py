import tkinter as tk
import random
import os
from utils.helpers import take_screenshot
from pets.behaviors.interactions import generate_roast_from_image_sequence
from gui.overlay import display_response_above_pet
from gui.utils import load_gif

# Global variables
window = None
canvas = None
image_id = None
frames = []
current_frame_index = 0
width = 100
height = 100
is_grounded = False
facing_right = True
poses = {
    "idle": "assets/pets/duck/animations/Idle.gif",
    "crouch": "assets/pets/duck/animations/Crouching.gif",
    "jump": "assets/pets/duck/animations/Jumping.gif",
    "walk": "assets/pets/duck/animations/Walking.gif",
    "dead": "assets/pets/duck/animations/Dead.gif",
    "run": "assets/pets/duck/animations/Running.gif",
}
screenshots = []
max_screenshots = 5


# -------------------------------------------------------------------- Pet Settings --------------------------------------------------------------------

def set_starting_position():
    """Set the pet's starting position to the bottom-middle of the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = screen_height - height
    window.geometry(f"{width}x{height}+{x}+{y}")

def set_pose(pose_name):
    """Switch the pet's animation to the given pose."""
    if pose_name in poses:
        load_and_display_gif(poses[pose_name])
    else:
        print(f"Pose '{pose_name}' not found!")

def draw_pet():
    """Draw the pet on the screen with its idle animation."""
    global canvas
    canvas = tk.Canvas(window, width=width, height=height, bg="black", highlightthickness=0)
    canvas.pack()
    set_pose("idle")
    canvas.bind("<Button-1>", interact)

    
def load_and_display_gif(file_path):
    """Load a GIF and start animating it."""
    global frames, image_id, current_frame_index
    frames = load_gif(file_path, width, height)
    if not frames:
        print("Error: No frames loaded from GIF!")
        return

    # Mirror frames if facing left
    if not facing_right:
        frames = [frame.transpose(method="flip") for frame in frames]

    image_id = canvas.create_image(width // 2, height // 2, image=frames[0])
    animate_gif()

# -------------------------------------------------------------------- Pet Actions --------------------------------------------------------------------
def move_randomly():
    """Move the pet randomly on the screen."""
    direction, distance = randomize_direction()

    if direction == "horizontal":
        move_horizontally(distance)
    elif direction == "vertical":
        jump(abs(distance))  # Ensure positive distances for jumping

    random_interval = random.randint(1000, 2000)
    window.after(random_interval, move_randomly)

def interact(event):
    """Handle interactions."""
    action = random.choice(["jump", "roast", "say_hi"])
    if action == "say_hi":
        display_response_above_pet(window, f"Hi! I'm your pet!")

def roast_user():
    """Generate a roast based on screenshots."""
    roast = generate_roast_from_image_sequence("screenshots")
    display_response_above_pet(window, roast)

def start_screenshot_task():
    """Start the periodic screenshot task."""
    global screenshots
    try:
        screenshot_path = take_screenshot()
        screenshots.append(screenshot_path)

        if len(screenshots) > max_screenshots:
            old_screenshot = screenshots.pop(0)
            os.remove(old_screenshot)

        print(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")
    window.after(5000, start_screenshot_task)

# ---------------------------------------------------------------- Pet Mini Actions ----------------------------------------------------------------
def move_horizontally(n):
    """Move the pet horizontally by n pixels."""
    global facing_right
    set_pose("walk")

    screen_width = window.winfo_screenwidth()
    current_x, current_y = window.winfo_x(), window.winfo_y()
    new_x = max(0, min(current_x + n, screen_width - width))

    # Update facing direction
    if n > 0 and not facing_right:
        facing_right = True
        load_and_display_gif(poses["walk"])  # Reload GIF to face right
    elif n < 0 and facing_right:
        facing_right = False
        load_and_display_gif(poses["walk"])  # Reload GIF to face left

    window.geometry(f"{width}x{height}+{new_x}+{current_y}")
    set_pose("idle")

def jump(n):
    """Make the pet jump by n pixels."""
    global is_grounded
    is_grounded = False
    set_pose("jump")

    current_x, current_y = window.winfo_x(), window.winfo_y()
    new_y = max(0, current_y - n)

    window.geometry(f"{width}x{height}+{current_x}+{new_y}")
    window.after(300, apply_gravity)
    window.after(500, lambda: set_pose("idle"))

# -------------------------------------------------------------------- Util Methods --------------------------------------------------------------------

def animate_gif():
    """Cycle through the GIF frames."""
    global current_frame_index
    if frames:
        current_frame_index = (current_frame_index + 1) % len(frames)
        canvas.itemconfig(image_id, image=frames[current_frame_index])
        window.after(100, animate_gif)

def randomize_direction():
    """Randomly choose the direction and distance to move."""
    direction = random.choice(["horizontal", "vertical"])
    distance = random.randint(50, 100) if direction == "horizontal" else random.randint(50, 100)
    return direction, distance


# -------------------------------------------------------------------- World Logic --------------------------------------------------------------------

def apply_gravity():
    """Apply gravity to make the pet fall."""
    global is_grounded
    if is_grounded:
        return

    screen_height = window.winfo_screenheight()
    virtual_floor = screen_height - height - 50  # Raise the floor by 50 pixels
    current_x, current_y = window.winfo_x(), window.winfo_y()

    if current_y + height < virtual_floor:
        window.geometry(f"{width}x{height}+{current_x}+{current_y + 10}")
        window.after(30, apply_gravity)
    else:
        is_grounded = True
        window.geometry(f"{width}x{height}+{current_x}+{virtual_floor}")





















if __name__ == "__main__":
    window = tk.Tk()
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.attributes("-transparentcolor", "black")
    window.geometry("100x100+200+200")
    set_starting_position()
    draw_pet()
    move_randomly()
    start_screenshot_task()
    window.mainloop()
