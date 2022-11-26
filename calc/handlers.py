import pickle
import os.path

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler,\
        MessageHandler, Filters, CallbackQueryHandler

(
    num_TYPE_SEL_STATE,
    OP_BUTTON_STATE,
    NUM_A_STATE,
    NUM_B_STATE,
) = range(4)


def loadData(sessionId):
    fName = f"{sessionId}.pickle"
    
    if not os.path.exists(fName):
        return None

    with open(fName, 'rb') as f:
        return pickle.load(f)
    

def saveData(data, sessionId):
    with open(f"{sessionId}.pickle", "wb") as f:
        pickle.dump(data, f)


def initCalcConversation(dispatcher) -> None:
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('calc', calcCommand)],
        states={
            num_TYPE_SEL_STATE: [MessageHandler(Filters.regex(r"I|R|C"), num_typeSelectHandler)],
            OP_BUTTON_STATE: [CallbackQueryHandler(opSelectHandler)],
            NUM_A_STATE: [MessageHandler(Filters.regex(r"^-?[0-9]*.?[0-9]+([+-]?[0-9]*.?[0-9]+j)?$"), inputNumAHandler)],
            NUM_B_STATE: [MessageHandler(Filters.regex(r"^-?[0-9]*.?[0-9]+([+-]?[0-9]*.?[0-9]+j)?$"), inputNumBHandler)],
        },
        fallbacks=[],
    ))


def calcCommand(update: Update, context: CallbackContext) -> int:
    data = loadData(update.effective_user.id)
    if not data:
        data = {
            'userName': update.effective_user.username,
            'num_a': 0,
            'num_b': 0,
            'op': "",
            'num_type': int,
        }
    
    kb = [
        ["Операции с I числами"],
        ["Операции с R числами"],
        ["Операции с C числами"],
    ]
    
    replayMarkup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    update.message.reply_text("Выберите действие", reply_markup=replayMarkup)

    saveData(data, update.effective_user.id)
    return num_TYPE_SEL_STATE


def num_typeSelectHandler(update: Update, context: CallbackContext) -> int:
    data = loadData(update.effective_user.id)

    if "I" in update.message.text:
        data['num_type'] = int
    elif "R" in update.message.text:
        data['num_type'] = float
    else: 
        data['num_type'] = complex
    
    replyMarkup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("a + b", callback_data='+'),
            InlineKeyboardButton("a - b", callback_data='-')]]
    )
    
    update.message.reply_text("Выберите действие:", reply_markup=replyMarkup)

    saveData(data, update.effective_user.id)
    return OP_BUTTON_STATE


def opSelectHandler(update: Update, context: CallbackContext) -> int:
    data = loadData(update.effective_user.id)
    
    query = update.callback_query
    query.answer()

    data['op'] = query.data

    query.edit_message_text("Введите число А")

    saveData(data, update.effective_user.id)
    return NUM_A_STATE


def inputNumAHandler(update: Update, context: CallbackContext) -> int:
    data = loadData(update.effective_user.id)

    data['num_a'] = update.message.text

    update.message.reply_text("Введите число B")

    saveData(data, update.effective_user.id)
    return NUM_B_STATE


def inputNumBHandler(update: Update, context: CallbackContext) -> int:
    data = loadData(update.effective_user.id)

    data['num_b'] = update.message.text

    try:
        res = exec(data)
    except ValueError:
        update.message.reply_text("Неверный тип чисел.\nВведите число А")
        return NUM_A_STATE

    update.message.reply_text(f"Результат: {res}")
    
    saveData(data, update.effective_user.id)
    return ConversationHandler.END

def exec(data):
    numA = data['num_type'](data['num_a'])
    numB = data['num_type'](data['num_b'])

    return eval(f"{numA} {data['op']} {numB}")