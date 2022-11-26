from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler,\
        MessageHandler, Filters, CallbackQueryHandler

from candies.model import setTotalCandies, setMaxDecr, getTotalCandies, getMaxDecr,\
        botTurn, playerTurn

(
    TOTAL_CANDIES_STATE,
    MAX_DECR_STATE,
    FIRST_TURN_STATE,
    PLAYER_TURN_STATE
) = range(4)


def initCandiesConversation (dispatcher) -> None:
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('candies', candiesCommand)],
        states={
            TOTAL_CANDIES_STATE: [MessageHandler(Filters.text, inputTotalCandiesHandler)],
            MAX_DECR_STATE: [MessageHandler(Filters.text, inputMaxDecrHandler)],
            FIRST_TURN_STATE: [CallbackQueryHandler(kbFirstTurnHandler)],
            PLAYER_TURN_STATE: [MessageHandler(Filters.text, playerTurnHandler)],
        },
        fallbacks=[],
    ))


def candiesCommand(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Игра в конфеты" +
            "\nВведите начальное количество конфет:")
    return TOTAL_CANDIES_STATE


def inputTotalCandiesHandler(update: Update, context: CallbackContext) -> int:
    userInput = update.message.text
    
    if not userInput.isdigit() or int(userInput) <= 0:
        update.message.reply_text("Вы должны ввести натуральное число." +
            "\nВведите начальное количество конфет:")
        return TOTAL_CANDIES_STATE
    
    setTotalCandies(int(userInput))
    
    update.message.reply_text("Введите, сколько можно максимально брать конфет:")
    return MAX_DECR_STATE


def inputMaxDecrHandler(update: Update, context: CallbackContext) -> int:
    userInput = update.message.text
    
    if not userInput.isdigit() or int(userInput) <= 0:
        update.message.reply_text("Вы должны ввести натуральное число." +
            "\nВведите, сколько можно максимально брать конфет:")
        return MAX_DECR_STATE
        
    if int(userInput) > getTotalCandies():
        update.message.reply_text("Число не должно превышать начальное количество конфет." +
            "\nВведите, сколько можно максимально брать конфет:")
        return MAX_DECR_STATE
    else: setMaxDecr(int(userInput))

    replyMarkup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Я, бот", callback_data='bot'),
            InlineKeyboardButton("Вы, игрок", callback_data='player')]]
    )
    
    update.message.reply_text("Кто будет брать первым?", reply_markup=replyMarkup)
    return FIRST_TURN_STATE


def kbFirstTurnHandler(update: Update, context: CallbackContext) -> int:
    messageText = ("Начинаем игру")

    query = update.callback_query
    query.answer()

    if query.data == 'bot':
        botAnswer = botTurnOutput()
        messageText += "\n" + botAnswer[1]
        
        if botAnswer[0]:
            query.edit_message_text(messageText)
            return ConversationHandler.END

    messageText += "\n\nСколько берёте конфет?"
    query.edit_message_text(messageText)

    return PLAYER_TURN_STATE


def playerTurnHandler(update: Update, context: CallbackContext) -> int:
    userInput = update.message.text
    
    if not userInput.isdigit() or int(userInput) <= 0:
        update.message.reply_text("Вы должны ввести натуральное число." +
            "\nСколько берёте конфет?")
        return PLAYER_TURN_STATE
    
    decr = int(userInput)
    if decr > getMaxDecr() or decr > getTotalCandies():
        update.message.reply_text("Так много конфет взять нельзя." +
            "\nСколько берёте конфет?")
        return PLAYER_TURN_STATE
    
    playerTurn(decr)

    if not getTotalCandies():
        update.message.reply_text("Игра закончена. Вы выиграли. Поздравляю!")
        return ConversationHandler.END
        
    botAnswer = botTurnOutput()
    messageText = botAnswer[1]

    if botAnswer[0]:
        update.message.reply_text(messageText)
        return ConversationHandler.END

    messageText += "\n\nСколько берёте конфет?"
    update.message.reply_text(messageText)

    return PLAYER_TURN_STATE


# Возвращает картеж: (признак завершения игры, сообщение для вывода)
def botTurnOutput():
    decr = botTurn()
    
    if not getTotalCandies():
        return (True, f"Я взял {decr} конфет\nИгра закончена. Вы проиграли.")
    else:
        return (False, f"Я взял {decr} конфет\nОсталось {getTotalCandies()}")
