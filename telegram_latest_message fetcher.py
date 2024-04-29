from telethon.sync import TelegramClient
from telethon.tl.types import InputChannel
from telethon.errors import SessionPasswordNeededError
import os
import json
from datetime import datetime

# Replace these values with your Telegram API credentials
api_id = '13439427'
api_hash = '545cd223c63a600ba27c287f5327e797'
phone_number = '+917225832206'  # Include the country code

# Replace these values with the usernames of the channels you want to monitor
channel_usernames = ['noname05716eng']

def authenticate():
    client = TelegramClient('session_name', api_id, api_hash)

    try:
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
            # Handle two-step verification
            try:
                client.sign_in(phone_number, input('Enter the code: '))
            except SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter your password: ')
                client.sign_in(password=password)

        return client
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def download_media_with_unique_id(client, message, file_extension=".jpg"):
    try:
        media = message.media
        if media:
            if hasattr(media, "photo"):
                # Handle photo (image) download
                for photo_size in media.photo.sizes:
                    if photo_size.type == 'x':
                        # Generate a unique identifier using the message ID
                        unique_id = f"{message.id}"

                        # Convert timestamp to a date string
                        timestamp = message.date.timestamp()
                        media_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

                        # Create a subfolder based on the media's date
                        media_folder = os.path.join("media/raw", media_date)
                        os.makedirs(media_folder, exist_ok=True)

                        file_path = os.path.join(media_folder, f"{unique_id}{file_extension}")
                        client.download_media(message, file=file_path)  # Save the file

                        # Store the association between unique ID and message
                        message_mapping[unique_id] = {
                            "text": message.text,
                            "media_path": file_path
                        }
                        save_to_file(message_mapping, "message_mappings.json")  # Save to JSON file
                        break
            elif hasattr(media, "document"):
                # Handle other types of media (documents, etc.)
                # Similar logic as above for saving media
                pass  # Adjust as needed
    except Exception as e:
        print(f"Failed to download media: {e}")

def get_latest_messages(client, channel_username, limit=6):
    try:
        entity = client.get_entity(channel_username.lower())
        channel = InputChannel(entity.id, entity.access_hash)

        messages = client.get_messages(channel, limit=limit)
        processed_messages = []

        for message in messages:
            if "**Follow us**[Russian version](https://t.me/noname05716)|[DDoSia Project](https://t.me/+igupZcC_O45jMGY1)|[Reserve channel](https://t.me/noname05716_reserve)" in message.text:
                processed_message = message.text.replace("**Follow us**[Russian version](https://t.me/noname05716)|[DDoSia Project](https://t.me/+igupZcC_O45jMGY1)|[Reserve channel](https://t.me/noname05716_reserve)", "")
                processed_messages.append(processed_message)
            
            # Download media if available
            download_media_with_unique_id(client, message)

        return processed_messages, messages  # Return both processed and original messages
    except Exception as e:
        print(f"Failed to retrieve messages from {channel_username}: {e}")
        return [], []




def save_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    global message_mapping
    message_mapping = {}  # Define the message_mapping dictionary

    client = authenticate()

    if client:
        for channel_username in channel_usernames:
            processed_messages, original_messages = get_latest_messages(client, channel_username)
            
            print(f"\nLatest messages from {channel_username}:")
            for message in original_messages:
                print(f"{message.sender_id}: {message.text}")

        client.disconnect()

if __name__ == "__main__":
    main()
