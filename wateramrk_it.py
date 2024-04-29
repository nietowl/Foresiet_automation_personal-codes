import os
from PIL import Image, ImageFile
from datetime import datetime

def get_average_color(image):
    """
    Calculate the average color of an image.
    """
    image = image.convert("RGB")
    width, height = image.size
    pixels = image.load()
    r_total = 0
    g_total = 0
    b_total = 0

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            r_total += r
            g_total += g
            b_total += b

    total_pixels = width * height
    avg_color = (r_total // total_pixels, g_total // total_pixels, b_total // total_pixels)
    return avg_color

def apply_metadata_and_watermark(input_image_path, output_folder_path, max_pixels=178956970):
    try:
        # Set a higher limit for image processing
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        # Open the input image
        input_image = Image.open(input_image_path)

        # Check image dimensions before opening
        width, height = input_image.size

        if width * height > max_pixels:
            # Resize the image to a more manageable size
            resized_image = input_image.resize((int(width / 2), int(height / 2)))
        else:
            resized_image = input_image

        # Add metadata
        metadata = {
            'Source': 'foresiet.com',
            'Copyright': 'Foresiet',
            'Author': 'Foresiet threat intelligence',
            'Creation Time': datetime.now().strftime('%d:%m:%Y %H:%M:%S'),
        }

        resized_image.info.update(metadata)

        # Calculate the average color of the image
        avg_color = get_average_color(resized_image)

        # Determine which watermark to use based on the average color
        if sum(avg_color) / 3 > 128:  # Light background
            watermark_image_path = os.path.join(os.path.dirname(__file__), 'watermark_dark.png')
        else:  # Dark background
            watermark_image_path = os.path.join(os.path.dirname(__file__), 'watermark_light.png')
        # Open the appropriate watermark image
        watermark_image = Image.open(watermark_image_path)

        # Convert the input image to RGB mode
        resized_image = resized_image.convert("RGB")

        # Determine the scaling factor for the watermark
        watermark_width, watermark_height = watermark_image.size
        scaling_factor = min(width / watermark_width, height / watermark_height)

        # Calculate the size of the scaled watermark
        scaled_width = int(watermark_width * scaling_factor)
        scaled_height = int(watermark_height * scaling_factor)

        # Resize the watermark image using the calculated size
        watermark_image = watermark_image.resize((scaled_width, scaled_height))

        # Calculate the position to paste the watermark (centered)
        x_offset = (width - scaled_width) // 2
        y_offset = (height - scaled_height) // 2

        # Paste the watermark onto the input image
        resized_image.paste(watermark_image, (x_offset, y_offset), watermark_image)

        # Determine the output path for the watermarked image
        input_filename = os.path.basename(input_image_path)
        output_image_path = os.path.join(output_folder_path, input_filename)

        # Save the watermarked image
        resized_image.save(output_image_path)

        # Print the file names
        print(f"Processed: {input_filename}")
        # print(f"Output: {output_image_path}")

        # Delete the input image from the input folder
        os.remove(input_image_path)
        print(f"Deleted: {input_filename}")

        # Return the path of the watermarked image
        return output_image_path

    except PIL.Image.DecompressionBombError as e:
        print(f"DecompressionBombError: {e}")
        # Handle the error, e.g., skip the image or display an error message

    except Exception as e:
        print(f"Error processing {input_image_path}: {e}")

def process_images_in_folder(input_folder_path, output_folder_path):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)

    # Iterate over files in the input folder
    for filename in os.listdir(input_folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_image_path = os.path.join(input_folder_path, filename)
            apply_metadata_and_watermark(input_image_path, output_folder_path)


# Example of usage:
input_folder = '/media/sf_input_images/'
output_folder = '/media/sf_output_images/'
process_images_in_folder(input_folder, output_folder)
