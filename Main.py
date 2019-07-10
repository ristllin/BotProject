#----------modules-----------
from StateType import *
from StateFunctions import *
from constants import *
from BadDb import *
from SpecialAPI import *
from tools import *
from math import *
from nltk.corpus import wordnet

#----------libraries----------
import wikipedia
import random
import datetime
import requests

#----------constants----------
CurrentState = None #StateType
CurrentInput = None #String
RawInput = None #String
RESPONSEOPTIONS = [] #[state123,state34...] ordered
TempMemory = [("name","user")] #saving temporary data

normalize()

def create(crnt_state_id = None,crnt_input = None,rspns = None,strength_factor = 1):
    """
    creates new node and updates DB
    :param CurrentInput: getting parsed user input
    :param CurrentState: getting current state
    :return: None
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    if (crnt_state_id == None):
        response = input("Enter response:")
        new_state = State(searchNextId(), words={}, origin=CurrentInput)
        new_state.updateStateIncoming(CurrentState.id)
        new_state.updateStateResponse(response)
        new_state.updateStateWords(CurrentInput,strength_factor)
        writeState(new_state)
        print("I'm smarter now, try me again.")
    else: #direct data, not from global
        if searchOrigin(crnt_input) != None: #skip existing states
            return
        new_state = State(searchNextId(), words={}, origin=crnt_input)
        new_state.incomingStates = {crnt_state_id}
        new_state.updateStateResponse(rspns)
        removeBadList(crnt_input.split(" "))
        crnt_input = "".join(crnt_input)
        new_state.updateStateWords(crnt_input,strength_factor)
        writeState(new_state)

def createSpecial():
    """
    creates new active node and updates DB (with special field)
    :param CurrentInput: getting parsed user input
    :param CurrentState: getting current state
    :return: None
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    response = input("Enter response:")
    api = input("Enter api (e.g. 'internet'):")
    command = input("Enter command (e.g. 'search'):")
    data = input("Enter data (as required by the API):")
    special = api+":"+command+":"+data
    new_state = State(searchNextId(), words={}, origin=CurrentInput, special=special)
    new_state.updateStateIncoming(CurrentState.id)
    new_state.updateStateResponse(response)
    new_state.updateStateWords(CurrentInput)
    writeState(new_state)
    print("I'm smarter now, try me again.")

def fullDebug():
    """
    prints out in full all dynamic variables
    :param CurrentInput:
    :param CurrentState:
    :param RESPONSEOPTIONS:
    :return:
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    print("___________________________")
    print("\n*Current Input:", CurrentInput)
    print("*Current State: ", CurrentState)
    print("\n*Response Options: ", RESPONSEOPTIONS)
    print("___________________________")

def debug():
    """
    Prints out current response possible response states by decending score and their id
    :param CurrentInput:
    :param CurrentState:
    :param RESPONSEOPTIONS:
    :return:
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    print("___________________________")
    for state in RESPONSEOPTIONS:
        score = calcTotalScore(state, CurrentInput, CurrentState)
        print(state.id + ": " + str(score) + " ,", end="")
    print("\n___________________________")

def search(command):
    """
    prints out by id order all of the states containing search query in their response
    :param command: "search <search query>"
    :return:
    """
    search_string = command[7:].lower()
    print("___________________________")
    tempStatesDb = []
    with open(FILEPATH, "r+") as f:
        for line in f:
            tempStatesDb.append(parseDbLine(line))
    for state in tempStatesDb:
        if search_string in state.response.lower():
            print("id: ", state.id, ": " + state.response + " --- " + state.origin)
    print("___________________________")

def connect(command):
    """
    gets user command, parses it and retrieves an integer stating which state to add to RESPONSEOPTIONS list
    :param command: string
    :return: None
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    stateNum = ""
    for ltr in command:
        if ltr.isnumeric():
            stateNum += ltr
    try:
        target_state = getState(int(stateNum))
        if target_state != None:
            if RESPONSEOPTIONS != []:
                RESPONSEOPTIONS[0] = target_state
            else:
                RESPONSEOPTIONS.append(target_state)
        else:
            print("Could not find state")
    except Exception as e:
        print("<<<Error: Connecting state failed>>>",e)

def yes():
    """
    Bot should learn current new path, updates state
    :param CurrentInput:
    :param CurrentState:
    :param RESPONSEOPTIONS:
    :return:
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    state = RESPONSEOPTIONS[0]
    state.updateStateIncoming(CurrentState.id)
    state.updateStateWords(CurrentInput)
    writeState(state)
    if STRONGMODE: #strengthen until first
        RESPONSEOPTIONS = sortStates(CurrentInput, CurrentState)
        while RESPONSEOPTIONS[0].id != state.id:
            print("Boosting up...")
            state.updateStateWords(CurrentInput)
            writeState(state)
            RESPONSEOPTIONS = sortStates(CurrentInput, CurrentState)
    CurrentState = getState(state.id)

