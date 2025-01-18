from PIL import Image
from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
import os
from dotenv import load_dotenv
from utils.llm import generate_response

load_dotenv()

# Load the processor and model
processor = Pix2StructProcessor.from_pretrained("google/pix2struct-textcaps-base")
model = Pix2StructForConditionalGeneration.from_pretrained("google/pix2struct-textcaps-base")


def generate_roast_from_image_sequence(screenshot_directory_path):
    """Generate a roast from a sequence of screenshots."""
    # Load the screenshots
    screenshots = []
    for filename in os.listdir(screenshot_directory_path):
        if filename.endswith(".png"):
            screenshot_path = os.path.join(screenshot_directory_path, filename)
            screenshot = Image.open(screenshot_path)
            screenshots.append(screenshot)

    # Process the screenshot one by one and concatenate the results as a prompt to a LLM model
    prompt = "You are an pure hater of this person and you are trying to roast him/her. You have taken some screenshots of his/her desktop and you are trying to generate a roast based on that. Here are content of the screenshots:\n"

    for screenshot in screenshots:
        processed_input = processor(screenshot, return_tensors="pt", legacy=False)
        model_output = model.generate(**processed_input)
        prompt += processor.decode(model_output[0], skip_special_tokens=True)

    prompt += "\nRoast:"

    return generate_response(prompt)


if __name__ == "__main__":
    screenshot_directory_path = "screenshots"
    generated_roast = generate_roast_from_image_sequence(screenshot_directory_path)
    print(generated_roast)