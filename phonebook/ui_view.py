from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton


def menuOut(update: Update):
    MENU_ITEMS = {
        'add': "Добавить контакт",
        'del': "Удалить контакты",
        'ed': "Редактировать контакт",
        'show': "Просмотр контактов",
        'imp': "Импорт из файла",
        'exp': "Экспорт в файл",
        'end': "Выход"
    }

    replayMarkup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(MENU_ITEMS[key], callback_data=key)]
            for key in MENU_ITEMS.keys()]
    )

    if hasattr(update.message, 'reply_text'):
        update.message.reply_text(
            "Выберите действие", reply_markup=replayMarkup
        )
    else:
        update.callback_query.message.reply_text(
            "Выберите действие", reply_markup=replayMarkup
        )


def showContacts(contactList, update: Update):
    outMessage = lambda outStr: \
            update.message.reply_text(outStr) if hasattr(update.message, 'reply_text') \
            else update.callback_query.message.reply_text(outStr)
    
    if contactList:
        outMessage("Найдены контакты:")
        
        for contact in contactList:
            outMessage(f"Имя: {contact['name']}" + \
                    f"\nТелефон: {contact['phone']}")

    else:
        outMessage("Контакты не найдены")
