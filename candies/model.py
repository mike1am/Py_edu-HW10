import random

from base import loadData, saveData

TASK_ID = "Candies"


def botTurn(data):
    decr = data['totalCandies'] % (data['maxDecr'] + 1)
    if decr == 0:
        decr = random.randint(1, min(data['totalCandies'], data['maxDecr']))
    
    data['totalCandies'] -= decr
    return decr


def gameScore(md, sig):
    gameData = loadData(sig, TASK_ID)

    if gameData:
        if md > 0:
            gameData['player'] += md
        elif md < 0:
            gameData['bot'] -= md

    else:
        gameData = {
            'player': md if md > 0 else 0,
            'bot': -md if md < 0 else 0
        }
    
    saveData(gameData, sig, TASK_ID)

    return f"{str(gameData['player'])} : {str(gameData['bot'])}"