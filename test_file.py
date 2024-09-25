import os
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import logging
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Constants
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Replace with your Telegram bot token

# Initialize Instaloader and Telegram Bot
loader = instaloader.Instaloader()

# List to store user data: user_profile and latest_post_id
users_data = []

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new user to the users_data list."""
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a username.")
        return
    
    username = context.args[0]
    if any(user['user_profile'].username == username for user in users_data):
        print(f"User @{username} is already being monitored.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"User @{username} is already being monitored.")
        return
    
    user_profile = instaloader.Profile.from_username(loader.context, username)
    users_data.append({'user_profile': user_profile, 'latest_post_id': None})
    print(f"User @{username} added for monitoring.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'User @{username} added!')

def fetch_all_posts_today(user_profile):
    """Fetch all posts for a given user profile that were posted today."""
    today = datetime.now().date()
    today_posts = []

    for post in user_profile.get_posts():
        if post.date.date() == today:
            today_posts.append(post)
        else:
            break

    return today_posts

async def send_today_posts(user, update, context):
    """Check for today's posts and send them to Telegram if available."""
    user_profile = user['user_profile']
    today_posts = fetch_all_posts_today(user_profile)
    
    if today_posts:
        for post in today_posts:
            media_url = post.url  # Get media URL (assuming it's an image; adjust if necessary)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Post from @{user_profile.username}: {media_url}")
            print(f"Sent post URL from @{user_profile.username} to Telegram: {media_url}")
    else:
        print(f"No new posts for @{user_profile.username} today.")

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Refresh and check for today's posts for all users."""
    for user in users_data:
        await send_today_posts(user, update, context)

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
    refresh_handler = CommandHandler('refresh', refresh)  # Use command instead of message filter

    application.add_handler(add_user_handler)
    application.add_handler(refresh_handler)

    # Run the bot until you stop it manually (Ctrl+C)
    application.run_polling()