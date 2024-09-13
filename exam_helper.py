import base64
import os
import requests
import pyperclip
import keyboard
from PIL import ImageGrab
import fitz

# Constants for configuration
API_KEY = "REDACTED" 
MODEL_NAME = "gpt-4o"
TRIGGER_KEY = 'caps lock'               # Trigger key to capture screenshot
TEXT_CONTEXT_FOLDER = "context_folder"  # Folder path for optional text context
SCREENSHOT_FILENAME = "screenshot.png"  # Filename for the temporary screenshot

def encode_image(image_path):
    """
    Encode an image file to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: Base64-encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def capture_screenshot():
    """
    Capture a screenshot of the current screen and save it to a file.

    Returns:
        str: The path to the saved screenshot file.
    """
    screenshot = ImageGrab.grab()
    screenshot.save(SCREENSHOT_FILENAME)
    return SCREENSHOT_FILENAME

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using fitz (PyMuPDF).

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")
    return text

def load_text_context(folder_path):
    """
    Load text context from PDF and TXT files within a specified folder.

    Args:
        folder_path (str): The path to the folder containing text context files.

    Returns:
        str: Concatenated text content from all valid files.
    """
    text_context = ""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return text_context

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.lower().endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text_context += file.read() + "\n"
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='ISO-8859-1') as file:
                    text_context += file.read() + "\n"
        elif filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            text_context += text + "\n"
    return text_context

def send_image_to_openai(base64_image, text_context, api_key):
    """
    Send the base64-encoded image and optional text context to the OpenAI API.

    Args:
        base64_image (str): Base64-encoded string of the image.
        text_context (str): Optional text context for the model.
        api_key (str): OpenAI API key.

    Returns:
        dict: JSON response from the OpenAI API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    user_message_content = [
        {
            "type": "text",
            "text": "Given the image, directly provide answers to the question posed. Base your responses on the provided context, ensuring accuracy and relevance. Provide answers only."
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": user_message_content
        }
    ]

    if text_context:
        messages.insert(0, {
            "role": "system",
            "content": text_context
        })

    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def clear_terminal():
    """
    Clear the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """
    Main function to monitor for the trigger key, capture screenshots, send them to the OpenAI API,
    and display the responses.
    """
    api_key = API_KEY
    
    clear_terminal()
    
    print(f"Press '{TRIGGER_KEY.upper()}' to capture a screenshot and analyze it. Press 'ESC' to exit.")

    while True:
        keyboard.wait(TRIGGER_KEY)  # Wait for the trigger key to be pressed

        clear_terminal()

        # Capture the screenshot
        screenshot_path = capture_screenshot()

        # Encode the screenshot to base64
        base64_image = encode_image(screenshot_path)

        # Load optional text context from the specified folder
        text_context = load_text_context(TEXT_CONTEXT_FOLDER)

        # Send the image and context to the OpenAI API
        response = send_image_to_openai(base64_image, text_context, api_key)

        # Delete the screenshot file
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        # Process and display the response
        try:
            # Extract the assistant's reply from the response
            answer = response['choices'][0]['message']['content']

            # Display the answer
            print(answer)

            # Copy the answer to the clipboard
            pyperclip.copy(answer)
        except (KeyError, IndexError) as e:
            print("Failed to process the response.")
            print(f"Error: {e}")
            pyperclip.copy("Error in processing the response.")

        # Exit the loop if 'ESC' key is pressed
        if keyboard.is_pressed('esc'):
            break

if __name__ == "__main__":
    main()
