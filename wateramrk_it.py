import os
from PIL import Image, ImageDraw, ImageFont, ImageFile
from datetime import datetime

def get_average_color(image):
    """
    Calculate the average color of an image.
    """
    image = image.convert("RGB")
    width, height = image.size
    pixels = image.load()
    r_total = g_total = b_total = 0

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            r_total += r
            g_total += g
            b_total += b

    total_pixels = width * height
    avg_color = (r_total // total_pixels, g_total // total_pixels, b_total // total_pixels)
    return avg_color

def apply_metadata_and_watermark(input_image_path, output_folder_path, text_to_add, max_pixels=178956970):
    try:
        # Set a higher limit for image processing
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        # Open the input image
        input_image = Image.open(input_image_path)
        width, height = input_image.size

        # Resize if the image has too many pixels
        if width * height > max_pixels:
            input_image = input_image.resize((width // 2, height // 2))

        # Add metadata
        metadata = {
            'Source': 'foresiet.com',
            'Copyright': 'Foresiet',
            'Author': 'Foresiet threat intelligence',
            'Creation Time': datetime.now().strftime('%d:%m:%Y %H:%M:%S'),
        }
        input_image.info.update(metadata)

        # Calculate the average color
        avg_color = get_average_color(input_image)

        # Determine which watermark to use based on the average color
        watermark_image_path = os.path.join(
            os.path.dirname(__file__), 
            'watermark_dark.png' if sum(avg_color) / 3 > 128 else 'watermark_light.png'
        )
        watermark_image = Image.open(watermark_image_path)

        # Convert the input image to RGB mode
        input_image = input_image.convert("RGB")

        # Resize the watermark
        watermark_width, watermark_height = watermark_image.size
        scaling_factor = min(width / watermark_width, height / watermark_height)
        watermark_image = watermark_image.resize(
            (int(watermark_width * scaling_factor), int(watermark_height * scaling_factor))
        )

        # Paste the watermark
        x_offset = (width - watermark_image.width) // 2
        y_offset = (height - watermark_image.height) // 2
        input_image.paste(watermark_image, (x_offset, y_offset), watermark_image)

        # Add text with yellow background strip
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_size = 20
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            print(f"Error: Could not open font resource at {font_path}")
            return

        draw = ImageDraw.Draw(input_image)
        text_bbox = draw.textbbox((0, 0), text_to_add, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        strip_padding = 10

        strip_x_start = 10
        strip_x_end = strip_x_start + text_width + 2 * strip_padding
        strip_y_start = height - text_height - 2 * strip_padding - 10
        strip_y_end = height - 10
        
        # Draw the yellow strip
        draw.rectangle([(strip_x_start, strip_y_start), (strip_x_end, strip_y_end)], fill="yellow")

        # Draw the text on top of the yellow strip
        text_position = (strip_x_start + strip_padding, strip_y_start + strip_padding)
        text_color = (0, 0, 0)
        draw.text(text_position, text_to_add, font=font, fill=text_color)

        # Save the output image
        output_image_path = os.path.join(output_folder_path, os.path.basename(input_image_path))
        input_image.save(output_image_path)
        
        # Print the file names
        print(f"Processed: {os.path.basename(input_image_path)}")
        print(f"Output: {output_image_path}")

        # Delete the input image from the input folder
        os.remove(input_image_path)
        print(f"Deleted: {os.path.basename(input_image_path)}")

        return output_image_path

    except Image.DecompressionBombError as e:
        print(f"DecompressionBombError: {e}")

    except Exception as e:
        print(f"Error processing {input_image_path}: {e}")

def process_images_in_folder(input_folder_path, output_folder_path, text_to_add):
    os.makedirs(output_folder_path, exist_ok=True)

    for filename in os.listdir(input_folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_image_path = os.path.join(input_folder_path, filename)
            apply_metadata_and_watermark(input_image_path, output_folder_path, text_to_add)

# Example of usage:
input_folder = '/media/sf_input_images/'
output_folder = '/media/sf_output_images/'
text_to_add = "foresiet.com"
process_images_in_folder(input_folder, output_folder, text_to_add)
