from StateType import *
from StateFunctions import *

FILEPATH = r"./StatesDB.txt"
CurrentState = None #StateType
CurrentInput = None #[word1,word2,word3]
ResponseOptions = None #[state123,state34...] ordered
LEARNINGMODE = True

def main():
    print("-------Agent Running-------")
    setState(0)
    while True:
        print(CurrentState.response)
        parseInput(input(">>> ")) #result updates CURRENTINPUT
        RESPONSEOPTIONS = sortStates(CurrentInput) #list of stateType [state34,state21...]
        if LEARNINGMODE:
            command = ""
            while command != 'fix' or command != 'restart' or command != 'y':
                if RESPONSEOPTIONS == []: #no options
                    print("I'm ClueLess...\n'fix' text, 'restart' or 'create' new state?")
                else:
                    print("Is this good? \n",RESPONSEOPTIONS[0].response)
                    print("<y>-yes,<n>-no/next,<r>-fix response")
                command = input(">>")
                if command == "create": #creates new state
                    response = input("Enter response:")
                    new_state = State(searchNextId())
                    new_state.updateStateIncoming(CurrentState.id)
                    new_state.updateStateResponse(response)
                    new_state.updateStateWords(CurrentInput)
                elif command == "restart":
                    setState(0)
                elif command == "y":
                    setState(RESPONSEOPTIONS[0].id)
                    RESPONSEOPTIONS[0].updateStateIncoming(CurrentState.id) #can you get result without incoming?
                    RESPONSEOPTIONS[0].updateStateWords(CurrentInput)
                elif command == "n":
                    RESPONSEOPTIONS.pop(0)
                elif command == "r":
                    response = input("Enter Correct response:")
                    RESPONSEOPTIONS[0].updateStateResponse(response)
                    print("response updated...")

        else:
            if RESPONSEOPTIONS == None:
                print("I am not sure what you mean")
                command = input("do you want to restart the conversation or rephrase?")
                if "restart" in command:
                    setState(0)
            else:
                print(RESPONSEOPTIONS[0].response)
                setState(RESPONSEOPTIONS[0].id)


if __name__ == "__main__":
    main()