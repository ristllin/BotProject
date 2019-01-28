from StateType import *
from Main import *
from BadDb import badDb

def parseDbLine(line):
    """
    gets line from DB, returns stateType object from data
    :param line:
    :return:
    """
    try:
        data = ";".split(line)
        incoming_states = {}
        incoming_states_raw = ",".split(data[1])
        for state in incoming_states_raw:
            incoming_states.add(state)
        words_raw = ",".split(data[3])
        words = {}
        for word in words_raw:
            raw_word = ":".split(word)
            words[raw_word[0]] = int(raw_word[1])
    except Exception as e:
        print("<<<Error: Corrupt file>>>.\n",e)
    return State(data[0],incoming_states,data[2],words)

def searchNextId():
    counter = 0
    with open(FILEPATH, "r+") as f:
        for line in f:
            counter+= 1
    return counter + 1

def writeState(state):
    """
    <<<<<<needs to be testes!!!>>>>
    """
    with open(FILEPATH, "r+") as f:
        for line in f:
            current_state = parseDbLine(line)
            if state.id == current_state.id: #update state
                f.write(str(state.id) + ";" + str(state.incomingStates) + ";" + state.response + ";" + str(state.words))
                return True
        f.write(str(state.id)+";"+str(state.incomingStates)+";"+state.response+";"+str(state.words))
        return True
    return False

def getState(state_id):
    with open(FILEPATH, "r+") as f:
        for line in f:
            current_state = parseDbLine(line)
            if str(state_id) == str(current_state.id):
                return current_state
    return None

def setState(new_state_id):
    global CurrentState
    new_state = getState(new_state_id)
    if new_state != None:
        CURRENTSTATE = new_state
    else:
        print("Error: state '",new_state_id,"' was not found in DB.")

def parseInput(user_input):
    user_input = user_input.lower()
    user_input = removeChars(user_input)
    user_input = removeDoubleBlanks(user_input)
    user_words = " ".split(user_input)
    removeBadList(user_words)
    return user_input

def removeBadList(user_words):
    for word in user_words:
        if word in badDb:
            user_words.remove(word)

def removeDoubleBlanks(user_input):
    while ("  " in user_input):
        user_input = user_input.replace("  "," ")
    return user_input

def removeChars(user_input):
    for char in user_input:
        if not(char.isalnum()):
            if char == "?": #keep ? as word
                user_input.reaplce("?"," ? ")
            if char == " ": #keep spaces
                continue
            else: #remove char
                user_input.replace(char,"")

def sortStates(currentInput):
    """
    gets input returns best matches for it
    :param currentInput:
    :return: returns [state,state,state...] ordered by hits, then by score
    """
    tempStatesDb = []
    rslt = [] #[state12,state34,state1,...,state98]
    with open(FILEPATH, "r+") as f:
        for line in f:
            tempStatesDb.append(parseDbLine(line))
    first_element = tempStatesDb.pop(0)
    rslt.append(first_element)
    for new_state in tempStatesDb: #insert all good states
        if calcHits(new_state,currentInput) > 0:
            inserted = False
            for i in range(len(rslt)): #insert ordered
                if calcHits(new_state,currentInput) > calcHits(rslt[i],currentInput):
                    rslt.insert(i,new_state)
                    inserted = True
                elif (calcHits(new_state,currentInput) == calcHits(rslt[i],currentInput)):
                    if calcScore(new_state,currentInput) > calcHits(rslt[i],currentInput):
                        rslt.insert(i, new_state)
                        inserted = True
            if not inserted:
                rslt.append(new_state)
    return rslt

def calcHits(state,words):
    count = 0
    for word in state.words:
        if word[0] in words:
            count +=1
    return count

def calcScore(state,words):
    score = 0
    for word in state.words:
        if word in words:
            score += state.words[word]
    return score

def userClueless():
