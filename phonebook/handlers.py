from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler,\
        MessageHandler, Filters, CallbackQueryHandler

from base import *
from .model import getContactList, addContact, edContact, delContacts, importContList, PHONE_RE
from .ui_view import menuOut, showContacts
from .imp_exp import expContacts, getImpList

(
    MENU_INPUT_STATE,
    NAME_INPUT_STATE,
    PHONE_INPUT_STATE,
    CONV_KB_STATE,
    FILE_IMP_STATE,
    FILE_EXP_STATE
) = range(6)


def initPhonebookConversation(dispatcher) -> None:
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('phonebook', phonebookCommand)],
        states={
            MENU_INPUT_STATE: [CallbackQueryHandler(menuHandler)],
            NAME_INPUT_STATE: [MessageHandler(Filters.text, nameHandler)],
            PHONE_INPUT_STATE: [MessageHandler(Filters.regex(PHONE_RE), phoneHandler)],
            CONV_KB_STATE: [CallbackQueryHandler(convKbHandler)],
            FILE_IMP_STATE: [MessageHandler(Filters.document.category("text"), fileImpHandler)],
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

        case 'show' | 'exp':
            replayMarkup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Все контакты", callback_data=1)],
                [InlineKeyboardButton("Выбор по имени", callback_data=0)],
            ])
            query.message.reply_text("Выберите:", reply_markup=replayMarkup)
            return CONV_KB_STATE

        case 'imp':
            query.message.reply_text("Перетащите файл импорта в окно мессанджера")
            return FILE_IMP_STATE


def nameHandler(update: Update, context: CallbackContext) -> int:
    convData = loadConv(update.effective_user.id)
    convData['name'] = update.message.text
    
    match convData['oper']:
        case 'add':
            if getContactList(convData['name'], update.effective_user.id, strong=True):
                update.message.reply_text(
                    "Такой контакт уже существует.\nИспользуйте пункт редактирования контакта"
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
            showContacts(convData['contacts'], update) # просмотр контактов перед удалением. Если список пустой, showContacts выводит соотв. сообщение 

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

        case 'exp':
            convData['contacts'] = getContactList(
                convData['name'],
                update.effective_user.id
            )
            expContacts(convData['contacts'], update, context)

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
                convData['contacts'][0]['ind'],
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

        case 'exp':
            if int(query.data):
                expContacts(
                    getContactList("", update.effective_user.id), # экспорт всех контактов
                    update,
                    context
                )   
                menuOut(update)
                return MENU_INPUT_STATE
            else:
                query.message.reply_text("Введите имя контакта")
                return NAME_INPUT_STATE



def fileImpHandler(update: Update, context: CallbackContext) -> int:
    impNum = importContList(
        getImpList(update, context),
        update.effective_user.id
    )
    
    update.message.reply_text(f"Импортировано {impNum} контактов")

    menuOut(update)
    return MENU_INPUT_STATE