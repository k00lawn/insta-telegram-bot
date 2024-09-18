import instaloader
import time
from telegram import Bot
import asyncio

# Constants
TELEGRAM_BOT_TOKEN = '7398205524:AAG6YzTmB8FIfvfgza4oqbyRokLT3bzl1KM'  # Replace with your Telegram bot token
CHAT_ID = '-1002477858332'                          # Replace with your chat ID or list of chat IDs
POLLING_INTERVAL = 60                              # Poll every minute (in seconds)

# Initialize Instaloader and Telegram Bot
loader = instaloader.Instaloader()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# List to store user data: username and last_post_id
users_data = []

def add_user(username):
    """Add a new user to the users_data list."""
    if any(user['username'] == username for user in users_data):
        print(f"User {username} is already being monitored.")
        return
    
    users_data.append({'username': username, 'last_post_id': None})
    print(f"User {username} added for monitoring.")

def fetch_latest_post(username):
    """Fetch the latest post for a given username."""
    profile = instaloader.Profile.from_username(loader.context, username)
    
    # Get the latest post
    latest_post = next(profile.get_posts())
    
    return latest_post

async def send_latest_post(username):
    """Send the latest post's media URL to Telegram."""
    latest_post = fetch_latest_post(username)
    
    # Get media URL (assuming it's an image; adjust if necessary)
    media_url = latest_post.url
    
    # Send message with media URL to Telegram
    await bot.send_message(chat_id=CHAT_ID, text=f"Latest post from @{username}: {media_url}")
    print(f"Sent latest post URL from @{username} to Telegram.")

async def main():
    # Example usage of adding users
    add_user('instagram')  # Replace with actual username
    add_user('cristiano')  # Replace with actual username

    while True:
        for user in users_data:
            await send_latest_post(user['username'])
        await asyncio.sleep(POLLING_INTERVAL)  # Wait for the specified interval before polling again

# Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())
