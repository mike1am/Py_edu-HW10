import pickle
import os.path
from functools import reduce

convStore = {}
IMP_EXP_DIR = "imp_exp_files"


def loadData(sig, taskId):
    fName = f".\\data_store\\{taskId}\\{sig}.pickle"
    
    if not os.path.exists(fName):
        return []

    with open(fName, 'rb') as f:
        return pickle.load(f)
    

def saveData(data, sig, taskId):
    try:
        prepDir(f".\\data_store\\{taskId}")
        with open(f".\\data_store\\{taskId}\\{sig}.pickle", "wb") as f:
            pickle.dump(data, f)
    except IOError:
        print("Ошибка записи в файл.")


def saveConv(data, sig):
    convStore[sig] = data


def loadConv(sig):
    if sig in convStore.keys():
        return convStore[sig]
    else: return None


def clearConv(sig):
    convStore.pop(sig)


def prepDir(dirName):
    for dirPart in reduce(
        lambda dirList, part:
            dirList + [(dirList[-1] + "\\" if dirList else "") + part],
        dirName.split("\\"),
        []
    ):
        if not os.path.isdir(dirPart):
            os.mkdir(dirPart)


# возвращает полное имя записанного файла
def writeExpFile(expList, sig, fName):
    fDir = f".\\{IMP_EXP_DIR}\\{sig}"
    
    try:
        prepDir(fDir)
        with open(f"{fDir}\\{fName}", "w") as file:
            for fileStr in expList:
                file.write(fileStr + "\n")
    except IOError:
        print("Ошибка записи в файл.")
        return ""
    
    return f"{fDir}\\{fName}"


def readImpFile(sig, fName):
    readList = []
    try:
        with open(f".\\{IMP_EXP_DIR}\\{sig}\\{fName}", "r") as file:
            for fileStr in file:
                readList.append(fileStr.rstrip("\n"))
    except IOError:
        print("Ошибка чтения из файла.")
        return []
    
    return readList


def getImpPath(sig, fName):
    fDir = f".\\{IMP_EXP_DIR}\\{sig}"
    try:
        prepDir(fDir)
    except IOError:
        print("Ошибка создания директории.")
        return ""
    
    return f"{fDir}\\{fName}"
