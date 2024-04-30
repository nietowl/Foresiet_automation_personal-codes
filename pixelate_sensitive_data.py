import os
import cv2
import pytesseract
import numpy as np
import sys

# Function to create a spaced-out pattern mask
def create_pattern_mask(image_shape, sensitive_areas, pattern_size):
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    
    for area in sensitive_areas:
        x, y, w, h = area
        for i in range(x, x + w, pattern_size):
            if i + pattern_size <= x + w:
                mask[y:y+h, i:i+pattern_size] = 255
    
    return mask

# Function to pixate sensitive areas with a pattern mask
def pixate_sensitive_areas_pattern(image, pattern_mask):
    pattern_color = (0, 0, 0)  # Color of the pattern (black in this case)
    pixated_image = image.copy()
    pixated_image[pattern_mask == 255] = pattern_color
    return pixated_image

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
        
        # Create a spaced-out pattern mask
        pattern_size = 30  # Adjust as needed
        pattern_mask = create_pattern_mask(image.shape, sensitive_areas, pattern_size)
        
        # Pixate the sensitive areas with the pattern mask
        pixated_image = pixate_sensitive_areas_pattern(image.copy(), pattern_mask)
        
        # Save the pixated image
        cv2.imwrite(output_path, pixated_image)

        print(f'Processed and saved: {filename}')

print('All images processed and saved.')
