from StateType import *
from StateFunctions import *
from constants import *
CurrentState = None #StateType
CurrentInput = None
ResponseOptions = [] #[state123,state34...] ordered

def main():
    global CurrentState
    global CurrentInput
    CurrentState = getState(0)
    print("-------Agent Running-------")
    if CurrentState == None:
        print("<<<Error>>>> Empty DB")
        quit()
    while True:
        try:
            print("<<<",CurrentState.response)
            CurrentInput = parseInput(input(">>> ")) #result updates CURRENTINPUT
            RESPONSEOPTIONS = sortStates(CurrentInput) #list of stateType [state34,state21...]
            if LEARNINGMODE:
                command = ""
                while command != 'fix' or command != 'restart' or command != 'y':
                    if RESPONSEOPTIONS == []: #no options
                        print("I'm ClueLess...\n'fix' text, 'restart', 'connect #' to add a known state or 'create' new state?")
                    else:
                        print("<<<",RESPONSEOPTIONS[0].response,"\nIs State: ",RESPONSEOPTIONS[0].id," good?")
                        print("<y>-yes,<n>-no/next,<r>-fix response,'create'-create new state, 'connect #' to add a known state")
                    command = input(">>")
                    if command == "create": #creates new state
                        response = input("Enter response:")
                        new_state = State(searchNextId(),origin=CurrentInput)
                        new_state.updateStateIncoming(CurrentState.id)
                        new_state.updateStateResponse(response)
                        new_state.updateStateWords(CurrentInput)
                        writeState(new_state)
                        print("I'm smarter now, try me again.")
                        break
                    elif command == "restart":
                        CurrentState = getState(0)
                        break
                    elif command == "y" and RESPONSEOPTIONS != []:
                        state = RESPONSEOPTIONS[0]
                        state.updateStateIncoming(CurrentState.id) #can you get result without incoming?
                        state.updateStateWords(CurrentInput)
                        writeState(state)
                        CurrentState = getState(state.id)
                        break
                    elif command == "n":
                        # print("debug: ",RESPONSEOPTIONS)
                        if RESPONSEOPTIONS != []:
                            RESPONSEOPTIONS.pop(0)
                        else:
                            print("Debug: Ran of of options")
                        # print("debug: after: ", RESPONSEOPTIONS)
                    elif command == "r":
                        response = input("Enter Correct response:")
                        RESPONSEOPTIONS[0].updateStateResponse(response)
                        writeState(RESPONSEOPTIONS[0])
                    elif "connect" in command:
                        stateNum = ""
                        for ltr in command:
                            if ltr.isnumeric():
                                stateNum += ltr
                        if RESPONSEOPTIONS != []:
                            RESPONSEOPTIONS[0] = getState(int(stateNum))
                        else:
                            RESPONSEOPTIONS.append(getState(int(stateNum)))
                    elif command == "full debug":
                        print("___________________________")
                        print("Current State: ",CurrentState)
                        print("Current Input:",CurrentInput)
                        print("Response Options: ",RESPONSEOPTIONS)
                        print("___________________________")
                    elif command == "debug":
                        print("___________________________")
                        for state in RESPONSEOPTIONS:
                            print(state.id+",", end="")
                        print("\n___________________________")
                    else:
                        print("---Unknown command---")

            else:
                if RESPONSEOPTIONS == None:
                    print("I am not sure what you mean")
                    command = input("do you want to restart the conversation or rephrase?")
                    if "restart" in command:
                        CurrentState = getState(0)
                else:
                    print(RESPONSEOPTIONS[0].response)
                    CurrentState = getState(RESPONSEOPTIONS[0].id)
        except Exception as e:
            print("<<<Error: Main crashed >_< >>>",e)
            quit()
            #print("Something went wrong, lets restart")


if __name__ == "__main__":
    main()