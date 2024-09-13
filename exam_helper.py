import base64
import os
import requests
import pyperclip
import keyboard
from PIL import ImageGrab
import fitz

# Constants for configuration
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
        # Directory does not exist, return empty text_context
        return text_context

    # Proceed to load text from files if directory exists
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

    # Prepare the message content
    user_message_content = [
        {
            "type": "text",
            "text": "Given the image input, directly provide clear and concise answers to the question posed. As much as possible, base your responses on the provided context, if any. Provide answers directly."
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
    and display the responses. The function will continue to run until the user manually terminates the process.
    """
    clear_terminal()
    
    # Instructions to the user
    print("DISCLAIMER:\n")
    print("The creator, author, or distributor of this script assumes NO responsibility for any direct or indirect consequences, damages, or liabilities arising from the use or misuse of this program.\n")
    print("This includes, but is not limited to, legal, academic, financial, or personal repercussions.\n")
    print("Use of this script is entirely at your own risk. By continuing, you acknowledge that you understand and accept these terms.\n")
    print("----------------------------\n")
    input("If you understand and agree to the above terms, press 'ENTER' to continue...")
    clear_terminal()
    print("IMPORTANT: After completing your tasks, it is NECESSARY to RESTART your computer to ensure no unintended API calls or processes continue running in the background.\n")
    print("----------------------------\n")
    input("If you understand, press 'ENTER' to continue...")
    clear_terminal()
    print("To add knowledge context, create a directory named 'context_folder' and place PDF and/or TXT files in it.\n")
    print(f"Press '{TRIGGER_KEY.upper()}' to capture a screenshot and analyze it.\n")
    print("\n----------------------------\n")
    input("Press 'ENTER' to continue...")
    clear_terminal()

    # Prompt user for API key
    api_key = input("Please enter your OpenAI API key: ")

    clear_terminal()
    
    print(f"Waiting for you to press '{TRIGGER_KEY.upper()}' to capture a screenshot...")

    while True:
        # Wait for the trigger key (Caps Lock) to be pressed
        keyboard.wait(TRIGGER_KEY)  # Wait for the trigger key to be pressed

        clear_terminal()

        try:
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
        
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    main()
