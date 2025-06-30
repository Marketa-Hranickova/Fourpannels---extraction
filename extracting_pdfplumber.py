import pdfplumber
import pandas as pd
import os  # Add this for path checks
import cv2
import numpy as np
from PIL import Image

# Define file_path at the top for debugging
file_path = "coordinates.txt"
pdf_path = "sample.pdf"  # Replace with your PDF path
tables_data = []
output_file = "extracted_data.txt"

#print("File size:", os.path.getsize(file_path), "bytes")
#print("Readable?", os.access(file_path, os.R_OK))
#KEEP
def parse_table_data_from_space_separated_floats(file_path):
    all_tables_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            #print("\nFile contents (first few lines):")
            for i, line in enumerate(f):
                if i < 5:  # Print first 5 lines to check format
                    print(f"Line {i+1}: {line.strip()}")
                else:
                    break
            f.seek(0)  # Reset file pointer to read again

            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                parts = [p.replace(',', '.') for p in clean_line.split()]
                #print(f"Split parts (Line {line_num}): {parts}")  # Debug split
                
                if len(parts) != 5:
                    print(f"Warning: Line {line_num} has {len(parts)} parts (expected 5). Skipping.")
                    continue

                try:
                    table_entry = {
                        'table_id': int(parts[0]),
                        'x': float(parts[1]),
                        'y': float(parts[2]),
                        'width': float(parts[3]),
                        'height': float(parts[4])
                    }
                    all_tables_data.append(table_entry)
                except ValueError as e:
                    print(f"Error in Line {line_num}: {e}")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    #print("\nParsed data:", all_tables_data[1])
    return all_tables_data


#KEEP
def extracting_pdf(pdf_path, parsed_data):
    tables_data = []
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]  # Focus on the first page only
        
        for entry in parsed_data:
            x, y, w, h = entry["x"], entry["y"], entry["width"], entry["height"]
            
            # Convert y-coordinate (PDFs start from bottom-left)
            #y_pdf = first_page.height - y - h
            
            # Define bounding box (x0, top, x1, bottom)
            bbox = (x, y, x + w, y + h)
            print(bbox)
            # Crop and extract text
            cropped_page = first_page.crop(bbox)
            table_text = cropped_page.extract_text()
            
            tables_data.append({
                "table_id": entry["table_id"],
                "text": table_text.strip() if table_text else "No text extracted"
            })


    
    return tables_data

def parse_table_data_from_space_separated_floats(file_path):
    """
    Parses a space-separated file containing table ID and bounding box coordinates.
    Each line should have: table_id x y width height.
    """
    all_tables_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print("\nFile contents (first few lines from coordinates.txt):")
            for i, line in enumerate(f):
                if i < 5:  # Print first 5 lines to check format
                    print(f"Line {i+1}: {line.strip()}")
                else:
                    break
            f.seek(0)  # Reset file pointer to read again

            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                parts = [p.replace(',', '.') for p in clean_line.split()]
                
                if len(parts) != 5:
                    print(f"Warning: Line {line_num} in {file_path} has {len(parts)} parts (expected 5). Skipping.")
                    continue

                try:
                    table_entry = {
                        'table_id': int(parts[0]),
                        'x': float(parts[1]),
                        'y': float(parts[2]),
                        'width': float(parts[3]),
                        'height': float(parts[4])
                    }
                    print(table_entry["table_id"])
                    all_tables_data.append(table_entry)
                except ValueError as e:
                    print(f"Error parsing Line {line_num} in {file_path}: {e}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it exists.")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
    
    return all_tables_data

def extracting_pdf(pdf_path, parsed_data):
    """
    Extracts text from specified bounding boxes in the PDF.
    Focuses on the first page of the PDF for extraction.
    """
    tables_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                print(f"Error: PDF '{pdf_path}' has no pages.")
                return []
            
            first_page = pdf.pages[0]  # Focus on the first page only
            print(f"\nExtracting text from specified bounding boxes on page 1 of '{pdf_path}'...")
            
            for entry in parsed_data:
                x, y, w, h = entry["x"], entry["y"], entry["width"], entry["height"]
                
                # Define bounding box (x0, top, x1, bottom) - pdfplumber uses standard PDF coords
                bbox = (x, y, x + w, y + h)
                print(f"Processing bbox: {bbox}") # Debug print
                
                # Crop and extract text
                cropped_page = first_page.crop(bbox)
                table_text = cropped_page.extract_text()
                
                tables_data.append({
                    "table_id": entry["table_id"],
                    "text": table_text.strip() if table_text else "No text extracted"
                })
    except FileNotFoundError:
        print(f"Error: The PDF file '{pdf_path}' was not found. Please ensure it exists.")
    except Exception as e:
        print(f"Error opening or processing PDF '{pdf_path}': {e}")
    
    return tables_data


