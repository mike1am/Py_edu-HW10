from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler,\
        MessageHandler, Filters, CallbackQueryHandler

from base import saveConv, loadConv, clearConv
from .model import getContactList, addContact, edContact, delContacts

(
    MENU_INPUT_STATE,
    NAME_INPUT_STATE,
    PHONE_INPUT_STATE,
    CONF_KB_STATE,
) = range(4)

MENU_ITEMS = {
    1: "Добавить контакт",
    2: "Удалить контакты",
    3: "Редактировать контакт",
    4: "Просмотр контактов",
    0: "Выход"
}


def initPhonebookConversation(dispatcher) -> None:
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('phonebook', phonebookCommand)],
        states={
            MENU_INPUT_STATE: [MessageHandler(Filters.text, menuHandler)],
            NAME_INPUT_STATE: [MessageHandler(Filters.text, nameHandler)],
            PHONE_INPUT_STATE: [MessageHandler(Filters.text, phoneHandler)],
            CONF_KB_STATE: [CallbackQueryHandler(confKbHandler)],
        },
        fallbacks=[],
    ))


def menuOut(update: Update):
    keyboard = [[MENU_ITEMS[i]] for i in MENU_ITEMS.keys()]
    replayMarkup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    if hasattr(update.message, 'reply_text'):
        update.message.reply_text("Выберите действие", reply_markup=replayMarkup)
    else:
        # update.callback_query.edit_message_text("Выберите действие", reply_markup=replayMarkup)
        update.callback_query.edit_message_text("Введите что-нибудь")
        


def phonebookCommand(update: Update, context: CallbackContext) -> int:
    convData = {
        'oper': "",
        'name': "",
        'phone': "",
        'contacts': [] # временный список контактов для вывода и запоминания индексов
    }
    
    menuOut(update)
    saveConv(convData, update.effective_user.id)
    return MENU_INPUT_STATE


def menuHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    
    operNum = list(MENU_ITEMS.keys())[
        list(MENU_ITEMS.values()).index(update.message.text)
    ]
    convData['oper'] = operNum
    
    saveConv(convData, update.effective_user.id)
    
    match operNum:
        case 0: # выход
            clearConv(update.effective_user.id)
            update.message.reply_text("Вы вышли из телефонного справочника")
            return ConversationHandler.END
        case 1:
            update.message.reply_text("Введите имя контакта")
            return NAME_INPUT_STATE
        case 2:
            update.message.reply_text("Введите имя контакта")
            return NAME_INPUT_STATE
        case 3:
            update.message.reply_text("Введите имя контакта")
            return NAME_INPUT_STATE
        case 4:
            update.message.reply_text("Введите имя контакта. all - все")
            return NAME_INPUT_STATE


def nameHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    convData['name'] = update.message.text
    
    match convData['oper']:
        case 1: # добавление
            if getContactList(convData['name'], update.effective_user.id):
                update.message.reply_text(
                    "Такой контакт уже существует. Используйте пункт редактирования контакта"
                )    
                menuOut(update)
                return MENU_INPUT_STATE
            else:
                update.message.reply_text("Введите телефон контакта")
            
                saveConv(convData, update.effective_user.id)
                return PHONE_INPUT_STATE
        
        case 2: # удаление
            update.message.reply_text("Найдены контакты:")
            convData['contacts'] = getContactList(
                convData['name'],
                update.effective_user.id
            )
            showContacts(convData['contacts'], update)

            if convData['contacts']: # если найдены контакты для удаления
                replyMarkup = InlineKeyboardMarkup([[
                    InlineKeyboardButton("Да", callback_data='Y'),
                    InlineKeyboardButton("Отмена", callback_data='N'),
                ]])
                update.message.reply_text(
                    "Вы действительно хотите удалить эти контакты?",
                    reply_markup=replyMarkup
                )
                saveConv(convData, update.effective_user.id)
                return CONF_KB_STATE
            else:
                menuOut(update)
                return MENU_INPUT_STATE
        
        case 3: # редактирование
            if not convData['contacts']: # первый прогон
                update.message.reply_text("Редактирование контакта:")
                convData['contacts'] = getContactList(
                    convData['name'],
                    update.effective_user.id
                )[:1] # берётся только первый контакт, если совпадений по имени было несколько
                showContacts(convData['contacts'], update)
                
                if convData['contacts']: # если найден контакт для редактирования
                    update.message.reply_text(
                        "Введите новое имя контакта. = - оставить прежним"
                    )
                    saveConv(convData, update.effective_user.id)
                    return NAME_INPUT_STATE
                else:
                    menuOut(update)
                    return MENU_INPUT_STATE
            else: # второй прогон
                if convData['name'] == "=": # если "=", то имя берётся из данных контакта
                    convData['name'] = convData['contacts'][0]['name']
                update.message.reply_text(
                    "Введите новый телефон контакта. = - оставить прежним"
                )
                saveConv(convData, update.effective_user.id)
                return PHONE_INPUT_STATE
        
        case 4: # просмотр
            if convData['name'].lower() == "all":
                convData['name'] = ""
            showContacts(
                getContactList(convData['name'], update.effective_user.id),
                update
            )
            menuOut(update)
            return MENU_INPUT_STATE
    
    
def phoneHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    convData['phone'] = update.message.text

    match convData['oper']:
        case 1: # добавление
            addContact(
                convData['name'],
                convData['phone'],
                update.effective_user.id
            )
            menuOut(update)
            return MENU_INPUT_STATE
        
        case 3: # редактирование
            if convData['phone'] == "=": # если "=", то тел. берётся из данных контакта
                convData['phone'] = convData['contacts'][0]['phone']
            
            edContact(
                convData['contacts'][0],
                convData['name'],
                convData['phone'],
                update.effective_user.id
            )
            convData['contacts'] = [] # для корректной работы след. опер. редактирования контакта

            menuOut(update)
            saveConv(convData, update.effective_user.id)
            return MENU_INPUT_STATE

        
def confKbHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    
    query = update.callback_query
    query.answer()

    # удаление
    if query.data == "Y":
        delContacts(convData['contacts'], update.effective_user.id)

    convData['contacts'] = []

    menuOut(update)
    saveConv(convData, update.effective_user.id)
    return MENU_INPUT_STATE


def showContacts(contactList, update: Update):
    outStr = ""
    for contact in contactList:
        outStr += f"\nИмя: {contact['name']}" + \
                f"\nТелефон: {contact['phone']}\n"
    if not outStr:
        outStr = "Контакты не найдены"
    else: outStr = "Найдены контакты:\n" + outStr
    if hasattr(update.message, 'reply_text'):
        update.message.reply_text(outStr)
    else:
        update.callback_query.edit_message_text(outStr)
