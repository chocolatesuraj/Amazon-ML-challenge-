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

# Sample input text
text = """awd test
1238madw
823W
100.23 m

Power adapter

@AC cable

adapter

ZL LED drive

Assembly Display

Fan drive
"""

# Example usage for the entity 'wattage'
entity_key = 'wattage'  # You can change this to test other entities
valid_units = entity_unit_map[entity_key]
unit_mapping = generate_abbreviation_map(entity_key, entity_unit_map, abbreviation_map)

# Extract the number and unit from the text
answer = extract_number_and_unit(text, valid_units, unit_mapping)
print(f"Answer: {answer}")
