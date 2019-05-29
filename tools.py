#----------modules-----------
from StateType import *
from StateFunctions import *
from constants import *
import operator
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


def analsys():
    DB = getStatesDb()
    wordDB = {}
    total_word_count = 0
    for state in DB:
        for word in state.words:
            lowered_word = word.lower()
            if wordDB.get(lowered_word) == None:
                wordDB[lowered_word] = 1
            else:
                wordDB[lowered_word] += 1
            total_word_count += 1
    print("total of: ", len(wordDB), " different words.")
    print("total of: ", total_word_count, " words altogether.")
    sorted_list = []
    for word in wordDB:
        sorted_list.append([wordDB[word],word])
    for word in sorted_list:
        rarity_factor = (1/word[0])*5
        word.append(rarity_factor)
    sorted_list.sort(key=operator.itemgetter(0))
    max_apr = sorted_list[0][0]
    length = len(sorted_list)
    for i in range(100):
        print("rarity: ",i,": ",sorted_list[i])
    for i in range(10):
        print("rarity: ",length-i, ": ", sorted_list[(length-10)+i])


analsys()
