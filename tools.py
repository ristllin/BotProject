#----------modules-----------
from StateType import *
from StateFunctions import *
from constants import *
from BadDb import *
from SpecialAPI import *

def normalize():
    """
    goes over every word in db and sets it's value to max value set
    run in Main to activate
    :return: None
    """
    MAXVALUE = 5
    db = getStatesDb()
    for state in db:
        for word in state.words:
            if state.words[word] > 5:
                state.words[word] = MAXVALUE
                writeState(state)

def getStatesDb():
    """
    pulls db from path and parses it into a list
    :return: list with all states in DB
    """
    tempStatesDb = []
    with open(FILEPATH, "r+") as f:
        for line in f:
            tempStatesDb.append(parseDbLine(line))
    return tempStatesDb