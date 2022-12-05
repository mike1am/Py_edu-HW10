from telegram import Update
from telegram.ext import CallbackContext

from base import convertCSV, parseCSV, writeExpFile, readImpFile, getImpPath

IMP_EXP_FNAME = "Контакты.csv"


def expContacts(contactList, update: Update, context: CallbackContext):
    outMessage = lambda outStr: \
        update.message.reply_text(outStr) if hasattr(update.message, 'reply_text') \
        else update.callback_query.message.reply_text(outStr)
    
    if contactList:
        context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open(
                writeExpFile( # возвращает имя записанного файла
                    convertCSV([
                        {'name': contact['name'], 'phone': contact['phone']} # в переданном списке есть ещё ключи 'ind', которые в экспорт не попадают
                        for contact in contactList
                    ]),
                    update.effective_user.id,
                    IMP_EXP_FNAME
                ),
                "rb"
            )
        )
    else:
        outMessage("Нет данных для экспорта")


def getImpList(update: Update, context: CallbackContext):
    with open(getImpPath(update.effective_user.id, IMP_EXP_FNAME), "wb") as impFile:
        context.bot.get_file(update.message.document).download(out=impFile)
    
    return parseCSV(readImpFile(update.effective_user.id, IMP_EXP_FNAME))
