from telethon import TelegramClient
from telethon.errors import ChannelInvalidError, AuthKeyUnregisteredError
from telethon.tl.types import InputChannel
from telethon.sessions import StringSession
import asyncio

# Replace these values with your Telegram API credentials
api_id = '13439427'
api_hash = '545cd223c63a600ba27c287f5327e797'
phone_number = '+917225832206'  # Include the country code

# Replace these values with the correct usernames of the channels you want to monitor
channel_usernames = ['noname05716eng']

async def authenticate():
    client = TelegramClient(StringSession(), api_id, api_hash)

    try:
        await client.connect()
        if not await client.is_user_authorized():
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
            
            if offset_id is None:
                messages = await client.get_messages(channel, limit=limit)
            else:
                messages = await client.get_messages(channel, offset_id=offset_id, limit=limit)

            processed_messages = []

            for message in messages:
                processed_messages.append(message.text)

            return processed_messages, messages
        else:
            raise ChannelInvalidError("Channel username is not valid or does not exist.")
    except ChannelInvalidError as e:
        print(f"Error: {e}")
        return [], []
    except Exception as e:
        print(f"Failed to retrieve messages from {channel_username}: {e}")
        return [], []

async def main():
    client = await authenticate()

    if client:
        for channel_username in channel_usernames:
            try:
                processed_messages, original_messages = await get_latest_messages(client, channel_username)
            except AuthKeyUnregisteredError:
                print("Session has become invalid. Re-authenticating...")
                client = await authenticate()
                if not client:
                    print("Failed to re-authenticate. Exiting.")
                    return
                processed_messages, original_messages = await get_latest_messages(client, channel_username)
            
            print(f"\nLatest messages from {channel_username}:")
            for message in original_messages:
                print(f"{message.sender_id}: {message.text}")

        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
