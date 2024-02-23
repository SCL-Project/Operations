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
CSV_FILE = 'confirmed_users.csv'

# File paths
SCHEDULE_PATH = 'Schedule.png'
BROCHURE_PATH = 'Welcome Brochure.pdf'

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Get Onboarding Schedule", callback_data="get_schedule")],
        [InlineKeyboardButton("Get Welcome Brochure", callback_data="get_brochure")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello and Welcome to Smart Contracts Lab Onboarding Bot,\n\n"
        "This bot is here to help you with your onboarding process.\n"
        "Before we can start please input your name, surname, UZH email address and matriculation number. "
        "You will get another message when this Chat is ready to use.\n\n"
        "Further informations will be provided when the onboarding week gets closer"
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

def load_registered_users(csv_file):
    user_ids = set()
    try:
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Check if row is not empty
                    user_id = row[0]  # Assuming the user ID is the first column
                    user_ids.add(int(user_id))
    except FileNotFoundError:
        logger.error(f"File not found: {csv_file}")
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")

    return list(user_ids)

def is_user_registered(user_id, csv_file):
    with open(csv_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == str(user_id):
                return True
    return False

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    if update.message.text:
        # Check if user is already registered
        if not is_user_registered(user.id, CSV_FILE):
            # New user: save user's message to CSV and notify the Taskforce for confirmation
            with open(CSV_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user.id, user.first_name, user.last_name, update.message.text])

            keyboard = [[InlineKeyboardButton("Confirm", callback_data=f'confirm_{user.id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID,
                                           text=f"New joiner details:\n\n{update.message.text}\n\nConfirm the user?",
                                           reply_markup=reply_markup)
        else:
            # Existing user: forward their message to the Taskforce
            await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID,
                                          text=f"Message from user {user.id} ({user.first_name} {user.last_name}):\n\n{update.message.text}")

async def confirm_user(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.data.split('_')[1]
    bot = context.bot
    await bot.send_message(chat_id=user_id,
                           text="Hi again,\n\nYou are successfully registered and you can now use this chat"
                                "\nWe will send you all the information on a later date.\n"
                                "If you have any questions, do not hesitate to write them here and we will get back to you.\n\n"
                                "Best regards,\nThe Onboarding Team")

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
    main()