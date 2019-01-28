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
        RESPONSEOPTIONS = sortStates(CurrentInput)
        if LEARNINGMODE:
            #while teacher isn't sattisfied:
                #no options
                    #Clueless -> fix? or create new state
                #no hits
                    #remodle state?
                    #next state?
                    #rewrite?
                #hits
                    #am i right?
                        #next?
                        #restart?
                        #rewrite?
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