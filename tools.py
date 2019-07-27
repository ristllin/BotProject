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

def AllKnownWords():
    """
    Goes over DB and returns a set with all known words
    :return: <Set> a set containing everyword in initial DB
    """
    DB = set()
    with open(FILEPATH, "r+") as f:
        for line in f:
            state = parseDbLine(line)
            for word in state.words:
                DB.add(word)
    return DB

def analysis(vrbs=False):
    """
    analyzes the states DB to find which words are rare and which are common
    it generates a dict containing all of the words that have appeared and a rarity factor.
     Rarity factor value is set from 1 to DIFVALUE, normalized\mapped to the amount of appearances
    :return:
    """
    DIFVALUE = 10 #max value a word can get for being rare
    DB = getStatesDb()
    wordDB = {} #{"word":[appearances,rarity_factor]..."last_word":[appr,rarty_fctr]}
    total_word_count = 0
    for state in DB:
        for word in state.words:
            lowered_word = word.lower()
            if wordDB.get(lowered_word) == None:
                wordDB[lowered_word] = [1]
            else:
                wordDB[lowered_word][0] += 1
            total_word_count += 1
    sorted_list = []
    for word in wordDB:
        sorted_list.append([wordDB[word][0],word])
    sorted_list.sort(key=operator.itemgetter(0))
    for word in sorted_list:
        rarity_factor = (1/word[0])*DIFVALUE
        # print("debug 2:",word)
        (wordDB[word[1]]).append(rarity_factor)
    length = len(sorted_list)
    if vrbs:
        print("total of: ", len(wordDB), " different words.")
        print("total of: ", total_word_count, " words altogether.")
        for i in range(10):
            print("rarity: ",i,": ",sorted_list[i])
        for i in range(10):
            print("rarity: ",length-i, ": ", sorted_list[(length-10)+i])
    return wordDB

def removeBadWords(userinput):
    """
    removes bad search words from userinput
    :param userinput: single String
    :return: single String
    """
    userWords = userinput.split(" ")
    # print("userWords:",userWords)
    rslt = ""
    for word in userWords:
        if word not in badsearchDb:
            rslt += word + " "
        # else:
            # print("caught:",word)
    return rslt


def normalizeByRarity(DB):
    db = getStatesDb()
    for state in db:
        for word in state.words:
            state.words[word] += int(DB[word.lower()][1])
            writeState(state)
# normalize()
# db = analysis()
# normalizeByRarity(db)
