# Onboarding Bot to communicate with the New Students during their Integration to SCL

This Telegram bot is designed to facilitate the onboarding process for new members of the Smart Contracts Lab. It provides new joiners with essential resources and collects their details for registration purposes.
The bot increases the efficiency and automatization of the operational process of introducing new students to the project.

## Features

- **Welcome Message**: After users press the start button the bot sends a greeting message to new users with buttons to download important documents.
- **Resource Distribution**: Allows users to download the important documents such as the onboarding schedule and welcome brochure directly from the chat.
- **User Registration**: Collects user details and stores them in a CSV file for confirmation by the task force team.
- **User Confirmation**: Enables the task force team to confirm new users after reviewing their submitted details.
- **Message Forwarding**: Forwards messages from users to the group chat of the onboarding task force for direct communication and support
- **Reply Messages**: The onboarding task force can directly reply to users with a reply button via the task force group chat (/reply USER_ID MESSAGE)
- **Broadcast Messages**: Supports broadcasting messages via a button to all registered users (/broadcast MESSAGE)

## Setup

1. **Clone the repository**:
Via GitHub Desktop or
*git clone <https://github.com/SCL-Project/Operations/tree/main/OnboardingBot>*

2. **Install dependencies**:
Ensure you have Python 3.8 or newer installed. Then, install the required packages using pip:  
*pip install python-telegram-bot --upgrade*  

3. **Configuration**:
- Set the `TOKEN` variable in the script to the bot token you received from BotFather.
- Update the `TASKFORCE_CHAT_ID` with your task force group chat ID.
- Adjust the `CSV_FILE`, `SCHEDULE_PATH`, and `BROCHURE_PATH` variables as needed.

4. **Running the Bot**
Execute the script with Python:  
*python <Chatbot>.py*

5. **Commands**

- `/start`: Sends the welcome message with the onboarding resources.
- `/reply USER_ID MESSAGE`: Allows the task force to reply to a specific user's inquiry (task force group chat only).
- `/broadcast MESSAGE`: Sends a message to all registered users (task force group chat only).

## Development

Feel free to contribute or customize the bot to fit your organization's needs. For contributions, please submit a pull request.

## License

This project is licensed under the MIT License