def is_char_present_in_cropped_page(cropped_pdf_page_obj, target_char='☒'):
    """
    Checks if a specific Unicode character is present in the cropped pdfplumber page object.
    It iterates through individual characters to find a precise match.
    """
    # Using .chars gives more granular control and accurate positioning than .extract_text()
    # for finding specific symbols.
    for char_obj in cropped_pdf_page_obj.chars:
        if char_obj['text'] == target_char:
            return True
    
    # Fallback/alternative: check if the character is in the extracted text
    # This might be less precise regarding exact location within the box,
    # but can catch symbols if 'chars' extraction is tricky.
    # extracted_text = cropped_pdf_page_obj.extract_text()
    # if extracted_text and target_char in extracted_text:
    #     return True

    return False


def crossing1(pdf_path, parsed_data, output_file="extracted_data.txt"):
    """
    Detects if 'Yes' or 'No' checkboxes (for table_id 1 entries) are marked with the '☒' symbol.
    This function has been adapted to use character-based detection.
    """
    results = []  # Store results for all entries
    target_char = '☒' # The crossed square symbol (U+2612)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                print(f"Error: PDF '{pdf_path}' has no pages.")
                return

            first_page = pdf.pages[0]
            print(f"\nDetecting checked boxes (using Unicode '{target_char}') with 'crossing1' function on page 1 of '{pdf_path}'...")

            for entry in parsed_data:
                if entry["table_id"] == 1:  # Only process table_id 1
                    print(f"Found table_id=1 at index 1: {entry}")
                    yes_marked = False
                    no_marked = False

                    # Iterate through potential vertical positions within the entry's height
                    # You might need to adjust the range(start, end, step) based on your PDF layout
                    # '14' is typical line height/step for your example, '17' starting offset, '-5' end buffer.
                    for y_offset in range(17, int(entry['height'])-5, 14): # Using 17 and -5 for consistency
                        # Yes box coordinates (right-aligned, assuming a 15-unit width for the checkbox)
                        yes_box = (
                            entry["x"] + entry["width"] - 15,  
                            entry["y"] + y_offset,
                            entry["x"] + entry["width"],
                            entry["y"] + y_offset + 14
                        )
                        
                        # No box coordinates (further left, assuming another 15-unit box)
                        no_box = (
                            entry["x"] + entry["width"] - 30,  
                            entry["y"] + y_offset,
                            entry["x"] + entry["width"] - 15,
                            entry["y"] + y_offset + 14
                        )
                        

                       # ... (existing code for yes_box and no_box) ...

                        # --- TEMPORARY DEBUGGING VISUALIZATION ---
                        # This part requires Pillow (PIL) installed: pip install Pillow
                        # And you might need to adjust resolution for clarity.
                        try:
                            # To see the Yes box
                            img = first_page.to_image(resolution=150) # Adjust resolution as needed
                            img.draw_rect(yes_box, stroke=(255, 0, 0), fill=(255, 0, 0, 50)) # Red rectangle
                            img.save(f"debug_yes_box_page{first_page.page_number}_y{y_offset}.png")
                            #print(f"Saved debug image for Yes box: debug_yes_box_page{first_page.page_number}_y{y_offset}.png")

                            # To see the No box
                            img = first_page.to_image(resolution=150) # Re-generate image to avoid drawing over it
                            img.draw_rect(no_box, stroke=(0, 0, 255), fill=(0, 0, 255, 50)) # Blue rectangle
                            img.save(f"debug_no_box_page{first_page.page_number}_y{y_offset}.png")
                            #print(f"Saved debug image for No box: debug_no_box_page{first_page.page_number}_y{y_offset}.png")
                        except ImportError:
                            print("Install Pillow (pip install Pillow) to use visualization.")
                        except Exception as vis_e:
                            print(f"Error during visualization: {vis_e}")
                        # --- END TEMPORARY DEBUGGING VISUALIZATION ---

                        # Crop the page to the Yes box and check for the symbol
                        yes_cropped_page = first_page.crop(yes_box)
                        if is_char_present_in_cropped_page(yes_cropped_page, target_char):
                            yes_marked = True
                            # break # Remove this break for now, so you can see all attempts
                        
                        # Crop the page to the No box and check for the symbol
                        no_cropped_page = first_page.crop(no_box)
                        if is_char_present_in_cropped_page(no_cropped_page, target_char):
                            no_marked = True
                            # break # Remove this break for now

                    # Determine the result for this entry
                        if yes_marked:
                            results.append("Yes")
                        elif no_marked:
                            results.append("No")
                        else:
                            results.append("Nothing")
                            print(y_offset)
        
        # Write all checkbox results to the output file
        with open(output_file, "a") as f:  # Append mode
            f.write("\n--- Checkbox Results (from crossing1, using Unicode '☒') ---\n")
            f.write("\n".join(results) + "\n")
        print(f"✅ Checkbox results appended to: {output_file}")

    except FileNotFoundError:
        print(f"Error: The PDF file '{pdf_path}' was not found. Please ensure it exists.")
    except Exception as e:
        print(f"An error occurred during checkbox detection in 'crossing1': {e}")


