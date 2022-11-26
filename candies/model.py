import random

totalCandies = 0
maxDecr = 0

def botTurn():
    global totalCandies
    decr = totalCandies % (maxDecr + 1)
    if decr == 0:
        decr = random.randint(1, min(totalCandies, maxDecr))
    
    totalCandies -= decr
    return decr


def playerTurn(decr):
    global totalCandies
    totalCandies -= decr


def setTotalCandies(num):
    global totalCandies
    totalCandies = num


def setMaxDecr(num):
    global maxDecr
    maxDecr = num


def getTotalCandies():
    return totalCandies


def getMaxDecr():
    return maxDecr