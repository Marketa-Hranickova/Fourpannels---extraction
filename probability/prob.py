# /Users/marke/Documents/SpaCyNewProject/spacy_analysis.py

import spacy
from spacy.matcher import Matcher # Make sure this import is at the top of your file or within the function

def analyze_german_text(text):
    """
    Loads a German spaCy model and performs basic NLP analysis on the given text.
    """
    try:
        # Load the German language model
        # Make sure you've run: python -m spacy download de_core_news_sm
        nlp = spacy.load("de_core_news_sm")
        print("German spaCy model loaded successfully.")
    except OSError:
        print("German spaCy model 'de_core_news_sm' not found.")
        print("Please run: python -m spacy download de_core_news_sm")
        return

    # Process the text with the loaded model
    doc = nlp(text)

    print("\n--- Tokenization and Part-of-Speech Tagging ---")
    print("{:<15} {:<10} {:<10} {:<15}".format("Token", "Lemma", "POS", "Dependency"))
    print("-" * 50)
    for token in doc:
        print(f"{token.text:<15} {token.lemma_:<10} {token.pos_:<10} {token.dep_:<15}")

    print("\n--- Named Entity Recognition (NER) ---")
    if doc.ents:
        for ent in doc.ents:
            # spacy.explain might return None if no explanation is available for a given label
            explanation = spacy.explain(ent.label_) if spacy.explain(ent.label_) else "N/A"
            print(f"Entity: '{ent.text}' | Type: {ent.label_} | Explanation: {explanation}")
    else:
        print("No named entities found.")

    print("\n--- Sentence Segmentation ---")
    for i, sent in enumerate(doc.sents):
        print(f"Sentence {i+1}: {sent.text}")

    print("\n--- Custom Keyword Extraction Example (Medical context) ---")
    medical_keywords = [
        "Schmerz", "Fieber", "Husten", "Diagnose", "Therapie",
        "Medikament", "Patient", "Arzt", "Krankenhaus", "Symptom"
    ]
    
    found_medical_terms = []
    lower_text = text.lower() 
    for keyword in medical_keywords:
        if keyword.lower() in lower_text:
            found_medical_terms.append(keyword)
    
    if found_medical_terms:
        print(f"Detected Medical Terms: {', '.join(set(found_medical_terms))}")
    else:
        print("No specific medical keywords detected in this text sample.")

    print("\n--- Custom Rule-Based Extraction Example (using Matcher) ---")
    # from spacy.matcher import Matcher # Already imported at the top for efficiency.
    matcher = Matcher(nlp.vocab)

    # Example: Find phrases like "starke Schmerzen" (strong pain)
    # CORRECTED PATTERN: Use "POS": "ADJ" instead of "ADJ": {} directly
    pattern = [{"POS": "ADJ", "LEMMA": {"IN": ["stark", "heftig", "chronisch"]}}, {"LEMMA": "Schmerz"}]
    matcher.add("PAIN_INTENSITY", [pattern])

    matches = matcher(doc)
    if matches:
        print("Detected pain intensity phrases:")
        for match_id, start, end in matches:
            span = doc[start:end] # The matched span of text
            print(f"- '{span.text}' (Rule: {nlp.vocab.strings[match_id]})")
    else:
        print("No specific pain intensity phrases detected.")


# --- Sample German Medical Report-like Text ---
text_file_path = "textsample.txt"
try:
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text_from_file = f.read()
    print(f"\nSuccessfully read text from: {text_file_path}")
except FileNotFoundError:
    print(f"Error: The file '{text_file_path}' was not found.")
    text_from_file = "" # Set to empty to avoid error in analyze_german_text
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    text_from_file = ""
if text_from_file:
    print("\n--- Analyzing Text from textsample.txt ---")
    analyze_german_text(text_from_file)

sample_text_2 = """
Bericht vom 15. Juni 2025: Die Patientin wurde wegen anhaltendem Husten und leichtem Fieber vorgestellt.
Es gab keine Hinweise auf eine Lungenentzündung. Die Medikamentenverordnung erfolgte.
Sie fühlt sich heute etwas besser, aber noch nicht ganz fit.
"""

# --- Run the analysis ---
print("--- Analyzing Sample Text 1 ---")
analyze_german_text(text_from_file)

print("\n\n" + "="*70 + "\n\n")

print("--- Analyzing Sample Text 2 ---")
analyze_german_text(sample_text_2)