import asyncio
from telethon import TelegramClient
from telethon.errors import ChannelInvalidError, AuthKeyUnregisteredError, UsernameNotOccupiedError
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import User, Channel, Chat

async def get_entity_details(client, entity):
    if isinstance(entity, User):
        details = f"ID: {entity.id}, Type: User, Username: {entity.username}, " \
                  f"First Name: {entity.first_name}, Last Name: {entity.last_name}, " \
                  f"Phone: {entity.phone}, Status: {entity.status}"
    elif isinstance(entity, Channel):
        details = f"ID: {entity.id}, Type: Channel/Group, Title: {entity.title}, " \
                  f"Creation Date: {entity.date}, " \
                  f"Number of Members: {getattr(entity, 'participants_count', 'Unknown')}"
    elif isinstance(entity, Chat):
        details = f"ID: {entity.id}, Type: Chat, Title: {entity.title}, " \
                  f"Creation Date: {entity.date}, " \
                  f"Number of Participants: {getattr(entity, 'participants_count', 'Unknown')}"
    else:
        details = f"ID: {entity.id}, Type: Unknown"
    return details

async def search_telegram_entities(client, queries):
    results = []
    for query in queries:
        try:
            response = await client(SearchRequest(q=query, limit=1000))
            for user in response.users:
                details = await get_entity_details(client, user)
                results.append(details)
                print(f"Match found: {details}")

            for chat in response.chats:
                details = await get_entity_details(client, chat)
                results.append(details)
                print(f"Match found: {details}")
        except Exception as e:
            results.append(f"An error occurred while searching for '{query}': {e}")
            print(f"An error occurred while searching for '{query}': {e}")

    await client.disconnect()
    return results
