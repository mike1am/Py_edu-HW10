# Define a few command handlers. These usually take the two arguments update and context
from telegram import Update
from telegram.ext import CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(f"Привет, {user.first_name}!\nСписок команд:" +
        "\n/candies - игра в конфеты" +
        "\n/calc - калькулятор"
    )
    