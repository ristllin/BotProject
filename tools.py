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

def importDataSet(dataset,stateDB):
    """
    teaches bot (updates stateDB) according to given dataset in proper format
    the each thread (title) is being treated as a new question.
    each thread is being preparsed (reaplcing \n with a space)
    each title is treated as a new question.
    />>> Title
    />> username|||question\answer\originalQuestion|||content
    adds words from title to original question and gives extra weight to these words
    :param dataset: path to dataset text file, assuming is in format as mentioned above
    :param stateDB: path to DB text file being updated
    :return:
    """
    #load dataset as a single string
    #replace \n with " "
    #split threads by >>> (titles)
    #for each thread
    #check if there is an original question and an answer, if there isn't skip thread
    #pop title and save words (without connectors)
    #split conversation by >> (different comments)
    #unify following comments by the same user
    #insert question as user question
    #set next answer as response
    #if there are more followup question insert as followup questions and answers in branch
