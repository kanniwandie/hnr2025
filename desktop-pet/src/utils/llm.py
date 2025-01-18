from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GENAI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_response(prompt):
    """Generate a response from the LLM model."""
    try:
        # Generate response from LLM
        response = model.generate_content(prompt)
        response_text = response.text

        return response_text
    except Exception as e:
        print(f"Error during LLM processing: {e}")
        return {"error": str(e)}