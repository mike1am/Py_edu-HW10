import re

from base.data_storing import saveData, loadData

TASK_ID = "Phonebook"
PHONE_RE = r"^(8|(\+\d{1,4})[ ]?)?(\(\d{1,5}\))?([\- ]?\d+)+$"


# Формирует список контактов на основе строки, в которой должно 
# содержаться имя или часть имени контакта
# sig - уникальная сигнатура набора данных справочника
# Возвращает список словарей вида {'ind': <уникальный индекс контакта>,
# 'name': <имя контакта>, 'phone': <телефон контакта>}
def getContactList(contName: str, sig: str, strong = False):
    phonebookData = loadData(sig, TASK_ID)
    resList = []
    
    for ind, contact in enumerate(phonebookData):
        if not strong and contName.lower() in contact['name'].lower() \
                or strong and contName == contact['name']:
            resList.append({
                'ind': ind,
                'name': contact['name'],
                'phone': contact['phone']
            })
            
            if strong: return resList

    return resList


def addContact(contName: str, contPhone: str, sig: str) -> None:
    phonebookData = loadData(sig, TASK_ID)

    phonebookData.append({
        'name': contName,
        'phone': contPhone
    })

    saveData(phonebookData, sig, TASK_ID)


def edContact(contInd, newName: str, newPhone: str, sig: str) -> None:
    phonebookData = loadData(sig, TASK_ID)

    phonebookData[contInd]['name'] = newName
    phonebookData[contInd]['phone'] = newPhone

    saveData(phonebookData, sig, TASK_ID)


# contList - список словарей с контактами - см. возврат getContactList
def delContacts(contList, sig):
    phonebookData = loadData(sig, TASK_ID)

    for i, ind in enumerate([contact['ind'] for contact in contList]):
        phonebookData.pop(ind - i) # поскольку при удалении индексы сдвигаются

    saveData(phonebookData, sig, TASK_ID) 


def importContList(contList, sig):
    impCnt = 0

    for contact in contList:
        if not contact['phone'] or re.fullmatch(PHONE_RE, contact['phone']): # если пусто или телефон
            matchContacts = getContactList(contact['name'], sig, strong=True)

            if matchContacts:
                edContact(matchContacts[0]['ind'], contact['name'], contact['phone'], sig)
            
            else:
                addContact(contact['name'], contact['phone'], sig)

            impCnt += 1

    return impCnt