'''
def detect_visual_cross(pdf_path, parsed_data, output_file="output.txt"):
    cross_symbols = ["✓", "✗", "☒", "×"]  # Common cross/check symbols
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        
        for entry in parsed_data:
            if entry["table_id"] == 1:  # Only process table_id 1
                for y in range(17, int(entry['height'])-5, 14):
                    yes_box = (
                        entry["x"] + entry["width"] - 15,  # Right-aligned "Yes" box
                        entry["y"] + y,
                        entry["x"] + entry["width"],
                         y+entry["y"] + 14
                    )
                    print(yes_box)
                    no_box = (
                        entry["x"] + entry["width"] - 30,  # Right-aligned "Yes" box
                        entry["y"] + y,
                        entry["x"] + entry["width"] -15,
                         y+entry["y"] + 14
                    )

                    # Check Yes box
                    yes_cropped = first_page.crop(yes_box)
                    yes_text = yes_cropped.extract_text() or ""
                    yes_marked = any(sym in yes_text for sym in cross_symbols)
                    
                    # Check No box
                    no_cropped = first_page.crop(no_box)
                    no_text = no_cropped.extract_text() or ""
                    no_marked = any(sym in no_text for sym in cross_symbols)
                    
                    results.append("Yes" if yes_marked else "No" if no_marked else "Nothing")
    
    # Write all results at once
    with open(output_file, "a") as f:  # Append mode
        f.write("\nCheckbox Results:\n")
        f.write("\n".join(results) + "\n")
'''

'''
def detect_checked_boxes(pdf_path, parsed_data, template_path, output_file="extracted_data.txt"):
    # Load reference cross template
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    assert template is not None, "Template image not found"
    w, h = template.shape[::-1]  # Get template dimensions
    
    with pdfplumber.open(pdf_path) as pdf, open(output_file, "w") as f:
        page = pdf.pages[0]
        page_img = page.to_image(resolution=200).original  # High-res image
        gray_page = cv2.cvtColor(np.array(page_img), cv2.COLOR_RGB2GRAY)
        
        for entry in parsed_data:
            if entry["table_id"] == 1:
                for y_offset in range(17, int(entry['height'])-5, 14):
                    # Yes box coordinates
                    yes_box = (
                        entry["x"] + entry["width"] - 15,
                        entry["y"] + y_offset,
                        entry["x"] + entry["width"],
                        entry["y"] + y_offset + 14
                    )
                    
                    # No box coordinates
                    no_box = (
                        entry["x"] + entry["width"] - 30,
                        entry["y"] + y_offset,
                        entry["x"] + entry["width"] - 15,
                        entry["y"] + y_offset + 14
                    )

                    # Check both boxes
                    yes_marked = is_box_checked(gray_page, yes_box, template, w, h)
                    no_marked = is_box_checked(gray_page, no_box, template, w, h)
                    #print("I WAS HERE")
                    # Write results
                    result = "Yes" if yes_marked else "No" if no_marked else "Nothing"
                    f.write(f"Line y={y_offset}: {result}\n")
'''
'''
def is_box_checked(page_img, bbox, template, w, h, threshold=0.8):
    """Uses template matching to detect crosses"""
    left, top, right, bottom = map(int, bbox)
    crop = page_img[top:bottom, left:right]
    
    # Template matching
    res = cv2.matchTemplate(crop, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    
    # Debug: Uncomment to see matching score
    # print(f"Match confidence: {max_val:.2f}")
    
    return max_val > threshold  # Returns True if good match
'''
#KEEP
def save_tables_to_txt(tables_data, output_file="extracted_data.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for table in tables_data:
            #f.write(f"=== Table {table['table_id']} ===\n")
            f.write(table["text"] + "\n")
            f.write("-" * 40 + "\n\n")  # Separator
    print(f"✅ Saved to: {output_file}")

# Call the function
parsed_data = parse_table_data_from_space_separated_floats(file_path)
tables_data = extracting_pdf(pdf_path, parsed_data)

#detect_visual_cross(pdf_path, parsed_data, output_file)
#detect_checked_boxes(pdf_path,parsed_data,template_path="template.png")
save_tables_to_txt(tables_data, output_file)
crossing1(pdf_path,parsed_data,output_file)



