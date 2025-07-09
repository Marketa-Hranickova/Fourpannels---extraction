import ollama
import json
import pandas as pd # Import the pandas library

def ask_llama_about_text_structured(text_file_path):
    """
    Feeds text from a file to Ollama Llama 3 and asks questions,
    expecting a structured JSON response.
    """
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            document_text = f.read()

        # Define the prompt to instruct Llama 3 to return JSON.
        # We explicitly define the expected JSON structure within the prompt.
        prompt = f"""
        Analyze the following medical document and extract the requested information.
        Respond *only* with a JSON object. If information is not explicitly present in the document, state "-".
        Keep answers as concise as possible.

        Expected JSON format:
        {{
          "endometriosis": "Yes/No",
          "patient_weight": "weight_value_and_unit_or_-",
          "patient_height": "height_value_and_unit_or_-",
          "hypermenorrhea_reported": "Yes/No",
          "metrorrhagia_reported": "Yes/No_and_elaboration_if_yes_or_-"
        }}

        Document:
        ---
        {document_text}
        ---
        """

        print(f"Sending request to Llama 3 for structured extraction from '{text_file_path}'...")

        # Call Ollama with the 'json' format parameter.
        # This tells Ollama to expect and return a JSON string.
        response = ollama.chat(
            model='llama3',
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            options={
                'temperature': 0.0 # Keep temperature low for factual extraction to reduce hallucination
            },
            stream=False, # Ensure we get the full JSON response at once
            format='json' # This is crucial for Ollama to return JSON
        )

        # Parse the JSON response from the model's content
        try:
            # The 'format="json"' parameter in ollama.chat makes response['message']['content']
            # a string that needs to be parsed.
            extracted_data = json.loads(response['message']['content'])

            print("\n--- Extracted Information (Pandas Table) ---")

            # Prepare data for pandas DataFrame
            questions = [
                "Does the patient have endometriosis?",
                "What is the patient's weight?",
                "What is the patient's height?",
                "Is Hypermenorrhea reported?",
                "Is Metrorrhagia reported?"
            ]
            answers = [
                extracted_data.get('endometriosis', '-'),
                extracted_data.get('patient_weight', '-'),
                extracted_data.get('patient_height', '-'),
                extracted_data.get('hypermenorrhea_reported', '-'),
                extracted_data.get('metrorrhagia_reported', '-')
            ]

            # Create a pandas DataFrame
            df = pd.DataFrame({
                'Question': questions,
                'Answer': answers
            })

            # Print the DataFrame
            print(df.to_string(index=False)) # .to_string(index=False) for a clean table without pandas index

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response from Llama 3: {e}")
            print("Raw response content (likely not valid JSON):")
            print(response['message']['content'])
        except KeyError as e:
            print(f"Error: Expected key '{e}' not found in the JSON response.")
            print("Raw response content:")
            print(response['message']['content'])

    except FileNotFoundError:
        print(f"Error: The file '{text_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration ---
    your_text_file = "sampletext.txt" # Make sure this file exists with your PDF content
    # You no longer need to define the questions here as they are in the JSON prompt

    # --- Run the function ---
    ask_llama_about_text_structured(your_text_file)
