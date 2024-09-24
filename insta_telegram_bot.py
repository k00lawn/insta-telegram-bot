import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import logging
from dotenv import load_dotenv

load_dotenv()

# Constants
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Replace with your Telegram bot token
POLLING_INTERVAL = 60  

# Initialize Instaloader and Telegram Bot
loader = instaloader.Instaloader()

# List to store user data: user_profile and latest_post_id
users_data = []

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new user to the users_data list."""
    username = context.args[0]
    if any(user['user_profile'].username == username for user in users_data):
        print(f"User @{username} is already being monitored.")
        return
    
    user_profile = instaloader.Profile.from_username(loader.context, username)
    users_data.append({'user_profile': user_profile, 'latest_post_id': None})
    print(f"User @{username} added for monitoring.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{username} Added!')

def fetch_latest_post(user_profile):
    """Fetch the latest post for a given user profile."""
    # Get the latest post
    latest_post = next(user_profile.get_posts())
    
    return latest_post

async def send_latest_post(user, update, context):
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Latest post from @{user_profile.username}: {media_url}")
        print(f"Sent latest post URL from @{user_profile.username} to Telegram.")
    else:
        print(f"No new posts for @{user_profile.username}.")

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in users_data:
            await send_latest_post(user, update, context)


# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Run the main function using asyncio
if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    add_user_handler = CommandHandler('add', add_user)
    refresh_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), refresh)

    application.add_handler(add_user_handler)
    application.add_handler(refresh_handler)

    # Run the bot until you stop it manually (Ctrl+C)
    application.run_polling()