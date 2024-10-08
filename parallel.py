import os
import random
import pandas as pd
from PIL import Image
import pytesseract
import src.utils
import re


# The mapping of entity to valid units
entity_unit_map = {
    'width': {'centimetre', 'foot', 'inch', 'metre', 'millimetre', 'yard'},
    'depth': {'centimetre', 'foot', 'inch', 'metre', 'millimetre', 'yard'},
    'height': {'centimetre', 'foot', 'inch', 'metre', 'millimetre', 'yard'},
    'item_weight': {'gram', 'kilogram', 'microgram', 'milligram', 'ounce', 'pound', 'ton'},
    'maximum_weight_recommendation': {'gram', 'kilogram', 'microgram', 'milligram', 'ounce', 'pound', 'ton'},
    'voltage': {'kilovolt', 'millivolt', 'volt'},
    'wattage': {'kilowatt', 'watt'},
    'item_volume': {'centilitre', 'cubic foot', 'cubic inch', 'cup', 'decilitre', 'fluid ounce', 'gallon', 'imperial gallon', 'litre', 'microlitre', 'millilitre', 'pint', 'quart'}
}

# Abbreviation mappings for various units, each unit can have multiple abbreviations
abbreviation_map = {
    'centimetre': ['cm', 'centimeter', 'centimetres', 'centimeters'],
    'foot': ['ft', 'foot', 'feet'],
    'inch': ['in', 'inch', 'inches'],
    'metre': ['m', 'meter', 'metres', 'meters'],
    'millimetre': ['mm', 'millimeter', 'millimetres', 'millimeters'],
    'yard': ['yd', 'yard', 'yards'],
    'gram': ['g', 'gram', 'grams'],
    'kilogram': ['kg', 'kilo', 'kilogram', 'kilograms'],
    'microgram': ['mcg', 'microgram', 'micrograms'],
    'milligram': ['mg', 'milligram', 'milligrams'],
    'ounce': ['oz', 'ounce', 'ounces'],
    'pound': ['lb', 'pound', 'pounds'],
    'ton': ['t', 'ton', 'tons'],
    'kilovolt': ['kv', 'kilovolt', 'kilovolts'],
    'millivolt': ['mv', 'millivolt', 'millivolts'],
    'volt': ['v', 'volt', 'volts'],
    'kilowatt': ['kw', 'kilowatt', 'kilowatts'],
    'watt': ['w', 'watt', 'watts'],
    'centilitre': ['cl', 'centilitre', 'centilitres'],
    'cubic foot': ['cu ft', 'cubic foot', 'cubic feet'],
    'cubic inch': ['cu in', 'cubic inch', 'cubic inches'],
    'cup': ['cup', 'cups'],
    'decilitre': ['dl', 'decilitre', 'decilitres'],
    'fluid ounce': ['fl oz', 'fluid ounce', 'fluid ounces'],
    'gallon': ['gal', 'gallon', 'gallons'],
    'imperial gallon': ['imp gal', 'imperial gallon', 'imperial gallons'],
    'litre': ['l', 'litre', 'liter', 'litres', 'liters'],
    'microlitre': ['μl', 'microlitre', 'microlitres'],
    'millilitre': ['ml', 'millilitre', 'milliliter', 'millilitres', 'milliliters'],
    'pint': ['pt', 'pint', 'pints'],
    'quart': ['qt', 'quart', 'quarts']
}


# Function to generate abbreviation map for a specific entity
def generate_abbreviation_map(entity_key, entity_unit_map, abbreviation_map):
    valid_units = entity_unit_map.get(entity_key, set())
    unit_abbreviation_mapping = {}
    
    # Loop over the valid units and map their abbreviations
    for unit in valid_units:
        if unit in abbreviation_map:
            for abbrev in abbreviation_map[unit]:
                unit_abbreviation_mapping[abbrev] = unit
        # Also include the full unit as valid
        unit_abbreviation_mapping[unit] = unit
    
    return unit_abbreviation_mapping

