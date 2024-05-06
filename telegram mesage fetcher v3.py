from telethon import TelegramClient
from telethon.errors import ChannelInvalidError, AuthKeyUnregisteredError
from telethon.tl.types import InputChannel
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, errors



# Replace these values with your Telegram API credentials
api_id = '13439427'
api_hash = '545cd223c63a600ba27c287f5327e797'
phone_number = '+917225832206'  # Include the country code

# Replace these values with the correct usernames of the channels you want to monitor
channel_usernames = ['noname05716eng',"foresiet_test_ch"]

session_file = "telegram_session.session"

import os
from telethon.errors import PhoneNumberInvalidError, CodeInvalidError

from telethon import TelegramClient

async def authenticate():
    client = TelegramClient(session_file, api_id, api_hash)

    try:
        await client.start(phone=phone_number)
        if not client.is_user_authorized():
            await client.send_code_request(phone_number)
            code = input('Enter the code: ')
            await client.sign_in(phone_number, code)

        return client
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None



async def get_latest_messages(client, channel_username, offset_id=None, limit=11):
    try:
        entity = await client.get_entity(channel_username.lower())
        if entity:
            channel = InputChannel(entity.id, entity.access_hash)

            # Get the latest messages
            if offset_id is None:
                messages = await client.get_messages(channel, limit=limit)
            else:
                messages = await client.get_messages(channel, offset_id=offset_id, limit=limit)

            # Determine the new offset ID
            if messages:
                new_offset_id = messages[-1].id + 1
            else:
                new_offset_id = None

            processed_messages = []

            for message in messages:
                processed_messages.append(message.text)

            return processed_messages, messages, new_offset_id
        else:
            raise errors.ChannelInvalidError("Channel username is not valid or does not exist.")
    except errors.ChannelInvalidError as e:
        print(f"Error: {e}")
        return [], [], offset_id  # Return the same offset ID to continue fetching messages
    except Exception as e:
        print(f"Failed to retrieve messages from {channel_username}: {e}")
        return [], [], None

async def main():
    client = await authenticate()

    if client:
        offset_id = None  # Initial offset ID is None
        end_time = datetime.now() + timedelta(minutes=50)  # Run for at least 5 minutes
        while datetime.now() < end_time:
            for channel_username in channel_usernames:
                try:
                    processed_messages, original_messages, new_offset_id = await get_latest_messages(client, channel_username, offset_id=offset_id)
                    offset_id = new_offset_id  # Update the offset ID for the next iteration
                except errors.AuthKeyUnregisteredError:
                    print("Session has become invalid. Re-authenticating...")
                    client = await authenticate()
                    if not client:
                        print("Failed to re-authenticate. Exiting.")
                        return
                    offset_id = None  # Reset offset ID after re-authentication

                print(f"\nLatest messages from {channel_username}:")
                for message in original_messages:
                    print(f"{message.sender_id}: {message.text}")

            # Add a short delay between iterations (e.g., 10 seconds)
            await asyncio.sleep(10)  # 10 seconds delay between iterations

        # After running for at least 5 minutes, resume the hourly check
        while True:
            for channel_username in channel_usernames:
                try:
                    processed_messages, original_messages, new_offset_id = await get_latest_messages(client, channel_username, offset_id=offset_id)
                    offset_id = new_offset_id  # Update the offset ID for the next iteration
                except errors.AuthKeyUnregisteredError:
                    print("Session has become invalid. Re-authenticating...")
                    client = await authenticate()
                    if not client:
                        print("Failed to re-authenticate. Exiting.")
                        return
                    offset_id = None  # Reset offset ID after re-authentication

                print(f"\nLatest messages from {channel_username}:")
                for message in original_messages:
                    print(f"{message.sender_id}: {message.text}")

            # Add a delay between iterations (e.g., wait for 1 hour)
            await asyncio.sleep(3600)  # 3600 seconds = 1 hour

if __name__ == "__main__":
    asyncio.run(main())
