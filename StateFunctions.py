from StateType import *
from constants import *#Consts
from BadDb import badDb

def parseDbLine(line):
    """
    gets line from DB, returns stateType object from data
    :param line: int<id>;int,int,int;String<response>;String<word>:int<hits>,...;String<origin Sentence>;special
    id,origins,response,words,origin sentance
    :return:
    """
    try:
        data = line.split(";")
        state_id = data[0]
        incoming_states = set()
        incoming_states_raw = data[1].split(",")
        for state in incoming_states_raw:
            incoming_states.add(state)
        response = data[2]
        words_raw = data[3].replace(" ","").split(",")
        words = {}
        for word in words_raw:
            raw_word = word.split(":")
            words[raw_word[0]] = int(raw_word[1]) #change to float?
        origin = data[4]
        special = data[5]
        return State(state_id, incomingStates=incoming_states, response=response, words=words, special=special, origin=origin)
    except IndexError as e:
        print("<<<Error: 1 (parseDbLine) Corrupt file>>>.\n",e)
        print("on Line:",line)
        print("Trying to fix DB, run again when fix finished")
        fixed = []
        with open(FILEPATH, "r+") as f:
            for line in f:
                if line != "" and line != "\n":
                    fixed.append(line)
        f.close()
        with open(FILEPATH, "w") as f:
            f.writelines(fixed)
        return None
    except Exception as e:
        print("<<<Error: 2 (parseDbLine) Corrupt file>>>.\n", e)


def searchNextId():
    """
    search what is the next missing id in DB
    :return:
    """
    counter = 0
    with open(FILEPATH, "r+") as f:
        for line in f:
            counter+= 1
    return counter

def writeState(state):
    """
    returns true if managed to write file.
    recognizes if it should update or add new state.
    """
    # print("working on state: ",state)
    stringified = str(state.id)+";"+str(state.incomingStates).replace(" ","")+";"+state.response+";"+str(state.words).replace(" ","")+";"+state.origin+";"+str(state.special)
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
            # print("adding new:",stringified) #debug
            return True
    f.close()
    if update:
        for i in range(len(states)):
            if state.id == parseDbLine(states[i]).id:
                states[i] = stringified
                break
        with open (FILEPATH, "w+") as f:
            f.writelines(states)
            # print("updating, new:",str(states)) #debug
            return True
    return False

def getState(state_id):
    """
    find state in DB by ID and returns it as a StateType
    :param state_id:
    :return:
    """
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
    """
    Parses user input, removes all non alpha\numeric chars, double spaces
    :param user_input:
    :return:
    """
    user_input = user_input.lower()
    user_input = removeChars(user_input)
    user_input = removeDoubleBlanks(user_input)
    user_words = user_input.split(" ")
    # removeBadList(user_words)
    return user_input

def removeBadList(user_words): #working????
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
    rslt.append(tempStatesDb.pop(0)) #adding
    for new_state in tempStatesDb: #insert all good states
        hits = \
            lcHits(new_state,currentInput)
        final_score = calcTotalScore(new_state,currentInput,former_state)
        if hits > 0:
            inserted = False
            for i in range(len(rslt)): #insert in order by score
                other_final_score = calcTotalScore(rslt[i],currentInput,former_state)
                if currentInput == new_state.origin:
                    rslt.insert(0, new_state) #add to head of list
                    inserted = True
                    break
                if final_score > other_final_score: #add in position of list
                    rslt.insert(i,new_state)
                    inserted = True
                    break
            if not inserted: #add to end of list if not there
                if new_state not in rslt:
                    rslt.append(new_state)
    tmp = []
    for index in rslt: #cancel doubles
        if index not in tmp:
            tmp.append(index)
    return tmp

def calcHits(state,currentInput):
    """
    Calculates how many words appeared before in given state that appear in current input
    :param state:
    :param currentInput:
    :return:
    """
    count = 0
    words = currentInput.split(" ")
    for word in state.words:
        if words != []:
            if word in words:
                count +=1
    return count

def calcScore(state,currentInput):
    """
    Calculates accumelated score\weight from words matching in current Input
    :param state:
    :param currentInput:
    :return:
    """
    score = 0
    words = currentInput.split(" ")
    for word in state.words:
        if word in words:
            score += state.words[word]
    return score

def calcTotalScore(state,currentInput,former_state):
    """
    Calculates Hits, Score and relation to a total score, used to determine most relevant state
    :param state: StateType (for state words)
    :param currentInput: String (current user parsed words in single String)
    :param former_state: StateType (for id to check if is an origin)
    :return:
    """
    # print("for state: ",state.response," and state: ",former_state.response,"\n Calc Score:",calcScore(state, currentInput),", Calc hits: ",calcHits(state, currentInput))
    nonrelative_score = calcScore(state, currentInput) * SCORECONST + (calcHits(state, currentInput) * HITSCONST)
    if former_state != None:
        if str(former_state.id) in state.incomingStates:
            return nonrelative_score * RELATIONCONST
    return nonrelative_score

def searchOrigin(origin):
    """
    Searches StateDB for state with provided origin
    :param origin: String - containing unparsed user input
    :return: None if origin doesn't exist in any state, else returns state
    """
    StatesDb = []
    with open(FILEPATH, "r+") as f: #loading states DB
        for line in f:
            StatesDb.append(parseDbLine(line))
    for state in StatesDb:
        if state.origin == origin:
            return state
    return None

