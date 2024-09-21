import instaloader
import time
from telegram import Bot
import asyncio

# Constants
TELEGRAM_BOT_TOKEN = 'YOUR-TELEGRAM-BOT-TOKEN'  # Replace with your Telegram bot token
CHAT_ID = 'YOUR-TELEGRAM-CHAT-ID'             # Replace with your chat ID or list of chat IDs
POLLING_INTERVAL = 60  

# Initialize Instaloader and Telegram Bot
loader = instaloader.Instaloader()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# List to store user data: user_profile and latest_post_id
users_data = []

def add_user(username):
    """Add a new user to the users_data list."""
    if any(user['user_profile'].username == username for user in users_data):
        print(f"User @{username} is already being monitored.")
        return
    
    user_profile = instaloader.Profile.from_username(loader.context, username)
    users_data.append({'user_profile': user_profile, 'latest_post_id': None})
    print(f"User @{username} added for monitoring.")

def fetch_latest_post(user_profile):
    """Fetch the latest post for a given user profile."""
    # Get the latest post
    latest_post = next(user_profile.get_posts())
    
    return latest_post

async def send_latest_post(user):
    """Check for new posts, update latest_post_id, and send to Telegram if new."""
    user_profile = user['user_profile']
    latest_post = fetch_latest_post(user_profile)
    
    # Check if the latest post is already recorded
    if user['latest_post_id'] is None or user['latest_post_id'] != latest_post.mediaid:
        # Update latest_post_id in users_data
        user['latest_post_id'] = latest_post.mediaid
        
        # Get media URL (assuming it's an image; adjust if necessary)
        media_url = latest_post.url
        
        # Send message with media URL to Telegram
        await bot.send_message(chat_id=CHAT_ID, text=f"Latest post from @{user_profile.username}: {media_url}")
        print(f"Sent latest post URL from @{user_profile.username} to Telegram.")
    else:
        print(f"No new posts for @{user_profile.username}.")

async def main():
    # Example usage of adding users
    add_user('instagram')  # Replace with actual username
    add_user('cristiano')  # Replace with actual username

    while True:
        for user in users_data:
            await send_latest_post(user)
        await asyncio.sleep(POLLING_INTERVAL)  # Wait for the specified interval before polling again

# Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())