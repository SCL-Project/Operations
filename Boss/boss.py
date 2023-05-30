from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext
from sendmail5 import mail, template_selected, edit_selected, edit_subject, edit_mail, scrap_email, process_message, load_templates, send_email
from newmail import newmail, newmail_process_message, show_email_preview, newmail_send_email, newmail_scrap_email, newmail_edit_options, newmail_edit_subject, newmail_edit_recipient, newmail_info_received
from telegram import Update
from sent2 import sent, handle_summary, handle_search, handle_back_to_menu, handle_back_to_search, handle_search_subject, handle_search_email, handle_subject_input, handle_email_input, handle_search_query
from config import BOT_TOKEN, ELASTIC_API_KEY, STRATO_EMAIL_ADDRESS


def add_handlers(dp):
    load_templates(dp)

    # Sendmail5 handlers
    dp.add_handler(CommandHandler('mail', mail))
    dp.add_handler(CallbackQueryHandler(
        template_selected, pattern=r'^template_.*$'))
    dp.add_handler(CallbackQueryHandler(edit_selected, pattern='^edit$'))
    dp.add_handler(CallbackQueryHandler(
        edit_subject, pattern='^edit_subject$'))
    dp.add_handler(CallbackQueryHandler(edit_mail, pattern='^edit_mail$'))
    dp.add_handler(CallbackQueryHandler(scrap_email, pattern='^scrap_email$'))
    dp.add_handler(CallbackQueryHandler(send_email, pattern='^send_email$'))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command),
                   process_message), group=1)  # Group 1 for general message handling

    # Newmail handlers
    dp.add_handler(CommandHandler('newmail', newmail))
    # Group 2 for newmail specific message handling
    dp.add_handler(MessageHandler(Filters.text & (
        ~Filters.command), newmail_process_message), group=2)
    dp.add_handler(CommandHandler('preview', show_email_preview))
    dp.add_handler(CallbackQueryHandler(
        newmail_edit_options, pattern="^newmail_edit_options$"))
    dp.add_handler(CallbackQueryHandler(
        newmail_edit_subject, pattern="^newmail_edit_subject$"))
    dp.add_handler(CallbackQueryHandler(
        newmail_edit_recipient, pattern="^newmail_edit_recipient$"))
    dp.add_handler(CallbackQueryHandler(
        newmail_send_email, pattern='^newmail_send_email$'))
    dp.add_handler(CallbackQueryHandler(
        newmail_scrap_email, pattern="^newmail_scrap_email$"))

    # Add your handlers
    dp.add_handler(CommandHandler('sent', sent))
    dp.add_handler(CallbackQueryHandler(handle_summary, pattern='^summary_'))
    dp.add_handler(CallbackQueryHandler(handle_search, pattern='^search$'))
    dp.add_handler(CallbackQueryHandler(
        handle_search_subject, pattern='^search_subject$'))
    dp.add_handler(CallbackQueryHandler(
        handle_search_email, pattern='^search_email$'))
    dp.add_handler(MessageHandler(Filters.text & ~
                   Filters.command, handle_search_query))  # Redirect to handle_search_query when a text message arrives
    dp.add_handler(CallbackQueryHandler(
        handle_back_to_menu, pattern='^back_to_menu$'))
    dp.add_handler(CallbackQueryHandler(
        handle_back_to_search, pattern='^back_to_search$'))


def process_mail_message(update: Update, context: CallbackContext):
    # Get the user's message
    message = update.message.text

    # Get the user's current template
    template = context.chat_data.get('template')

    # Check if the user has missing variables
    missing_vars = context.chat_data.get('missing_vars')
    if missing_vars:
        # Split the message into values using commas
        values = [value.strip() for value in message.split(',')]

        # Check if the number of values matches the number of missing variables
        if len(values) != len(missing_vars):
            update.message.reply_text(
                f"Please provide exactly {len(missing_vars)} values separated by commas.")
            return

        # Create a dictionary of variable-value pairs
        variable_value_map = {var: value for var,
                              value in zip(missing_vars, values)}

        # Update the template with the provided values
        for var, value in variable_value_map.items():
            template = template.replace(f"{{{var}}}", value)

        # Update the chat data with the filled template and remove missing variables
        context.chat_data['template'] = template
        context.chat_data.pop('missing_vars')

        # Send a preview of the filled template to the user
        preview = f"Preview:\n\n{template}"
        update.message.reply_text(preview)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    add_handlers(dp)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
