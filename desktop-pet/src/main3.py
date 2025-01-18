import tkinter as tk
import random
import time
import os
import requests
from datetime import datetime, timedelta

# -- Custom Modules (adjust to your actual structure) --
from utils.llm import generate_response
from utils.helpers import take_screenshot
from pets.behaviors.interactions import generate_roast_from_image_sequence
from gui.overlay import display_response_above_pet
from gui.utils import load_gif

# -- PIL for GIF manipulation, flipping, etc. --
from PIL import Image, ImageTk, ImageSequence, ImageOps

# ------------------- Global Variables -------------------
window = None
canvas = None
image_id = None

# For controlling the animation frames
gif_frames = []
current_frame_index = 0

# Pet settings
pet_width, pet_height = 120, 100
x_direction, y_direction = 1, 1
moving = True
image_flipped = False

# Reminders & To-Do
reminders = []
todolist = []

# Weather
OPENWEATHER_API_KEY = "48d632279f4f699d5203743231ea388e"

# For text/dialog boxes
response_box = None
response_bok = None
label = None
labal = None

# For screenshot/roasting
screenshots = []
max_screenshots = 5

# Predefined “poses” if you want multiple animations (optional).
# For simplicity, we’ll just use “Walking.gif” from the first code,
# but you can add more if desired.
poses = {
    "walk": "assets/pets/duck/animations/Walking.gif",  # adjust path
    # "idle": "assets/pets/duck/animations/Idle.gif",
    # ... etc.
}

# ------------------- Setup & Initialization -------------------

def create_window():
    """Initializes the Tkinter window (always on top, transparent)."""
    global window
    window = tk.Tk()
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.attributes("-transparentcolor", "black")  # Make the black color transparent
    window.title("Desktop Pet")

    # Set initial size and position to bottom-right or wherever you like
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    start_x = screen_width - pet_width - 50
    start_y = screen_height - pet_height - 50
    window.geometry(f"{pet_width}x{pet_height}+{start_x}+{start_y}")

def create_canvas():
    """Creates the canvas on which the pet is drawn."""
    global canvas
    canvas = tk.Canvas(window, width=pet_width, height=pet_height,
                       bg="black", highlightthickness=0)
    canvas.pack()

def load_and_prepare_gif(gif_path): 
    """
    Loads frames of a GIF using PIL (similar to the first code),
    resizing them to (70,70) for display.
    """
    global gif_frames

    try:
        original_gif = Image.open(gif_path)
        # Resize each frame to your desired size (70x70 here for the ‘pet’)
        frames = [frame.copy().resize((70, 70)) for frame in ImageSequence.Iterator(original_gif)]
        gif_frames = frames
    except Exception as e:
        print(f"Error loading GIF: {e}")
        gif_frames = []

def animate_gif():
    """
    Handles cycling through the GIF frames and flipping if needed.
    Binds the current frame to the canvas, then schedules the next update.
    """
    global current_frame_index, image_flipped

    if not gif_frames:
        return  # No frames loaded, do nothing

    frame = gif_frames[current_frame_index]
    if image_flipped:
        frame = ImageOps.mirror(frame)

    # Convert to PhotoImage for Tkinter
    frame_for_canvas = ImageTk.PhotoImage(frame)
    canvas.delete("all")  # Clear previous frame
    canvas.create_image(
        (pet_width - 70)//2,  # Center X offset
        (pet_height - 70)//2, # Center Y offset
        image=frame_for_canvas,
        anchor="nw"
    )
    # Keep a reference so Python doesn't GC the image
    canvas.image = frame_for_canvas

    # Next frame
    current_frame_index = (current_frame_index + 1) % len(gif_frames)
    # Schedule the next update in 100ms
    canvas.after(100, animate_gif)

# ------------------- Movement (from the first code) -------------------

def randomize_movement_delay():
    """
    Occasionally randomize direction and speed.
    Return the delay (ms) before the next move_pet call.
    """
    global x_direction, y_direction
    # Probability-based random flipping of directions
    if random.random() < 0.025:  # about 2.5% chance
        x_direction, y_direction = random.choices([0, -1, 1], k=2)

    # Return either a random delay or a short delay
    # so the movement doesn't look too uniform
    return random.randint(300, 500) if random.random() < 0.025 else 50

