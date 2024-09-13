# Exam Helper 
Exam Helper is a Python script designed to assist users by capturing screenshots and optionally including text context from specified documents to analyze content using the OpenAI API. This tool is particularly useful for academic purposes where quick reference and analysis of visual and textual data are required.

## Disclaimer
The creator, author, or distributor of this script assumes NO responsibility for any direct or indirect consequences, damages, or liabilities arising from the use or misuse of this program. This includes, but is not limited to, legal, academic, financial, or personal repercussions. Use of this script is entirely at your own risk. By continuing, you acknowledge that you understand and accept these terms.

## Features
- **Screenshot Capture**: Triggered by the Caps Lock key, the script captures a screenshot of your current screen.
- **Text Context Inclusion**: Allows for the inclusion of additional text context from PDF and TXT files located in a specified directory.
- **OpenAI API Integration**: Sends the captured data to the OpenAI API for processing and retrieves the analysis.
- **Clipboard Support**: Automatically copies the API's response to the clipboard for easy use.

## Usage
To use Exam Helper:
1. Ensure you have a valid OpenAI API key.
2. Run the script:
   ```
   python exam_helper.py
   ```
3. Follow the on-screen instructions to input your OpenAI API key and proceed with the operation as guided by the prompts.

### Adding Text Context
Create a directory named `context_folder` and place your PDF and/or TXT files in it. The script will automatically parse these files for additional context when processing your requests.

### Exiting the Program
Currently, you must restart your computer after using this script to ensure that no unintended processes continue to run. Future updates may include a more refined exit strategy.

## Contributing
Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
mikaelvincent.dev - tumampos@mikaelvincent.dev

## Project Link: 
https://github.com/mikaelvincent/Exam_Helper
