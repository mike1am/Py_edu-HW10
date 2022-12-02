from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler,\
        MessageHandler, Filters, CallbackQueryHandler

from base import saveConv, loadConv, clearConv
from .model import getContactList, addContact, edContact, delContacts
from .ui_view import menuOut, showContacts

(
    MENU_INPUT_STATE,
    NAME_INPUT_STATE,
    PHONE_INPUT_STATE,
    CONV_KB_STATE,
) = range(4)


def initPhonebookConversation(dispatcher) -> None:
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('phonebook', phonebookCommand)],
        states={
            MENU_INPUT_STATE: [CallbackQueryHandler(menuHandler)],
            NAME_INPUT_STATE: [MessageHandler(Filters.text, nameHandler)],
            PHONE_INPUT_STATE: [MessageHandler(Filters.regex(
                r"^(8|(\+\d{1,4})[ ]?)?(\(\d{1,5}\))?([\- ]\d+)+$"
            ), phoneHandler)],
            CONV_KB_STATE: [CallbackQueryHandler(convKbHandler)],
        },
        fallbacks=[],
    ))
        

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
    
    query = update.callback_query
    query.answer()

    convData['oper'] = query.data
    
    saveConv(convData, update.effective_user.id)
    
    match convData['oper']:
        case 'end':
            clearConv(update.effective_user.id)
            query.message.reply_text("Вы вышли из телефонного справочника")
            return ConversationHandler.END
        case 'add' | 'del' | 'ed':
            query.message.reply_text("Введите имя контакта")
            return NAME_INPUT_STATE
        case 'show':
            replayMarkup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Все контакты", callback_data=1)],
                [InlineKeyboardButton("Выбор по имени", callback_data=0)],
            ])
            query.message.reply_text("Выберите:", reply_markup=replayMarkup)
            return CONV_KB_STATE


def nameHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    convData['name'] = update.message.text
    
    match convData['oper']:
        case 'add':
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
        
        case 'del':
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
                return CONV_KB_STATE
            
            else:
                menuOut(update)
                return MENU_INPUT_STATE
        
        case 'ed':
            # первый прогон (поиск контакта для редактирования)
            if not convData['contacts']:
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
            
            # второй прогон (обработка нового имени)
            else:
                if convData['name'] == "=": # если "=", то имя берётся из данных контакта
                    convData['name'] = convData['contacts'][0]['name']
                update.message.reply_text(
                    "Введите новый телефон контакта. = - оставить прежним"
                )
                saveConv(convData, update.effective_user.id)
                return PHONE_INPUT_STATE
        
        case 'show':
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
        case 'add':
            addContact(
                convData['name'],
                convData['phone'],
                update.effective_user.id
            )
            menuOut(update)
            return MENU_INPUT_STATE
        
        case 'ed':
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

        
def convKbHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    
    query = update.callback_query
    query.answer()

    match convData['oper']:
        case 'del':
            if query.data == "Y":
                delContacts(convData['contacts'], update.effective_user.id)

            convData['contacts'] = [] # для корректной работы след. опер. редактирования контакта

            menuOut(update)
            saveConv(convData, update.effective_user.id)
            return MENU_INPUT_STATE

        case 'show':
            if int(query.data):
                showContacts(
                    getContactList("", update.effective_user.id), # вывод всех контактов
                    update
                )   
                menuOut(update)
                return MENU_INPUT_STATE
            else:
                query.message.reply_text("Введите имя контакта")
                return NAME_INPUT_STATE