def move_pet():
    """
    Moves the pet around the screen, bouncing off edges,
    flipping the sprite when changing horizontal direction.
    Also checks reminders each time.
    """
    global moving, x_direction, y_direction, image_flipped

    if moving:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        current_x = window.winfo_x()
        current_y = window.winfo_y()

        new_x = current_x + x_direction
        new_y = current_y + y_direction

        # Flip horizontally if changing direction from R to L or vice versa
        if x_direction < 0 and not image_flipped:
            image_flipped = True
        elif x_direction > 0 and image_flipped:
            image_flipped = False

        # Bounce off edges
        if new_x < 0 or new_x > screen_width - pet_width:
            x_direction = -x_direction
        if new_y < 0 or new_y > screen_height - pet_height:
            y_direction = -y_direction

        # Update position
        window.geometry(f"{pet_width}x{pet_height}+{new_x}+{new_y}")

        # Keep response boxes (if open) near the pet
        try:
            if response_box:
                response_box.geometry(
                    f"350x150+{window.winfo_x() + pet_width // 2 - 175}+{window.winfo_y() + pet_height + 10}"
                )
        except:
            pass
        try:
            if response_bok:
                response_bok.geometry(
                    f"{labal.winfo_reqwidth() + 20}x{labal.winfo_reqheight() + 90}+"
                    f"{new_x + pet_width // 2 - response_bok.winfo_reqwidth() // 2}+{new_y + 110}"
                )
        except:
            pass

    # Check reminders
    check_reminders()

    # Schedule next movement
    delay = randomize_movement_delay()
    window.after(delay, move_pet)

# -------------- Dragging the Pet (from the first code) --------------

drag_start_x = 0
drag_start_y = 0

def start_drag(event):
    """Remember initial click coords, pause movement."""
    global drag_start_x, drag_start_y, moving
    drag_start_x, drag_start_y = event.x, event.y
    moving = False

def drag(event):
    """On right-click drag, move the pet window."""
    new_x = window.winfo_x() + (event.x - drag_start_x)
    new_y = window.winfo_y() + (event.y - drag_start_y)
    window.geometry(f"{pet_width}x{pet_height}+{new_x}+{new_y}")

    # Move any open response box along with the pet
    try:
        if response_box:
            response_box.geometry(
                f"350x150+{window.winfo_x() + pet_width // 2 - 175}+{window.winfo_y() + pet_height + 10}"
            )
    except:
        pass
    try:
        if response_bok:
            response_bok.geometry(
                f"{labal.winfo_reqwidth() + 20}x{labal.winfo_reqheight() + 90}+"
                f"{new_x + pet_width // 2 - response_bok.winfo_reqwidth() // 2}+{new_y + 110}"
            )
    except:
        pass

def stop_drag(event):
    """Resume movement after drag is released."""
    global moving
    moving = True

# -------------- Pet Dragging Cursor --------------

import pyautogui
import threading

is_carrying_cursor = False

def on_space_key(event):
    threading.Thread(target = run_to_cursor).start()

