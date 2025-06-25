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

def crossing1(pdf_path, parsed_data, output_file="extracted_data.txt"):
    results = []  # Store results for all entries
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        for entry in parsed_data:
            if entry["table_id"] == 1:  # Only process table_id 1
                yes = no = False
                yescor = entry["x"] + entry["width"] - 15
                nocor = entry["x"] + entry["width"] - 30
                
                for y in range(14, int(entry['height']), 14):
                    # Check Yes box
                    ybox = (yescor, y+entry["y"], yescor+15, y+entry["y"] + 14)
                    cropped_page = first_page.crop(ybox)
                    table_text = cropped_page.extract_text()
                    if table_text and "X" in table_text.upper():
                        yes = True
                        break
                    
                    # Check No box
                    nbox = (nocor, y+entry["y"], nocor+15, y+entry["y"] + 14)
                    cropped_page = first_page.crop(nbox)
                    table_text = cropped_page.extract_text()
                    if table_text and "X" in table_text.upper():
                        no = True
                        break
                
                results.append("Yes" if yes else "No" if no else "")

        # Write to file
    with open(output_file, "a") as f:
        f.write("\nCheckbox Results:\n" + "\n".join(results) + "\n")

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



