from telethon.sync import TelegramClient
import os

# Your API credentials
api_id = 'Your-API-key'
api_hash = 'Your-API-Hash'

# Phone number and login
phone_number = 'Your-Number'
username = 'Your-Username'

# Group ID (# replace with your actual group ID)
group_id = -############

# Create a directory to store downloaded images
output_directory = 'downloaded_images'
os.makedirs(output_directory, exist_ok=True)

# Initialize the client
client = TelegramClient(username, api_id, api_hash)

async def download_images():
    await client.start(phone_number)

    try:
        group_entity = await client.get_entity(group_id)

        async for message in client.iter_messages(group_entity, limit=None):
            if message.photo:
                photo = message.photo
                file_path = os.path.join(output_directory, f'{message.id}.jpg')
                await client.download_media(photo, file=file_path)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.disconnect()

# Run the download function
client.loop.run_until_complete(download_images())