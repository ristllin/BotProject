#----------modules-----------
from StateType import *
from StateFunctions import *
from constants import *
from BadDb import *
#----------libraries----------
import wikipedia
import random
import datetime
#----------constants----------
CurrentState = None #StateType
CurrentInput = None
RESPONSEOPTIONS = [] #[state123,state34...] ordered

def create():
    """
    creates new node and updates DB
    :param CurrentInput: getting parsed user input
    :param CurrentState: getting current state
    :return: None
    """
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    response = input("Enter response:")
    new_state = State(searchNextId(), words={}, origin=CurrentInput)
    new_state.updateStateIncoming(CurrentState.id)
    new_state.updateStateResponse(response)
    new_state.updateStateWords(CurrentInput)
    writeState(new_state)
    print("I'm smarter now, try me again.")

def createSpecial():
    """
    creates new active node and updates DB
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
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    stateNum = ""
    for ltr in command:
        if ltr.isnumeric():
            stateNum += ltr
    if RESPONSEOPTIONS != []:
        RESPONSEOPTIONS[0] = getState(int(stateNum))
    else:
        RESPONSEOPTIONS.append(getState(int(stateNum)))

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
    # print("state under update:",state)
    state.updateStateIncoming(CurrentState.id)
    state.updateStateWords(CurrentInput)
    # print("writing state:",state)
    writeState(state)
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
        print("Debug: Ran of of options")

def correct():
    response = input("Enter Correct response:")
    RESPONSEOPTIONS[0].updateStateResponse(response)
    writeState(RESPONSEOPTIONS[0])

def executeSpecial(command,userInput):
    """
    gets String "<API>:<Command>:<data>" passes command to relevant api
    :param command:
    :return: None
    """
    parsed = command.split(":") #parsed = [API,COMMAND,DATA]
    if len(parsed) == 3:
        api = parsed[0]
        command = parsed[1]
        data = parsed[2]
        if "internet" in api:
            internet(command, data, userInput)
        elif "random" in api:
            randoms(command, data, userInput)
        elif "time" in api:
            time(command,data,userInput)

def time(command,data,userInput):
    if command == "time":
        print(str(datetime.datetime.now()))

def memory():
    """
    saving temporary data for conversation
    saving it on computer...?
    :return:
    """
    return True

def internet(command,data,userInput):
    if command == "search":
        try:
            content = userInput
            for word in badsearchDb:
                content = content.replace(" "+word+" "," ")
            # print("debug: searching internet for:",content)
            info = wikipedia.summary(content, sentences=5)
            print(info[:200])
        except Exception as e:
            print("Failed ",e) #interconnection problems e.g.?

def randoms(command,data,userInput):
    if command == "coin":
        toss = random.randint(0, 1)
        if toss == 0:
            print("heads")
        else:
            print("tails")
    elif command == "pass": #generates password
        length = 10
        if "length" in userInput:
            num = "0"
            for char in userInput:
                if not (char.isalpha() or char == " "):
                    num += char
            print(num)
            length = int(num)
        print("".join([chr(random.randint(33,126)) for i in range(int(length))]))

def main():
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    CurrentState = getState(0)
    print("-------Agent Running-------")
    if CurrentState == None:
        print("<<<Error>>>> Empty DB")
        quit()
    while True:
        # try:
            print("<<<",CurrentState.response)
            if "Null" not in CurrentState.special and CurrentInput != None:
                executeSpecial(CurrentState.special,CurrentInput)
            CurrentInput = parseInput(input(">>> ")) #result updates CURRENTINPUT
            if CurrentInput == "":
                continue
            RESPONSEOPTIONS = sortStates(CurrentInput,CurrentState) #list of stateType [state34,state21...]
            if LEARNINGMODE:
                command = ""
                while command != 'fix' or command != 'restart' or command != 'y':
                    if RESPONSEOPTIONS != []: #no options
                        print("<<<",RESPONSEOPTIONS[0].response,"\nIs State: ",RESPONSEOPTIONS[0].id," good? Origin: ",RESPONSEOPTIONS[0].origin)
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
                    print("Hmm... it seams I am clueless.")
                    command = input("do you want to restart the conversation or rephrase?")
                    if "restart" in command:
                        CurrentState = getState(0)
                else:
                    CurrentState = getState(RESPONSEOPTIONS[0].id)
        # except Exception as e:
        #     print("<<<Error: Main crashed >_< >>>",e)
        #     quit()
        #     print("Something went wrong, lets restart")


if __name__ == "__main__":
    main()