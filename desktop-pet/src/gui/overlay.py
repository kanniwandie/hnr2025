import tkinter as tk


def display_response_above_pet(window, pet, message):
    """Display a response as a text box above the pet for 5 seconds and make it follow the pet."""
    # Create the response box
    response_box = tk.Toplevel(window)
    response_box.title("Response")
    response_box.overrideredirect(True)  # Remove the title bar for a clean look
    response_box.attributes("-topmost", True)  # Keep it on top

    # Set the initial position of the response box above the pet
    pet_x = pet.window.winfo_x()
    pet_y = pet.window.winfo_y()
    response_width, response_height = 200, 50
    response_box.geometry(
        f"{response_width}x{response_height}+{pet_x + pet.width//2 - response_width//2}+{pet_y - response_height - 10}"
    )

    # Add the response message
    tk.Label(response_box, text=message, font=("Arial", 12), bg="yellow", wraplength=response_width).pack(expand=True, fill="both")

    # Function to update the position of the response box
    def update_position():
        if response_box.winfo_exists():  # Ensure the response box still exists
            pet_x = pet.window.winfo_x()
            pet_y = pet.window.winfo_y()
            response_box.geometry(
                f"{response_width}x{response_height}+{pet_x + pet.width//2 - response_width//2}+{pet_y - response_height - 10}"
            )
            # Keep updating the position as long as the response box is visible
            window.after(50, update_position)

    # Start updating the position
    update_position()

    # Close the response box after 5 seconds
    response_box.after(5000, response_box.destroy)
