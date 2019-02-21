#----------modules-----------
from StateType import *
from StateFunctions import *
from constants import *
from BadDb import *
from SpecialAPI import *
from tools import *

#----------libraries----------
import wikipedia
import random
import datetime
import requests

#----------constants----------
CurrentState = None #StateType
CurrentInput = None #String
RESPONSEOPTIONS = [] #[state123,state34...] ordered
TempMemory = [("name","user")] #saving temporary data

normalize()

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
        print("RESPONSEOPTIONS - empty. connect a new state or reset")

def correct():
    """
    re-set current state response.
    :return: None
    """
    response = input("Enter Correct response:")
    RESPONSEOPTIONS[0].updateStateResponse(response)
    writeState(RESPONSEOPTIONS[0])

def main():
    global CurrentState
    global CurrentInput
    global RESPONSEOPTIONS
    global TempMemory
    CurrentState = getState(0)
    print("-------Agent Running-------")
    if CurrentState == None:
        print("<<<Error>>>> Empty DB")
        quit()
    while True:
        try:
            print("<<<",CurrentState.response)
            if "Null" not in CurrentState.special and CurrentInput != None:
                executeSpecial(CurrentState.special,CurrentInput,TempMemory)
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
        except Exception as e:
            if LEARNINGMODE:
               print("<<<Error: Main crashed >_< >>>",e)
            else:
                print("Ohh boy, I am not feeling so well, lets try again")
                CurrentState = getState(0)


if __name__ == "__main__":
    main()