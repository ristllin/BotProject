from StateType import *
from constants import *#Consts
from BadDb import badDb

def parseDbLine(line):
    """
    gets line from DB, returns stateType object from data
    :param line: int<id>;int,int,int;String<response>;String<word>:int<hits>,...;String<origin Sentence>
    id,origins,response,words,origin sentance
    :return:
    """
    try:
        data = line.split(";")
        incoming_states = set()
        incoming_states_raw = data[1].split(",")
        for state in incoming_states_raw:
            incoming_states.add(state)
        words_raw = data[3].replace(" ","").split(",")
        words = {}
        for word in words_raw:
            raw_word = word.split(":")
            words[raw_word[0]] = int(raw_word[1])
        return State(data[0], incoming_states, data[2], words, data[4])
    except Exception as e:
        print("<<<Error: (parseDbLine) Corrupt file>>>.\n",e)
        return None


def searchNextId():
    counter = 0
    with open(FILEPATH, "r+") as f:
        for line in f:
            counter+= 1
    return counter

def writeState(state):
    """
    <<<<<<needs to be testes!!!>>>>
    """
    stringified = str(state.id)+";"+str(state.incomingStates).replace(" ","")+";"+state.response+";"+str(state.words).replace(" ","")+";"+state.origin
    stringified = stringified.replace("}", "").replace("{", "").replace("'", "")
    stringified = removeDoubleBlanks(stringified)
    update = False

    with open(FILEPATH, "r+") as f:
        states = f.readlines()
        for line in states:
            current_state = parseDbLine(line)
            if state.id == current_state.id: #update state
                update = True
        if not update:
            f.write("\n"+stringified)
            return True
    f.close()
    if update:
        for i in range(len(states)):
            if state.id == parseDbLine(states[i]).id:
                states[i] = stringified
                break
        with open (FILEPATH, "w+") as f:
            f.writelines(states)
            return True
    return False

def getState(state_id):
    with open(FILEPATH, "r+") as f:
        for line in f:
            current_state = parseDbLine(line)
            if current_state == None:
                print("<<<Error: (getState) skipping: ",line,">>>")
                continue
            if str(state_id) == str(current_state.id):
                return current_state
    return None

def parseInput(user_input):
    user_input = user_input.lower()
    user_input = removeChars(user_input)
    user_input = removeDoubleBlanks(user_input)
    user_words = user_input.split(" ")
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
                user_input = user_input.replace("?"," ? ")
            elif char == " ": #keep spaces
                continue
            elif char.isalpha():
                continue
            else: #remove char
                user_input = user_input.replace(char,"")
    return user_input

def sortStates(currentInput,former_state):
    """
    gets input returns best matches for it
    :param currentInput:
    :return: returns [state,state,state...] list of stateType ordered by hits, then by score
    """
    tempStatesDb = []
    rslt = [] #[state12,state34,state1,...,state98]
    with open(FILEPATH, "r+") as f:
        for line in f:
            tempStatesDb.append(parseDbLine(line))
    first_element = tempStatesDb.pop(0)
    rslt.append(first_element)
    for new_state in tempStatesDb: #insert all good states
        hits = calcHits(new_state,currentInput)
        final_score = calcTotalScore(new_state,currentInput,former_state)
        if hits > 0:
            inserted = False
            for i in range(len(rslt)): #insert ordered
                other_final_score = calcTotalScore(rslt[i],currentInput,former_state)
                if final_score > other_final_score:
                    rslt.insert(i,new_state)
                    inserted = True
                # if calcHits(new_state,currentInput) > calcHits(rslt[i],currentInput):
                #     rslt.insert(i,new_state)
                #     inserted = True
                # elif (calcHits(new_state,currentInput) == calcHits(rslt[i],currentInput)):
                #     if calcScore(new_state,currentInput) > calcHits(rslt[i],currentInput):
                #         rslt.insert(i, new_state)
                #         inserted = True
            if not inserted:
                rslt.append(new_state)
    tmp = []
    for index in rslt: #cancel doubles
        if index not in tmp:
            tmp.append(index)
    return tmp

def calcHits(state,words):
    count = 0
    for word in state.words:
        if word != []:
            if word[0] in words:
                count +=1
    return count

def calcScore(state,words):
    score = 0
    for word in state.words:
        if word in words:
            score += state.words[word]
    return score

def calcTotalScore(state,currentInput,former_state):
    HITSCONST = 3
    RELATIONCONST = 3
    nonrelative_score = calcScore(state, currentInput) + (calcHits(state, currentInput) * HITSCONST)
    if former_state != None:
        if str(former_state.id) in state.incomingStates:
            return nonrelative_score * RELATIONCONST
    return nonrelative_score