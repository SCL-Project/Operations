import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
import requests
import logging
import re
import html2text
from config import BOT_TOKEN, ELASTIC_API_KEY, STRATO_EMAIL_ADDRESS


def load_templates(context):
    templates = {}
    for filename in os.listdir('templates'):
        with open(os.path.join('templates', filename), 'r') as file:
            content = file.read()
            title = re.search(r'{Title:(.+)}', content).group(1).strip()
            content = re.sub(r'{Title:.*}', '', content)  # Add this line
            templates[filename] = {'content': content, 'title': title}
    context.bot_data['templates'] = templates


def mail(update: Update, context: CallbackContext):
    templates_dir = 'templates'
    templates = [f for f in os.listdir(templates_dir) if f.endswith('.txt')]
    if not templates:
        return update.message.reply_text('No templates found.')
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
        context.bot_data['templates'][t]['title'], callback_data=f'template_{t}') for t in templates]])
    update.message.reply_text('Choose a template:', reply_markup=reply_markup)


def template_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    template_name = query.data.split('_')[1]
    context.user_data['template_name'] = template_name
    query.answer()
    missing_vars = re.findall(
        r'{(\w+)}', context.bot_data['templates'][template_name]['content'])
    context.user_data['missing_vars'] = missing_vars
    query.edit_message_text(
        f"Selected template: {context.bot_data['templates'][template_name]['title']}\n\nPlease enter the required information separated by commas: {', '.join(missing_vars)}")
    context.user_data['state'] = 'info'


def process_message(update: Update, context: CallbackContext):
    state = context.user_data.get('state')
    if state == 'info':
        info_received(update, context)
    elif state == 'email':
        email_received(update, context)


def info_received(update: Update, context: CallbackContext):
    info = update.message.text.split(',')
    if len(info) != len(context.user_data['missing_vars']):
        update.message.reply_text(
            f'Please enter exactly {len(context.user_data["missing_vars"])} values separated by a comma: {", ".join(context.user_data["missing_vars"])}')
        return
    context.user_data['info'] = dict(
        zip(context.user_data['missing_vars'], info))
    update.message.reply_text("Please enter the receiver's email address:")
    context.user_data['state'] = 'email'


def email_received(update: Update, context: CallbackContext):
    email = update.message.text
    context.user_data['email'] = email
    context.user_data['state'] = 'preview'
    if 'info' not in context.user_data:
        update.message.reply_text(
            'Please enter the required information separated by commas: [name, date]')
        context.user_data['state'] = 'info'
        return
    template_name = context.user_data['template_name']
    template = context.bot_data['templates'][template_name]
    email_body = template['content']
    for var, value in context.user_data['info'].items():
        email_body = email_body.replace(f"{{{var}}}", value)
    email_body = f"<!DOCTYPE html><html><body>{email_body}</body></html>"
    text_body = html2text.html2text(email_body)
    text_body = re.sub(r'\|\s+!\[image description\]\(https://i.imgur.com/nTgZcwa.png\)', '', text_body)  # Add this line
    text_body = re.sub(r'---', '', text_body)  # Add this line
    text_body = re.sub(r'# Smart Contracts Lab', '', text_body)  # Add this line
    text_body = re.sub(r'\(C\) 2023 Smart Contracts Lab', '', text_body)
    preview = f"Subject: {template['title']}\n\n{text_body.strip()}\n\nTo: {email}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Send', callback_data='send_email')], [
                                        InlineKeyboardButton('Scrap', callback_data='scrap_email')]])
    update.message.reply_text(preview, reply_markup=reply_markup)
    
def send_email(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    subject = context.bot_data['templates'][context.user_data['template_name']]['title']
    email_body = context.bot_data['templates'][context.user_data['template_name']]['content']
    for var, value in context.user_data['info'].items():
        email_body = email_body.replace(f"{{{var}}}", value)
    to_email = context.user_data['email']
    data = {"apikey": ELASTIC_API_KEY, "from": STRATO_EMAIL_ADDRESS, "to": to_email,
            "subject": subject, "bodyHtml": email_body, "isTransactional": "true"}
    response = requests.post(
        "https://api.elasticemail.com/v2/email/send", data=data)
    logging.info(f'Elastic Email API response: {response.text}')
    if response.status_code == 200:
        query.edit_message_text('Email sent successfully!')
    else:
        query.edit_message_text(f'Error sending email: {response.text}')


def scrap_email(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Email scrapped!')


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    context = updater.dispatcher
    load_templates(context)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('mail', mail))
    dp.add_handler(CallbackQueryHandler(
        template_selected, pattern='^template_'))
    dp.add_handler(CallbackQueryHandler(send_email, pattern='^send_email$'))
    dp.add_handler(CallbackQueryHandler(scrap_email, pattern='^scrap_email$'))
    dp.add_handler(MessageHandler(None, process_message))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
