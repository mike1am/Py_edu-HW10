import random


def botTurn(data):
    decr = data['totalCandies'] % (data['maxDecr'] + 1)
    if decr == 0:
        decr = random.randint(1, min(data['totalCandies'], data['maxDecr']))
    
    data['totalCandies'] -= decr
    return decr
