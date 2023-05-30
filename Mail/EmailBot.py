import imaplib
import email
import telegram
import os
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from datetime import datetime, timedelta
import asyncio
import pytz


def get_plain_text_message(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                charset = part.get_content_charset() or 'utf-8'
                return part.get_payload(decode=True).decode(charset, errors='replace')
    else:
        if message.get_content_type() == 'text/plain':
            charset = message.get_content_charset() or 'utf-8'
            return message.get_payload(decode=True).decode(charset, errors='replace')
    return None


async def main():
    # Get the local timezone
    # Replace "UTC" with your timezone string, e.g., "America/New_York"
    local_timezone = pytz.timezone("Europe/Zurich")

    # Calculate the date 1 hour ago
    date_1_hour_ago = datetime.now(local_timezone) - timedelta(hours=1)
    date_string = date_1_hour_ago.strftime("%d-%b-%Y")

    # Set up the Telegram bot using your bot token
    bot = telegram.Bot(token='6136690729:AAG786l2vsIw2FaeZOVwA7pNp4hxNA1aLbI')

    # Set up the IMAP connection to your email provider
    mail = imaplib.IMAP4_SSL('imap.strato.com', 993)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mail.select('inbox')

    # Search for messages in the inbox since 1 hour ago
    status, response = mail.search(None, f'SINCE "{date_string}"')

    if response == [b'']:
        mail.close()
        mail.logout()
        return

    # Loop through the messages and send them to the Telegram bot
    for num in response[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        message = email.message_from_bytes(data[0][1])
        email_date = email.utils.parsedate_to_datetime(message['Date'])
        timestamp = email_date.astimezone(local_timezone)

        # Extract plain text from the email message
        text = get_plain_text_message(message)

        # Only send the message if the email is younger than 1 hour
        if text and timestamp > date_1_hour_ago:
            sender = message['From']
            chat_id = '6116706465'  # 6116706465 -916281629
            message_text = f"NEW MAIL\n\nFrom: {sender}\n\n{text}"
            await bot.send_message(chat_id=chat_id, text=message_text)

    # Close the IMAP connection
    mail.close()
    mail.logout()

# Run the async function
asyncio.run(main())
