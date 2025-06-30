import asyncio
from googletrans import Translator 
import os # Import the os module to handle file paths

async def translate_text_async(text: str, dest_language: str = 'cz') -> str:
    """
    Translates the given text asynchronously to the specified destination language.

    Args:
        text (str): The text to be translated.
        dest_language (str): The language code for the destination language (default is 'en' for English).

    Returns:
        str: The translated text.
    """
    translator = Translator()
    # Await the translation result. This pauses execution until the translation is complete.
    result = await translator.translate(text, dest=dest_language)
    return result.text

async def translate_file_to_english(input_filepath: str, output_filepath: str):
    """
    Reads German text from an input file, translates it to English asynchronously,
    and saves the translated text to an output file.

    Args:
        input_filepath (str): The path to the input file containing German text.
        output_filepath (str): The path where the translated English text will be saved.
    """
    try:
        # Ensure the input file exists
        if not os.path.exists(input_filepath):
            print(f"Error: Input file not found at {input_filepath}")
            return

        with open(input_filepath, 'r', encoding='utf-8') as f:
            german_text = f.read()

        print(f"Successfully read German text from: {input_filepath}")
        print("Translating text to English...")

        # Call the async translation function and await its result
        translated_text = await translate_text_async(german_text, dest_language='cz')

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(translated_text)

        print(f"Translation complete. English text saved to: {output_filepath}")

    except Exception as e:
        print(f"An error occurred during translation: {e}")

# --- Main execution block ---
if __name__ == "__main__":
    # Define your input and output file paths
    # Make sure 'textsample.txt' exists in the same directory as this script,
    # or provide its full path.
    german_input_file = "textsample.txt"
    english_output_file = "translated_en.txt"

    # Ensure paths are absolute for robust execution, especially if you move files
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # german_input_file = os.path.join(current_dir, "textsample.txt")
    # english_output_file = os.path.join(current_dir, "translated_output.txt")


    # Run the main asynchronous function using asyncio.run()
    # This sets up and manages the event loop for your async operations.
    asyncio.run(translate_file_to_english(german_input_file, english_output_file))