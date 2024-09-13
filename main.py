import os
import random
import pandas as pd
from PIL import Image
import pytesseract
import src.utils

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def predictor(image_link, category_id, entity_name):
    '''
    Download the image and save it to a specified folder.
    '''
    print(f"Processing: {image_link} | Category: {category_id} | Entity: {entity_name}")
    
    try:
        download_folder = os.path.join(os.getcwd(), "temp_images")
        if not os.path.exists(download_folder):
            print("Creating temp_images folder")
            os.makedirs(download_folder)
        
        # Download the image using utils.py functions
        print("Downloading image")
        src.utils.download_image(image_link, download_folder)
        print(f"Image saved to: {os.path.join(download_folder, os.path.basename(image_link))}")
        image_save_path = os.path.join(download_folder, os.path.basename(image_link))
        # Open the image and extract text

        print("Extracting text from image")
        image = Image.open(image_save_path)
        text_in_image = pytesseract.image_to_string(image)
        print("texttttttttt",text_in_image)
    
    except Exception as e:
        print(f"Error processing image: {image_link}. Error: {str(e)}")
    
    return ""  # Ignore return value as requested

if __name__ == "__main__":
    DATASET_FOLDER = "C:/Users/xgadg/Downloads/66e31d6ee96cd_student_resource_3/student_resource 3/dataset"
    
    test = pd.read_csv(os.path.join(DATASET_FOLDER, 'sample_test.csv'))
    
    test['prediction'] = test.apply(
        lambda row: predictor(row['image_link'], row['group_id'], row['entity_name']), axis=1)
    
    output_filename = os.path.join(DATASET_FOLDER, 'test_out.csv')
    test[['index', 'prediction']].to_csv(output_filename, index=False)
