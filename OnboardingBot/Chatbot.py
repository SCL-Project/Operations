import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
import csv

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token from BotFather
TOKEN = '6706420741:AAEe9m9FoVZHSNiENuSKO2NHylCCoo9aL1A'

# Group Chat ID of the Onboarding Taskforce
TASKFORCE_CHAT_ID = -1001998746458

# CSV file path for storing user data
CSV_FILE = 'OnboardingBot/confirmed_users.csv'

# File paths
SCHEDULE_PATH = 'OnboardingBot/Schedule.png'
BROCHURE_PATH = 'OnboardingBot/Welcome Brochure.pdf'

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Get Onboarding Schedule", callback_data="get_schedule")],
        [InlineKeyboardButton("Get Welcome Brochure", callback_data="get_brochure")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello and Welcome to Smart Contracts Lab Onboarding Bot,\n\n"
        "This bot is here to help you with your Onboarding process.\n"
        "Before we can start please input your Name, Surname, UZH Email address, matriculation number. "
        "You will get another message when this Chat is ready to use.\n\n"
        "You can also get the Onboarding Schedule and Welcome Brochure below.\n\n"
        "Thank you.\n\nBest regards,\nThe Onboarding Team",
        reply_markup=reply_markup
    )

async def send_schedule(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    with open(SCHEDULE_PATH, 'rb') as file:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=file)

async def send_brochure(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    with open(BROCHURE_PATH, 'rb') as file:
        await context.bot.send_document(chat_id=query.message.chat_id, document=file)

def load_registered_users(csv_file_path):
    registered_users = set()
    try:
        with open(csv_file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                registered_users.add(int(row[0]))
    except FileNotFoundError:
        # File not found, meaning no users are registered yet.
        pass
    return registered_users

def register_user(user_id, user_first_name, user_last_name, csv_file_path):
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, user_first_name, user.last_name])

def store_user_message(user_id, message_text, text_file_path):
    with open(text_file_path, mode='a') as file:
        file.write(f"{user_id}: {message_text}\n")

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    message_text = update.message.text
    registered_users = load_registered_users(CSV_FILE)  # Reload the registered users each time

    # Check if user is already registered
    if user.id not in registered_users:
        # Register new user
        register_user(user.id, user.first_name, user.last_name, CSV_FILE)
        
        # Notify the TASKFORCE_CHAT_ID about the new user
        keyboard = [[InlineKeyboardButton("Confirm", callback_data=f'confirm_{user.id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID, 
                                       text=f"New joiner details:\n\n{message_text}\n\nConfirm the user?", 
                                       reply_markup=reply_markup)

        # Log the new registration
        logger.info(f"Registered a new user {user.id}: {message_text}")
        
        # Send a message to the user that they will be confirmed shortly
        await context.bot.send_message(chat_id=user.id, text="Your registration is being processed. You will be confirmed shortly.")
    else:
        # Append the message to the 'onboarding_data' text file
        store_user_message(user.id, message_text, 'OnboardingBot/onboarding_data.txt')
        
        # Send a message to the user that they are already registered
        await context.bot.send_message(chat_id=user.id, text="You are already registered. But you can ask me anything!")
        
        # Forward the message to the TASKFORCE_CHAT_ID
        await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID, 
                                       text=f"Question from {user.first_name} {user.last_name} (ID: {user.id}):\n\n{message_text}")
        logger.info(f"Forwarded a message from already registered user {user.id}: {message_text}")

async def reply_to_user(update: Update, context: CallbackContext):
    # Ensure that this command is used in the TASKFORCE_CHAT_ID only
    if update.message.chat_id != TASKFORCE_CHAT_ID:
        return

    try:
        args = context.args  # Extract arguments passed with the command
        if len(args) < 2:
            raise ValueError("Insufficient arguments.")

        user_id = int(args[0])  # The first argument is the user ID
        message_to_send = ' '.join(args[1:])  # The rest is the message

        await context.bot.send_message(chat_id=user_id, text=message_to_send)
        await update.message.reply_text(f"Message sent to user {user_id}")
    except (IndexError, ValueError, TypeError) as e:
        await update.message.reply_text("Usage: /reply USER_ID MESSAGE")

async def confirm_user(update: Update, context: CallbackContext):
    query = update.callback_query

    if query is None:
        logger.error("Callback query is None")
        return

    logger.info("Answering query")
    await query.answer()
    logger.info("Query answered")

    try:
        user_id = int(query.data.split('_')[1])
        confirmation_message = "Hi again,\n\nYou are now confirmed and can use this chat..."

        logger.info(f"Sending confirmation message to {user_id}")
        await context.bot.send_message(chat_id=user_id, text=confirmation_message)
        logger.info("Confirmation message sent")

    except Exception as e:
        logger.error(f"Error in confirm_user: {e}")
        await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID, text=f"Failed to confirm user {user_id}. Error: {e}")

async def broadcast_to_users(update: Update, context: CallbackContext):
    if update.message.chat_id != TASKFORCE_CHAT_ID:
        return

    try:
        message_to_broadcast = ' '.join(context.args)
        if not message_to_broadcast:
            raise ValueError("No message provided.")

        # Load the registered users from the CSV file
        registered_users = load_registered_users(CSV_FILE)
        
        # Send the broadcast message to each registered user
        for user_id in registered_users:
            await context.bot.send_message(chat_id=user_id, text=message_to_broadcast)

        await update.message.reply_text(f"Broadcast message sent to {len(registered_users)} users.")
    except ValueError as e:
        await update.message.reply_text("Usage: /broadcast MESSAGE")


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    confirm_handler = CallbackQueryHandler(confirm_user, pattern='^confirm_')
    schedule_handler = CallbackQueryHandler(send_schedule, pattern='^get_schedule$')
    brochure_handler = CallbackQueryHandler(send_brochure, pattern='^get_brochure$')
    reply_handler = CommandHandler("reply", reply_to_user, filters.Chat(chat_id=TASKFORCE_CHAT_ID))
    broadcast_handler = CommandHandler("broadcast", broadcast_to_users, filters.Chat(chat_id=TASKFORCE_CHAT_ID))
    confirm_handler = CallbackQueryHandler(confirm_user, pattern='^confirm_')
    
    application.add_handler(confirm_handler)
    application.add_handler(broadcast_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(confirm_handler)
    application.add_handler(schedule_handler)
    application.add_handler(brochure_handler)
    application.add_handler(reply_handler)
    application.add_error_handler(error)


    application.run_polling()

if __name__ == '__main__':
    registered_users = load_registered_users(CSV_FILE)
    main()