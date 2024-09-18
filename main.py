import os
import random
import pandas as pd
from PIL import Image
import pytesseract
import src.utils
import re
import cv2


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
    'centimetre': ['cm', 'centimeter', 'centimetres', 'centimeters', 'cent', 'cms', 'c.m.', 'cm.', 'centim', '¢m', 'c₥', 'cₘ','em'],
    'foot': ['ft', 'foot', 'feet', 'ft.', 'feet', 'f.t.', 'ft', 'fe', '′', 'ftm'],
    'inch': ['in', 'inch', 'inches', 'in.', 'ins', 'inchs', 'i.n.', 'in', '"', '″', 'in'],
    'metre': ['m', 'meter', 'metres', 'meters', 'mtr', 'met', 'mts', 'mt', 'm.', '₥', 'mₘ'],
    'millimetre': ['mm', 'millimeter', 'millimetres', 'millimeters', 'mil', 'mms', 'mm.', 'mil.', 'ₘₘ', 'mmₘ'],
    'yard': ['yd', 'yard', 'yards', 'yds', 'yd.', 'yds', 'ydₘ'],
    'gram': ['g', 'gram', 'grams', 'gm', 'gms', 'gr', 'grs', '₉', 'gₘ'],
    'kilogram': ['kg', 'kilo', 'kilogram', 'kilograms', 'kgs', 'klg', 'k.g.', 'kg.', 'ₖ₉', 'kgₘ'],
    'microgram': ['mcg', 'microgram', 'micrograms', 'mcgs', 'μg', 'ug', 'mc', 'μ₉', 'mcₘ'],
    'milligram': ['mg', 'milligram', 'milligrams', 'mgs', 'mg.', 'millig', 'ₘ₉', 'mgₘ'],
    'ounce': ['oz', 'ounce', 'ounces', 'ozs', 'oz.', 'o.z.', '℥'],
    'pound': ['lb', 'pound', 'pounds', 'lbs', 'lbm', 'lb.', 'pound', 'pds', 'ₗₑ', 'lbₘ'],
    'ton': ['t', 'ton', 'tons', 'tn', 'tns', 't.', 'tonne', 'ₜ', 'tonₘ'],
    'kilovolt': ['kv', 'kilovolt', 'kilovolts', 'kvs', 'kV', 'KV', 'ₖV'],
    'millivolt': ['mv', 'millivolt', 'millivolts', 'mvs', 'mV', 'mV', 'ₘV'],
    'volt': ['v', 'volt', 'volts', 'vs', 'v.', 'V', 'ₜ'],
    'kilowatt': ['kw', 'kilowatt', 'kilowatts', 'kws', 'kW', 'KW', 'ₖW'],
    'watt': ['w', 'watt', 'watts', 'ws', 'w.', 'W', 'ₙ'],
    'centilitre': ['cl', 'centilitre', 'centilitres', 'cL', 'c.l.', 'cl', 'ₗ'],
    'cubic foot': ['cu ft', 'cubic foot', 'cubic feet', 'cf', 'cuft', 'ft³', 'ft3'],
    'cubic inch': ['cu in', 'cubic inch', 'cubic inches', 'ci', 'cuin', 'in³', 'in3'],
    'cup': ['cup', 'cups', 'c', 'cu', 'cps', 'ₗ'],
    'decilitre': ['dl', 'decilitre', 'decilitres', 'dL', 'd.l.', 'dl', 'ₗ'],
    'fluid ounce': ['fl oz', 'fluid ounce', 'fluid ounces', 'floz', 'fl oz', 'f.loz', '℥'],
    'gallon': ['gal', 'gallon', 'gallons', 'gals', 'gal.', 'gall', 'ₗ'],
    'imperial gallon': ['imp gal', 'imperial gallon', 'imperial gallons', 'imp.gal', 'imp gal', 'ₗ'],
    'litre': ['l', 'litre', 'liter', 'litres', 'liters', 'L', 'ltr', 'lt', 'ₗ'],
    'microlitre': ['μl', 'microlitre', 'microl']}


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
    text = text.replace('"', 'inch').replace('″', 'inch')
    text = text.replace("'", 'foot').replace('′', 'foot')  # foot
    text = text.replace(',', '.')  # Replace comma with decimal point

    """
    Extracts numbers followed by units from a given text.

    Args:
    text (str): The input text.
    valid_units (list): A list of valid unit names.
    unit_mapping (dict): A dictionary mapping unit abbreviations to full names.

    Returns:
    list: A list of extracted number-unit pairs.
    """

    # Create a regex pattern for the valid units or abbreviations
    unit_pattern = '|'.join([re.escape(unit) for unit in valid_units] + [re.escape(abbrev) for abbrev in unit_mapping.keys()])

    # Regex to match an integer or decimal number followed by any valid unit or abbreviation
    pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)'

    matches = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
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
            # No valid unit found, skip this match
            continue

        # Append the matched number and unit
        matches.append(f"{number} {full_unit}")

    if(len(matches) == 0):
        return ""
    
    return matches[0]



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

        #image = Image.open(image_save_path)
        image = cv2.imread(image_save_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        custom_config = r'--oem 1'


        text_in_image = pytesseract.image_to_string(thresh, config=custom_config)
        print("texttttttttt",text_in_image)

        valid_units = entity_unit_map[entity_name]
        unit_mapping = generate_abbreviation_map(entity_name, entity_unit_map, abbreviation_map)

        # Extract the number and unit from the text
        answer = extract_number_and_unit(text_in_image, valid_units, unit_mapping)
        output_file = "C:/Users/xgadg/Downloads/66e31d6ee96cd_student_resource_3/student_resource 3/dataset/errors.csv"

        # Open the file in append mode

        # with open(output_file, 'a') as f:
        #     # Check if answer is empty
        #     if answer == "":
        #         # Write to file
        #         f.write(f"\n*****************\ntext_in_image: {text_in_image}, extracted text: {answer}\n,entity_name: {entity_name}, image_link: {image_link}\n*****************\n")

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
