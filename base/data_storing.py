import pickle
import os.path

convStore = {}


def loadData(sig, taskId):
    fName = f"{taskId}-{sig}.pickle"
    
    if not os.path.exists(fName):
        return []

    with open(fName, 'rb') as f:
        return pickle.load(f)
    

def saveData(data, sig, taskId):
    with open(f"{taskId}-{sig}.pickle", "wb") as f:
        pickle.dump(data, f)


def saveConv(data, sig):
    convStore[sig] = data


def loadConv(sig):
    if sig in convStore.keys():
        return convStore[sig]
    else: return None


def clearConv(sig):
    convStore.pop(sig)
    