# Function to map units and extract the number and unit, including decimals
def extract_number_and_unit(text, valid_units, unit_mapping):
    # Create a regex pattern for the valid units or abbreviations
    unit_pattern = '|'.join([re.escape(unit) for unit in valid_units] + [re.escape(abbrev) for abbrev in unit_mapping.keys()])
    
    # Regex to match an integer or decimal number followed by any valid unit or abbreviation
    match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)', text, re.IGNORECASE)
    
    if match:
        number = match.group(1)
        unit_abbreviation = match.group(2).lower()
        
        # Check if the matched unit or abbreviation is valid
        if unit_abbreviation in unit_mapping:
            # Convert abbreviation to full unit name
            full_unit = unit_mapping[unit_abbreviation]
        elif unit_abbreviation in valid_units:
            # It's already a valid unit
            full_unit = unit_abbreviation
        else:
            # No valid unit found
            return ""
        
        # Return the matched number and the corresponding unit
        return f"{number} {full_unit}"
    return ""



pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def predictor(image_link, category_id, entity_name):
    '''
    Download the image and save it to a specified folder.
    '''
    #print(f"Processing: {image_link} | Category: {category_id} | Entity: {entity_name}")
    
    try:
        download_folder = os.path.join(os.getcwd(), "temp_images")
        if not os.path.exists(download_folder):
            #print("Creating temp_images folder")
            os.makedirs(download_folder)
        
        # Download the image using utils.py functions
        #print("Downloading image")
        src.utils.download_image(image_link, download_folder)
        #print(f"Image saved to: {os.path.join(download_folder, os.path.basename(image_link))}")
        image_save_path = os.path.join(download_folder, os.path.basename(image_link))
        # Open the image and extract text

        #print("Extracting text from image")
        image = Image.open(image_save_path)
        text_in_image = pytesseract.image_to_string(image)
        #print("texttttttttt",text_in_image)

        valid_units = entity_unit_map[entity_name]
        unit_mapping = generate_abbreviation_map(entity_name, entity_unit_map, abbreviation_map)

        # Extract the number and unit from the text
        answer = extract_number_and_unit(text_in_image, valid_units, unit_mapping)
        #print(f"Answer: {answer}")
        return answer

        
    
    except Exception as e:
        print(f"Error processing image: {image_link}. Error: {str(e)}")
    
    return ""  # Ignore return value as requested

import os
import pandas as pd
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_row(row, previous_results, output_filename):
    index = row['index']
    image_link = row['image_link']
    category_id = row['group_id']
    entity_name = row['entity_name']

    # Check if the index already exists in previous results
    if index in previous_results['index'].values:
        print(f"Index {index} already processed, skipping.")
        return index, None  # Skip this index

    # Process the row and get the prediction
    prediction = predictor(image_link, category_id, entity_name)

    # Append the new result to the output file
    with open(output_filename, 'a') as f:
        f.write(f"{index},{prediction}\n")

    #print(f"Processed index {index} with prediction: {prediction}")
    return index, prediction

if __name__ == "__main__":
    DATASET_FOLDER = "C:/Users/xgadg/Downloads/66e31d6ee96cd_student_resource_3/student_resource 3/dataset"
    output_filename = os.path.join(DATASET_FOLDER, 'test_out.csv')

    # Initialize previous results as an empty DataFrame if the file does not exist or is empty
    if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
        previous_results = pd.read_csv(output_filename)
    else:
        # Create an empty DataFrame for previous results
        previous_results = pd.DataFrame(columns=['index', 'prediction'])

    # Load the test CSV
    test = pd.read_csv(os.path.join(DATASET_FOLDER, 'test.csv'))
    total_rows = len(test)
    
    # Create a ThreadPoolExecutor to handle multithreading
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        
        # Submit tasks to the executor
        for _, row in test.iterrows():
            futures.append(executor.submit(process_row, row, previous_results, output_filename))

        # Process the results
        processed_rows = 0
        for future in as_completed(futures):
            index, prediction = future.result()
            if prediction is not None:
                processed_rows += 1
                progress_percentage = (processed_rows / total_rows) * 100
                print(f"Progress: {processed_rows}/{total_rows} ({progress_percentage:.2f}%)")

    print(f"Results appended to: {output_filename}")
