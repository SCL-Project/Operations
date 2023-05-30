import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
import requests
import logging
from config import BOT_TOKEN, ELASTIC_API_KEY, STRATO_EMAIL_ADDRESS

# Load templates
def load_templates(context):
    templates = {}
    for filename in os.listdir('templates'):
        with open(os.path.join('templates', filename), 'r') as file:
            templates[filename] = file.read()
    context.bot_data['templates'] = templates

# Mail command handler
def mail(update: Update, context: CallbackContext):
    load_templates(context)
    templates = context.bot_data['templates']
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(template, callback_data=f'template_{template}') for template in templates]
    ])
    update.message.reply_text('Choose a template:', reply_markup=reply_markup)


def template_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    template_name = query.data.split('_')[1]
    context.user_data['template_name'] = template_name
    query.answer()
    query.edit_message_text(f"Selected template: {template_name}\n\nPlease enter the required information separated by commas: [name, date]")
    context.user_data['state'] = 'info'

def process_message(update: Update, context: CallbackContext):
    state = context.user_data.get('state')

    if state == 'info':
        info_received(update, context)
    elif state == 'email':
        email_received(update, context)

def info_received(update: Update, context: CallbackContext):
    info = update.message.text.split(',')
    if len(info) != 2:
        update.message.reply_text('Please enter exactly two values separated by a comma: [name, date]')
        return
    context.user_data['info'] = info
    update.message.reply_text("Please enter the receiver's email address:")
    context.user_data['state'] = 'email'

def email_received(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    context.user_data['state'] = 'preview'

    if 'info' not in context.user_data:
        update.message.reply_text('Please enter the required information separated by commas: [name, date]')
        context.user_data['state'] = 'info'
        return

    # Access 'name' and 'date' from the 'info' key in the user_data dictionary
    name, date = context.user_data['info']
    
    email_body = context.bot_data['templates'][context.user_data['template_name']].format(name=name, date=date)
    preview = f"Subject: {context.user_data['template_name']}\n\n{email_body}\n\nTo: {email}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('Send', callback_data='send_email')],
        [InlineKeyboardButton('Scrap', callback_data='scrap_email')]
    ])

    update.message.reply_text(preview, reply_markup=reply_markup)
    update.message.reply_text(preview, reply_markup=reply_markup)

def send_email(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    subject = context.user_data['template_name']
    name, date = context.user_data['info']
    email_body = context.bot_data['templates'][context.user_data['template_name']].format(name=name, date=date)
    to_email = context.user_data['email']
    
    data = {
        "apikey": ELASTIC_API_KEY,
        "from": STRATO_EMAIL_ADDRESS,
        "to": to_email,
        "subject": subject,
        "bodyHtml": email_body
    }

    response = requests.post("https://api.elasticemail.com/v2/email/send", data=data)
    logger.info(f'Elastic Email API response: {response.text}')  # Log the API response

    if response.status_code == 200:
        query.edit_message_text('Email sent successfully!')
    else:
        query.edit_message_text(f'Error sending email: {response.text}')

def scrap_email(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Email scrapped!')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    context = updater.dispatcher

    # Load templates
    load_templates(context)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler('mail', mail))
    dp.add_handler(CallbackQueryHandler(template_selected, pattern='^template_'))
    dp.add_handler(CallbackQueryHandler(send_email, pattern='^send_email$'))
    dp.add_handler(CallbackQueryHandler(scrap_email, pattern='^scrap_email$'))

    # Register message handlers
    dp.add_handler(MessageHandler(None, process_message))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM, or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