def no():
    """
    Bot gave wrong response, change to next state by score
    :return:
    """
    global RESPONSEOPTIONS
    if RESPONSEOPTIONS != []:
        RESPONSEOPTIONS.pop(0)
    else:
        print("RESPONSEOPTIONS - empty. connect a new state or reset")

def correct():
    """
    re-set current state response.
    :return: None
    """
    response = input("Enter Correct response:")
    RESPONSEOPTIONS[0].updateStateResponse(response)
    writeState(RESPONSEOPTIONS[0])

def importDataSet(dataset,STRENGTHFACTOR = 1):
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
    :return: None (edits stateDB)
    """
    #-------------Load and Parse--------------
    #parsed_DB = [[<Title>,[<user_name>,<responseType>,<response_content>],...,responses],...,more threads]
    # STRENGTHFACTOR = 5 #what weight each word should get automatically when loaded
    print("ImportDataSet() called")
    print("Loading and parsing data")
    with open(dataset,"r") as file:
        thread_count = 0
        response_count = 0
        data = file.read() #load dataset as a single string
        data = data.replace("\n"," ") # replace \n with " "
        data = data.split(">>>") #split threads by >>> (titles)
        data.pop(0)
        parsed_DB = []
        for thread in data: #for each thread
            thread_count += 1
            parsed_thread = []
            split_thread = thread.split(">>") #split conversation by >> (different comments)
            title = (split_thread[0].split("|||"))[1]
            parsed_thread.append(title)
            split_thread.pop(0) #remove title
            for response in split_thread:
                response_count += 1
                username,response_type,response_content = response.split("|||")
                parsed_thread.append([username,response_type,response_content])
            parsed_DB.append(parsed_thread)
        print("parsed: ",thread_count," threads. and ",response_count," responses.")
        question = True
        for thread in parsed_DB:
            try:
                # print("----------->starting thread: ",thread)
                state_id = 0
                title = thread[0] #pop title
                thread.pop(0)
                thread[0][2] += title #add title key words to original question
                for comment in thread:
                    content = comment[2].replace(";","").replace(",","").replace(":","")
                    if len(content) > 200: #cut long messages <<<<hurts algo>>>>
                        content = content[:200]
                    # print("--->On comment:",comment)
                    if question: #insert question as user question
                        user_input = content
                        question = not question
                    else: #content as response
                        response = content
                        # print("Creating: state:",state_id," user input:",user_input,"response: ",response)
                        # print("<<<debug: >>>",state_id)
                        next_state_id = searchNextId()
                        create(crnt_state_id = state_id,crnt_input = user_input,rspns = response,strength_factor = STRENGTHFACTOR) #create state with this response and previous userinput
                        state_id = next_state_id
                        question = not question
            except Exception as e:
                print("Error on thread:",thread)

def calcCertainty(input_length,avgCmp,current_score,avg_score_per_word):
    """

    :param input_length: int - amount of words in current sentence
    :param avgCmp: amount of inputs calculated for given average
    :param current_score: ambiguous Score from scoring algo
    :param avg_score_per_word:
    :return:
    """
    TOLERANCE = 0.2
    avg_score_per_word = (avg_score_per_word * avgCmp + (current_score / input_length)) / (avgCmp + 1)
    avgCmp += 1
    current_avg_per_word = current_score / input_length
    if current_avg_per_word > avg_score_per_word * (1 + TOLERANCE * 3):
        certainty = 4 #very good
    elif current_avg_per_word > avg_score_per_word * (1 + TOLERANCE):
        certainty = 3 #good
    elif (current_avg_per_word) * (1 + TOLERANCE) < avg_score_per_word:
        certainty = 1 #bad
    elif (current_avg_per_word) * (1 + TOLERANCE * 3) < avg_score_per_word:
        certainty = 0 #very bad
    else:
        certainty = 2 #Medium
    return certainty,avgCmp,current_score,avg_score_per_word


def EnhanceResults(user_input, DB, iter = 0):
    """
    Gets a sentence, replaces unknown words with alternative words using word2vec.
    :param user_input: (Str) after basic parsing (bad words removal etc..)
    :return: (Str) Alternative Sentence
    """
    if DEBUG: print("debug: EnhanceResults called()")
    words = user_input.split(" ")
    alternative_sentance = ""
    for word in words:
        if word in DB:
            alternative_sentance += word + " "
        else:
            alternative_sentance += GetAlternative(word,iter) + " "
    if DEBUG: print("debug: alternative sentance created: ",alternative_sentance)
    return alternative_sentance

def GetAlternative(word,iter):
    """
    Gets a word (String), uses natural language toolkit to find synonyms to the given word, and returns one of them randomly (String)
    :param word: String
    :return: (String) a synonym to the given word
    """
    alternative = word
    synonyms = []
    for syn in wordnet.synsets(word):
        for lm in syn.lemmas():
            synonyms.append(lm.name())
    if len(synonyms) > iter:
        alternative = synonyms[iter]
        if DEBUG: print("debug: synonyms are: ",synonyms)
    if DEBUG: print("debug: Alt for: ",word," is: ",alternative)
    return alternative


def main():
    global CurrentState
    global CurrentInput
    global RawInput
    global RESPONSEOPTIONS
    global TempMemory
    #--------init---------------
    print("-------Initializing-------")
    DB = AllKnownWords()
    avg_score_per_word = 5 #<<<<<>>>>> need to build algo for that
    avgCmp = 1
    CurrentState = getState(0) #set state to init
    # importDataSet(r"D:\projects\BotProject\basicCarQuestions.txt",3) #add new dataset
    # importDataSet(r"D:\projects\BotProject\fordForums.txt",1 )  # add new dataset
    print("-------Agent Running-------")
    if CurrentState == None:
        print("<<<Error>>>> Empty DB")
        quit()
    while True: #should be True
        try:
            print("<<<",CurrentState.response)                                                      #print current State response
            if "Null" not in CurrentState.special and CurrentInput != None:                         #Special Apis activation
                executeSpecial(CurrentState.special,CurrentInput,TempMemory,RawInput)
            RawInput = input(">>> ")
            CurrentInput = parseInput(RawInput)                                                     #Parse userInput...
            if CurrentInput == "":                                                                  #No input, repeat
                continue
            # Calc Best response for input, returns a list of stateType [state34,state21...]
            RESPONSEOPTIONS = sortStates(CurrentInput,CurrentState)
            #analyze Chosen state
            iter = 0
            input_length = len(CurrentInput.split(" "))
            current_score = calcTotalScore(RESPONSEOPTIONS[0], CurrentInput, CurrentState)
            certainty,avgCmp,current_score,avg_score_per_word = calcCertainty(input_length,avgCmp,current_score,avg_score_per_word)
            while certainty < 2 and iter <= MAXENHANCMENTITER:
                if DEBUG: print("debug: Activating Enhancement tools")
                new_sentance = EnhanceResults(CurrentInput,DB, iter) #find unknown words, get alternative for each, create new sentance with them
                alternative_state = sortStates(new_sentance, CurrentState)[0]
                alt_score = calcTotalScore(alternative_state, new_sentance, CurrentState)
                if DEBUG: print("debug: alt_score: ",alt_score)
                if alt_score > current_score:
                    RESPONSEOPTIONS.insert(0, alternative_state) #if higher than current score, push to RESPONSEOPTIONS
                certainty, avgCmp, current_score, avg_score_per_word = calcCertainty(input_length, avgCmp, current_score,avg_score_per_word)
                iter += 1
            if certainty < 1: #still bad
                print("I am sorry, I am not sure how to answer that. Please try to rephrase.")
                continue
            if LEARNINGMODE:
                command = ""
                while command != 'fix' or command != 'restart' or command != 'y':
                    if RESPONSEOPTIONS != []: #no options
                        print("<<<",RESPONSEOPTIONS[0].response,"\nIs State: ",RESPONSEOPTIONS[0].id," good? Origin: ",RESPONSEOPTIONS[0].origin)
                        print("CurrentScorePerWord: ",current_score/input_length," TotalAvgScorePerWord:",avg_score_per_word," certainty:",certainty)
                        print("<y>-yes,<n>-no/next,<r>-fix response,'create', 'connect <id#>', 'search <string>'")
                    else:
                        print("I'm ClueLess...\n'fix' text, 'restart', 'connect #' to add a known state or 'create' new state?")
                    command = input(">")
                    if command == "create": #creates new state
                        create()
                        break
                    if command == "create special": #creates new active state
                        createSpecial()
                        break
                    elif command == "restart" or command == "reset":
                        CurrentState = getState(0)
                        break
                    elif command == "y" and RESPONSEOPTIONS != []:
                        yes()
                        break
                    elif command == "n":
                        no()
                    elif command == "r":
                        correct()
                    elif "connect" in command:
                        connect(command)
                    elif command == "full debug" or command == "debug full":
                        fullDebug()
                    elif command == "debug":
                        debug()
                    elif "search" in command:
                        search(command)
                    else:
                        print("---Unknown command---")
            else: #not learning mode
                if RESPONSEOPTIONS == None:
                    print("Hmm... it seems I am clueless.")
                    command = input("do you want to restart the conversation or rephrase?")
                    if "restart" in command:
                        CurrentState = getState(0)
                else:
                    CurrentState = getState(RESPONSEOPTIONS[0].id)
        except Exception as e:
            if LEARNINGMODE:
               print("<<<Error: Main crashed >_< >>>",e)
            else:
                print("Ohh boy, I am not feeling so well, lets try again")
                CurrentState = getState(0)


if __name__ == "__main__":
    main()