import pandas as pd
from datetime import datetime
import telegram
import asyncio

df = pd.read_excel('./Birthday.xlsx')

today = datetime.now().strftime('%m/%d')
bot = telegram.Bot(
    token='6243968294:AAFZXG_QIyJGQ-Zd7uGMkxH6t5AzHp7hkno')  # Bot Token


async def send_message(chat_ids, message):
    for chat_id in chat_ids:
        await bot.send_message(chat_id=chat_id, text=message)


async def main():
    chat_ids = ['1941405353', '6116706465']  # Add Chat ID's here

    for i, row in df.iterrows():
        if pd.notna(row['First Name']) and pd.notna(row['Last Name']) and pd.notna(row['Birthday']):
            birthday = row['Birthday'].strftime('%m/%d')
            if birthday == today:
                # Message
                message = f"Today is {row['First Name']} {row['Last Name']}'s birthday!🎉 ({row['Status']}) "
                await send_message(chat_ids, message=message)

if __name__ == '__main__':
    asyncio.run(main())
