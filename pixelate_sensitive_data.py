import os
import cv2
import pytesseract
import numpy as np
import sys

# Function to pixate sensitive areas
def pixate_sensitive_areas(image, sensitive_areas):
    for area in sensitive_areas:
        x, y, w, h = area
        roi = image[y:y+h, x:x+w]
        blurred_roi = cv2.GaussianBlur(roi, (21, 21), 0)
        image[y:y+h, x:x+w] = blurred_roi
    return image

# Input and output directories
input_dir = '/media/sf_input_images/'
output_dir = '/media/sf_output_images/'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each image in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        image_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f'pixated_{filename}')
        
        # Load the image
        image = cv2.imread(image_path)
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Initialize list to store sensitive areas
        sensitive_areas = []
        
        # Loop through the extracted text data
        for i in range(len(text['text'])):
            # Get the text and its bounding box coordinates
            text_str = text['text'][i].strip()
            if text_str:
                x, y, w, h = text['left'][i], text['top'][i], text['width'][i], text['height'][i]
                sensitive_areas.append((x, y, w, h))
        
        # Pixate the sensitive areas
        pixated_image = pixate_sensitive_areas(image.copy(), sensitive_areas)
        
        # Save the pixated image
        cv2.imwrite(output_path, pixated_image)

        print(f'Processed and saved: {filename}')

print('All images processed and saved.')
