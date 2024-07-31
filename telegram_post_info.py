from telethon import TelegramClient, events
import configparser
import asyncio
from datetime import datetime, timezone

# Read credentials from config-p.ini
config = configparser.ConfigParser()
config.read('/home/cipher/all_funtion/config-p.ini')

api_id = config['telegram']['api_id']
api_hash = config['telegram']['api_hash']
phone_number = config['telegram']['phone_number']
session_file = "telegram_session.session"

async def authenticate():
    client = TelegramClient(session_file, api_id, api_hash)

    try:
        await client.start(phone=phone_number)
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            code = input('Enter the code: ')
            await client.sign_in(phone_number, code)

        return client
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

async def get_message_info(client, url):
    try:
        # Parse the URL to extract chat ID and message ID
        parts = url.split('/')
        chat_username = parts[-2]
        message_id = int(parts[-1])

        # Get the chat entity and message details
        chat = await client.get_entity(chat_username)
        message = await client.get_messages(chat, ids=message_id)

        if not message:
            print("Message not found.")
            return

        # Extract information
        posted_date = message.date
        creation_date = datetime.fromtimestamp(message.date.timestamp(), timezone.utc)
        edited_date = datetime.fromtimestamp(message.edit_date.timestamp(), timezone.utc) if message.edit_date else None
        sender_name = None
        forwarded_name = None
        forwarded_channel_in = None
        forwarded_channel_from = None
        forwarded_date = None

        if message.sender_id:
            sender = await message.get_sender()
            sender_name = sender.username if sender else None

        if message.forward:
            forward = message.forward
            forwarded_name = (await forward.sender).username if forward.sender_id else None
            forwarded_channel_in = forward.chat.username if forward.chat else None
            forwarded_channel_from = forward.from_name
            forwarded_date = forward.date

        # Print the extracted information
        print(f"Posted Date: {posted_date}")
        print(f"Creation Date: {creation_date}")
        print(f"Edited Date: {edited_date}")
        print(f"Sender Name: {sender_name}")
        print(f"Forwarded Name: {forwarded_name}")
        print(f"Forwarded Channel In: {forwarded_channel_in}")
        print(f"Forwarded Channel From: {forwarded_channel_from}")
        print(f"Forwarded Date: {forwarded_date}")

    except Exception as e:
        print(f"Error retrieving message info: {e}")

async def main():
    url = input('Enter the Telegram message URL: ')
    client = await authenticate()
    if client:
        await get_message_info(client, url)
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
