from base.data_storing import saveData, loadData

TASK_ID = "pb"


# Формирует список контактов на основе строки, в которой должно 
# содержаться имя или часть имени контакта
# sig - уникальная сигнатура набора данных справочника
# Возвращает список словарей вида {'ind': <уникальный индекс контакта>,
# 'name': <имя контакта>, 'phone': <телефон контакта>}
def getContactList(contName: str, sig: str):
    phonebookData = loadData(sig, TASK_ID)
    resList = []
    
    for ind, contact in enumerate(phonebookData):
        if contName.lower() in contact['name'].lower():
            resList.append({
                'ind': ind,
                'name': contact['name'],
                'phone': contact['phone']
            })

    return resList


def addContact(contName: str, contPhone: str, sig: str) -> None:
    phonebookData = loadData(sig, TASK_ID)

    phonebookData.append({
        'ind': len(phonebookData), 
        'name': contName,
        'phone': contPhone
    })

    saveData(phonebookData, sig, TASK_ID)


# contact - словарь с контактом, как эл. списка, возвращаемого getContactList
def edContact(contact, contName: str, contPhone: str, sig: str) -> None:
    phonebookData = loadData(sig, TASK_ID)

    phonebookData[contact['ind']]['name'] = contName
    phonebookData[contact['ind']]['phone'] = contPhone

    saveData(phonebookData, sig, TASK_ID)


# contList - список словарей с контактами - см. возврат getContactList
def delContacts(contList, sig):
    phonebookData = loadData(sig, TASK_ID)

    for i, ind in enumerate([contact['ind'] for contact in contList]):
        phonebookData.pop(ind - i) # поскольку при удалении индексы сдвигаются

    saveData(phonebookData, sig, TASK_ID) 
