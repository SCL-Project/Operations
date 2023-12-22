import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
import csv

registered_users = set()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token from BotFather
TOKEN = '6706420741:AAEe9m9FoVZHSNiENuSKO2NHylCCoo9aL1A'

# Group Chat ID of the Onboarding Taskforce
TASKFORCE_CHAT_ID = -1001998746458

# CSV file path for storing user data
CSV_FILE = 'onboarding_data.csv'

# File paths
SCHEDULE_PATH = 'SCL.png'
BROCHURE_PATH = 'OnboardingDates.pdf'

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
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(SCHEDULE_PATH, 'rb'))

async def send_brochure(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await context.bot.send_document(chat_id=query.message.chat_id, document=open(BROCHURE_PATH, 'rb'))

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    message_text = update.message.text

    # Check if user is already registered
    if user.id in registered_users:
        # Forward the message to the TASKFORCE_CHAT_ID
        await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID, 
                                       text=f"Question from {user.first_name} {user.last_name} (ID: {user.id}):\n\n{message_text}")
        logger.info(f"Forwarded a message from already registered user {user.id}: {message_text}")
    else:
        # Register new user and handle the onboarding process
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user.id, user.first_name, user.last_name, message_text])
        
        keyboard = [[InlineKeyboardButton("Confirm", callback_data=f'confirm_{user.id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=TASKFORCE_CHAT_ID, 
                                       text=f"New joiner details:\n\n{message_text}\n\nConfirm the user?", 
                                       reply_markup=reply_markup)
        
        # Add user to the set of registered users
        registered_users.add(user.id)

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
    await query.answer()

    user_id = query.data.split('_')[1]
    bot = context.bot
    await bot.send_message(chat_id=user_id,
                           text="Hi again,\n\nYou can now use this chat.\nWe will send you all the information on a later date.\n"
                                "If you have any questions, do not hesitate to write them here and we will get back to you.\n\n"
                                "Best regards,\nThe Onboarding Team")

async def broadcast_to_users(update: Update, context: CallbackContext):
    # Ensure that this command is used in the TASKFORCE_CHAT_ID only
    if update.message.chat_id != TASKFORCE_CHAT_ID:
        return

    try:
        message_to_broadcast = ' '.join(context.args)  # The message to broadcast
        if not message_to_broadcast:
            raise ValueError("No message provided.")

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
