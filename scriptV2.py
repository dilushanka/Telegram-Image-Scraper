from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeFilename
import os
import logging
from datetime import datetime
from pathlib import Path
import mimetypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Your API credentials (store these securely in environment variables)
api_id = os.getenv('TELEGRAM_API_ID', 'Your-API-key')
api_hash = os.getenv('TELEGRAM_API_HASH', 'Your-API-Hash')
phone_number = os.getenv('TELEGRAM_PHONE', 'Your-Number')

# Group ID can be a username, invite link, or numeric ID
group_identifier = -1001234567890  # Replace with your group ID/username
# Examples:
# group_identifier = -1001234567890  # Numeric ID
# group_identifier = 'username'      # Group username
# group_identifier = 'https://t.me/joinchat/abc123'  # Invite link

# Create a directory to store downloaded images
output_directory = Path('downloaded_images')
output_directory.mkdir(exist_ok=True)

def get_file_extension(media):
    """Determine file extension based on mime type or attributes"""
    if hasattr(media, 'mime_type') and media.mime_type:
        return mimetypes.guess_extension(media.mime_type) or '.jpg'
    return '.jpg'

async def download_images():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        
        logger.info(f"Logged in as {await client.get_me().username}")
        
        try:
            # Get the group entity
            group_entity = await client.get_entity(group_identifier)
            logger.info(f"Accessing group: {group_entity.title}")
            
            # Counter for downloaded files
            downloaded_count = 0
            skipped_count = 0
            error_count = 0
            
            # Get total messages for progress tracking
            total_messages = await client.get_messages(group_entity, limit=1)
            
            async for message in client.iter_messages(group_entity, limit=None):
                try:
                    file_name = None
                    
                    # Check for photo
                    if message.photo:
                        # Create filename with timestamp and message ID
                        date_str = message.date.strftime('%Y%m%d_%H%M%S')
                        file_name = output_directory / f'photo_{date_str}_{message.id}.jpg'
                        await client.download_media(message.photo, file=file_name)
                        downloaded_count += 1
                        logger.info(f"Downloaded photo: {file_name}")
                    
                    # Check for document (could be images, PDFs, etc.)
                    elif message.document:
                        # Check if it's an image
                        if (message.document.mime_type and 
                            message.document.mime_type.startswith('image/')):
                            
                            # Try to get original filename
                            original_filename = None
                            for attr in message.document.attributes:
                                if isinstance(attr, DocumentAttributeFilename):
                                    original_filename = attr.file_name
                                    break
                            
                            if original_filename:
                                file_name = output_directory / original_filename
                            else:
                                ext = get_file_extension(message.document)
                                date_str = message.date.strftime('%Y%m%d_%H%M%S')
                                file_name = output_directory / f'document_{date_str}_{message.id}{ext}'
                            
                            await client.download_media(message.document, file=file_name)
                            downloaded_count += 1
                            logger.info(f"Downloaded document image: {file_name}")
                        else:
                            skipped_count += 1
                    
                    # Check for media in web preview
                    elif message.web_preview and hasattr(message.web_preview, 'photo'):
                        date_str = message.date.strftime('%Y%m%d_%H%M%S')
                        file_name = output_directory / f'webpreview_{date_str}_{message.id}.jpg'
                        await client.download_media(message.web_preview.photo, file=file_name)
                        downloaded_count += 1
                        logger.info(f"Downloaded web preview: {file_name}")
                    
                    # Show progress every 100 messages
                    if message.id % 100 == 0:
                        logger.info(f"Processed message ID: {message.id} | Downloaded: {downloaded_count}")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error downloading message {message.id}: {str(e)}")
                    continue
            
            # Summary
            logger.info("\n" + "="*50)
            logger.info("DOWNLOAD SUMMARY")
            logger.info("="*50)
            logger.info(f"Total downloaded: {downloaded_count}")
            logger.info(f"Skipped (non-images): {skipped_count}")
            logger.info(f"Errors: {error_count}")
            logger.info(f"Files saved in: {output_directory.absolute()}")
            
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            raise

def main():
    """Main function to run the downloader"""
    try:
        # Run the async function
        client = TelegramClient('session_name', api_id, api_hash)
        client.loop.run_until_complete(download_images())
        
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        logger.info("Download process completed")

if __name__ == "__main__":
    main()