def run_to_cursor():
    global moving, is_carrying_cursor

    moving = False 

    cursor_x, cursor_y = pyautogui.position()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
 
    current_x = window.winfo_x()
    current_y = window.winfo_y()
 
    step_count = 1000
    for step in range(1, step_count + 1):
        # Dynamically update the cursor position
        cursor_x, cursor_y = pyautogui.position()

        new_x = current_x + (cursor_x - current_x - pet_width // 2) * step / step_count
        new_y = current_y + (cursor_y - current_y - pet_height // 2) * step / step_count

        new_x = int(max(0, min(new_x, screen_width - pet_width)))
        new_y = int(max(0, min(new_y, screen_height - pet_height)))

        window.geometry(f"{pet_width}x{pet_height}+{new_x}+{new_y}")
        time.sleep(0.001)

    is_carrying_cursor = True

    start_time = time.time()
    direction_x = random.choice([-1, 1]) * random.randint(2, 5)  
    direction_y = random.choice([-1, 1]) * random.randint(2, 5) 

    while time.time() - start_time < 3:
        new_x = window.winfo_x() + direction_x
        new_y = window.winfo_y() + direction_y

        if new_x < 0 or new_x > screen_width - pet_width:
            direction_x = -direction_x
        if new_y < 0 or new_y > screen_height - pet_height:
            direction_y = -direction_y

        window.geometry(f"{pet_width}x{pet_height}+{new_x}+{new_y}")

        pyautogui.moveTo(new_x + pet_width // 2, new_y + pet_height // 2)
        time.sleep(0.001) 
 
    is_carrying_cursor = False
    moving = True


# --------------- Reminders / To-Do from first code ----------------

def check_reminders():
    """Check if it's time to show any reminders."""
    now = datetime.now()
    global reminders
    for reminder in reminders[:]:
        if reminder["time"] <= now:
            response = reminder["message"]
            response_pages = paginate_text(response, 30)
            show_response_box(response_pages, 0)
            reminders.remove(reminder)

# --------------- Screenshot / Roast (second code logic) ---------------
def start_screenshot_task():
    """
    Takes a screenshot every 5 seconds (adjust as you like),
    storing up to `max_screenshots`. Then used for roast.
    """
    global screenshots
    try:
        screenshot_path = take_screenshot()
        screenshots.append(screenshot_path)

        # Remove oldest if we exceed max
        if len(screenshots) > max_screenshots:
            old_screenshot = screenshots.pop(0)
            if os.path.exists(old_screenshot):
                os.remove(old_screenshot)

        print(f"Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"Error taking screenshot: {e}")

    window.after(5000, start_screenshot_task)

def roast_user():
    """
    Generates a roast from the image sequence (screenshots).
    Displays it above the pet using the second code's overlay logic.
    """
    roast = generate_roast_from_image_sequence("screenshots")  # adjust if you store differently
    display_response_above_pet(window, roast)

# ------------------- Pet Interaction (first code + extra) -------------------

def on_pet_click(event):
    """
    Called when user left-clicks the pet.
    Opens a response box that allows the user to type queries
    (reminders, weather, to-do, etc.), or random roast.
    """
    global moving, response_box
    moving = False  # Pause movement

    # If there's already a box open, close it first
    if response_box and response_box.winfo_exists():
        response_box.destroy()

    response_box = tk.Toplevel(window)
    response_box.title("Ask the Pet")
    response_box.configure(bg="#f0f8ff", padx=10, pady=10)
    response_box.geometry(
        f"350x150+{window.winfo_x() + pet_width // 2 - 175}+{window.winfo_y() + pet_height + 10}"
    )
    response_box.overrideredirect(True)  # No window decorations

    global label
    label = tk.Label(response_box, text="What's up?", font=("Arial", 12), bg="#f0f8ff")
    label.pack(pady=10)

    entry_field = tk.Entry(response_box, font=("Arial", 12))
    entry_field.pack(pady=5, fill="x", padx=20)

    def submit_query():
        query_text = entry_field.get()
        if query_text:
            # Decide if it's conversation, automation, or gibberish
            classification_query = (
                "tag the following dialogue with one of these tags. "
                "respond with only the tag. 'conversation', 'automation task', 'gibberish'. "
                "if it is not a 'conversation', then it is an 'automation task'. "
                "if you do not understand, then it is 'gibberish': "
                f"'{query_text}'"
            )
            classification = generate_response(classification_query)
            print("Classification:", classification)

            if "conversation" in classification.lower() or "gibberish" in classification.lower():
                # Just talk
                response = generate_response(f"'{query_text}'")
                show_paginated_response(response)
            elif "automation task" in classification.lower():
                handle_automation_task(query_text)
            else:
                print("Unknown classification. Doing nothing.")

        close_response_box(response_box)

    # Buttons
    button_frame = tk.Frame(response_box, bg="#f0f8ff")
    button_frame.pack(pady=5)

    submit_btn = tk.Button(button_frame, text="Submit", command=submit_query,
                           bg="#d3d3d3", font=("Arial", 10))
    submit_btn.pack(side="left", padx=10)

    close_btn = tk.Button(button_frame, text="Close",
                          command=lambda: close_response_box(response_box),
                          bg="#d3d3d3", font=("Arial", 10))
    close_btn.pack(side="left", padx=10)

def close_response_box(box):
    """Close the response box and resume pet movement."""
    global moving
    if box and box.winfo_exists():
        box.destroy()
    moving = True

def show_paginated_response(response_text):
    """
    Split the response into pages (30 words each) and
    display them in a new box using show_response_box.
    """
    pages = paginate_text(response_text, 30)
    show_response_box(pages, 0)

def show_response_box(pages, current_page):
    """
    Similar to the first code’s response box logic, shows multiple pages
    with Next/Prev if needed.
    """
    global response_bok, labal
    # Close existing if open
    if response_bok and response_bok.winfo_exists():
        response_bok.destroy()

    response_bok = tk.Toplevel(window)
    response_bok.title("Pet's Response")
    response_bok.overrideredirect(True)
    response_bok.attributes("-topmost", True)
    response_bok.configure(bg="#f0f8ff", padx=10, pady=10)

    labal = tk.Label(
        response_bok,
        text=pages[current_page],
        font=("Arial", 12),
        wraplength=320,
        bg="#f0f8ff",
        justify="left",
        anchor="nw"
    )
    labal.pack(expand=True, fill="both")

    # Initial geometry
    response_bok.geometry(
        f"{labal.winfo_reqwidth() + 20}x{labal.winfo_reqheight() + 90}+"
        f"{window.winfo_x() + pet_width//2 - 175}+"
        f"{window.winfo_y() + pet_height + 10}"
    )

    # Nav buttons
    nav_frame = tk.Frame(response_bok, bg="#f0f8ff")
    nav_frame.pack(fill="x", pady=5)

    if current_page > 0:
        prev_btn = tk.Button(
            nav_frame, text="Previous", font=("Arial", 10), bg="#d3d3d3",
            command=lambda: update_page(response_bok, pages, current_page - 1)
        )
        prev_btn.pack(side="left", padx=5)

    if current_page < len(pages) - 1:
        next_btn = tk.Button(
            nav_frame, text="Next", font=("Arial", 10), bg="#d3d3d3",
            command=lambda: update_page(response_bok, pages, current_page + 1)
        )
        next_btn.pack(side="right", padx=5)

    close_btn = tk.Button(
        response_bok, text="Close", font=("Arial", 10), bg="#d3d3d3",
        command=lambda: response_bok.destroy()
    )
    close_btn.pack(pady=5)

def update_page(box, pages, new_page):
    """Destroy and re-show the response box with the new page index."""
    box.destroy()
    show_response_box(pages, new_page)

# --------------- Helper Functions ---------------

def paginate_text(text, words_per_page=30):
    """
    Splits a string into a list of 'pages', each with up to `words_per_page` words.
    """
    words = text.split()
    return [
        ' '.join(words[i:i+words_per_page]) for i in range(0, len(words), words_per_page)
    ]

def handle_automation_task(user_query):
    """
    Uses Gemini to figure out which 'automation' the user wants (reminder, email, weather, etc.),
    then performs that action.
    """
    global reminders, todolist

    classification_query = (
        "tag the following dialogue with one of these tags. respond with only the tag, "
        "'timed reminder', 'email', 'launch', 'weather', 'todolist add', 'todolist delete', 'todolist view'. "
        "dialogue: "
        f"'{user_query}'"
    )
    classification = generate_response(classification_query)
    print("Automation classification:", classification)

    syntax_query = (
        "tag the following dialogue with one of these tags. 'timed reminder', 'email', 'launch', 'weather', "
        "'todolist add', 'todolist delete', 'todolist view'. fill in and only respond with the respective syntax value "
        "as listed below. \n"
        "'timed reminder' syntax: [amount of time in numbers] : [reminder message/purpose]\n"
        "'launch' syntax: [only the program/app name]\n"
        "'weather' syntax: weather\n"
        "'todolist add' syntax: [task to do] : [due date, converted to YYYY-MM-DD HH:MM, NIL if none]\n"
        "'todolist delete' syntax: [task to delete/remove/cancel off]\n"
        "'todolist view' syntax: todolist view.\n"
        "dialogue: "
        f"'{user_query}'"
    )
    syntax = generate_response(syntax_query)
    print("Automation syntax response:", syntax)

    # Timed Reminder
    if "reminder" in classification.lower():
        parts = syntax.split(":")
        if len(parts) == 2:
            time_part, message = parts[0], parts[1].strip()
            # get minutes from time_part
            minutes = int("".join(filter(str.isdigit, time_part)))
            reminder_time = datetime.now() + timedelta(minutes=minutes)
            reminders.append({"time": reminder_time, "message": message})
            result = f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M')}: {message}"
            show_paginated_response(result)
    # Launch
    elif "launch" in classification.lower():
        app_name = syntax.strip()
        # Example: launching from desktop shortcuts
        username = os.getlogin()
        # Adjust path as needed
        app_path = f"C:\\Users\\{username}\\Desktop\\{app_name}.lnk"
        if os.path.exists(app_path):
            try:
                os.startfile(app_path)
                show_paginated_response(f"Launched {app_name}")
            except Exception as e:
                show_paginated_response(f"Error launching {app_name}: {e}")
        else:
            show_paginated_response(f"Application not found: {app_path}")
    # Weather
    elif "weather" in classification.lower():
        try:
            response = requests.get("https://ipinfo.io")
            location = response.json()
            latitude, longitude = location['loc'].split(',')
            # Use openweathermap
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}"
            w_resp = requests.get(url)
            if w_resp.status_code == 200:
                data = w_resp.json()
                city = location.get("city", "Unknown")
                desc = data["weather"][0]["description"]
                temp_c = data["main"]["temp"] - 273.15  # converting from Kelvin
                result = f"Weather in {city} - {desc}\nTemperature: {temp_c:.1f}°C"
                show_paginated_response(result)
            else:
                show_paginated_response(f"Error retrieving weather (status: {w_resp.status_code})")
        except Exception as e:
            show_paginated_response(f"Failed to get weather: {e}")
    # To-Do List
    elif "todolist" in classification.lower():
        if "add" in classification.lower():
            # [task to do] : [due date in YYYY-MM-DD HH:MM, NIL if none]
            try:
                # If there's more than 1 colon, we handle carefully
                colon_count = syntax.count(":")
                if colon_count > 2:
                    first_colon_index = syntax.find(":")
                    syntax = syntax[first_colon_index + 1:]

                task, due_date_str = syntax.split(":", 1)
                task = task.strip()
                due_date_str = due_date_str.strip()

                if due_date_str.upper() == "NIL":
                    due_date = datetime(9999, 12, 31, 23, 59)
                else:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        due_date = datetime(9999, 12, 31, 23, 59)

                if task:
                    todolist.append((task, due_date))
                    todolist.sort(key=lambda x: x[1])
                    show_paginated_response(f"'{task}' added to your To-Do List.")
            except Exception as e:
                show_paginated_response(f"Error adding to to-do list: {e}")

        elif "delete" in classification.lower():
            # [task to remove]
            # If there's "todolist delete:" in syntax, remove it
            to_delete = syntax.replace("todolist delete:", "").strip()
            if not to_delete:
                to_delete = syntax.strip()

            # Remove from todolist
            found = False
            for item in todolist:
                if item[0] == to_delete:
                    todolist.remove(item)
                    found = True
                    show_paginated_response(f"'{to_delete}' removed from your To-Do List.")
                    break
            if not found:
                show_paginated_response(f"Task '{to_delete}' not found in your To-Do List.")

        elif "view" in classification.lower():
            if not todolist:
                show_paginated_response("Your To-Do List is empty.")
            else:
                text = "To-Do List:\n"
                for i, (task, due_date) in enumerate(todolist, start=1):
                    if due_date.year == 9999:
                        text += f"{i}. {task}\n"
                    else:
                        text += f"{i}. {task} : {due_date.strftime('%Y-%m-%d %H:%M')}\n"
                show_paginated_response(text)
    else:
        # Fallback
        show_paginated_response("I didn't recognize that automation task.")


# ------------------- Main Entry Point -------------------
def main():
    create_window()
    create_canvas()

    # Load your walking animation frames. If you want multiple poses, you can load them as needed.
    load_and_prepare_gif(poses["walk"])

    # Start the GIF animation
    animate_gif()

    # Bind user interaction events
    canvas.bind("<Button-1>", on_pet_click)  # Left-click -> ask pet
    canvas.bind("<Button-3>", start_drag)    # Right-click -> drag
    canvas.bind("<B3-Motion>", drag)
    canvas.bind("<ButtonRelease-3>", stop_drag)

    window.bind("<space>", on_space_key)

    # Begin movement
    move_pet()

    # Start periodic screenshot capturing
    start_screenshot_task()

    # Start the main loop
    window.mainloop()

if __name__ == "__main__":
    main()
