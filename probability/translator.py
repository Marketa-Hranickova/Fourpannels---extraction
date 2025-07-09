import asyncio
from googletrans import Translator
import os

async def translate_text_async(text: str, dest_language: str = 'en') -> str:
    """
    Translates the given text asynchronously to the specified destination language.

    Args:
        text (str): The text to be translated.
        dest_language (str): The language code for the destination language.

    Returns:
        str: The translated text.
    """
    translator = Translator()
    result = await translator.translate(text, dest=dest_language)
    return result.text

async def translate_single_file_to_czech(input_filepath: str, output_filepath: str):
    """
    Reads text from a single input file, translates it to Czech asynchronously,
    and saves the translated text to an output file.

    Args:
        input_filepath (str): The path to the input text file.
        output_filepath (str): The path where the translated Czech text will be saved.
    """
    try:
        if not os.path.exists(input_filepath):
            print(f"Error: Input file not found: {input_filepath}")
            return

        with open(input_filepath, 'r', encoding='utf-8') as f:
            source_text = f.read()

        print(f"Translating '{os.path.basename(input_filepath)}' to Czech...")

        # *** CHANGE IS HERE: dest_language='cs' ***
        translated_text = await translate_text_async(source_text, dest_language='cs')

        output_dir = os.path.dirname(output_filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(translated_text)

        print(f"Finished translating '{os.path.basename(input_filepath)}'. Saved to: {output_filepath}")

    except Exception as e:
        print(f"An error occurred during translation of '{os.path.basename(input_filepath)}': {e}")

# --- Main execution block ---
async def main():
    """
    Main asynchronous function to orchestrate the translation of multiple files
    from an input folder to an output folder.
    """
    input_folder = "texts"
    # *** CHANGE IS HERE: new output folder name ***
    output_folder = "texts_cz"

    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found. Please create it and place your text files inside.")
        return

    os.makedirs(output_folder, exist_ok=True)
    print(f"Processing files from: '{input_folder}'")
    print(f"Saving translated files to: '{output_folder}'")

    translation_tasks = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_filepath = os.path.join(input_folder, filename)
            # *** CHANGE IS HERE: output filename convention for Czech ***
            base_name, ext = os.path.splitext(filename)
            output_filename = f"{base_name}_cs{ext}" # Example: document.txt -> document_cs.txt
            output_filepath = os.path.join(output_folder, output_filename)

            # *** CHANGE IS HERE: call the CZECH translation function ***
            translation_tasks.append(
                translate_single_file_to_czech(input_filepath, output_filepath)
            )
        else:
            print(f"Skipping non-text file: {filename}")

    if not translation_tasks:
        print("No text files found in the input folder to translate.")
        return

    await asyncio.gather(*translation_tasks)
    print("\nAll translations complete!")

if __name__ == "__main__":
    asyncio.run(main())