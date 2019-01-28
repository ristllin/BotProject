from StateFunctions import *
from Main import *

class State():
    """
    states are not added to DB automatically! must use writeState to add, and also use it after updates.
    """
    def __init__(self,id,incomingStates={0},response="Undefined",words={},origin=""):
        self.id = id #int
        self.words = words #{"word1":#Hits,"word2":#Hits,...,"wordN":#Hits}
        self.incomingStates = incomingStates #{12,134,86}
        self.origin = origin #original sentance that created this state "get me the password to 34"
        self.response = response #"this is the message you should respond"

    def __repr__(self):
        return "ID: "+str(self.id)+"; Response: "+self.response+"\n; Origin Sentance:"+self.origin

    def printFullState(self):
        print("ID: "+str(self.id)+"; Response: "+self.response+"\n; Origin Sentance:"+self.origin+";\n Words:"+str(self.words)+"\n Incoming State:"+str(self.incomingStates))

    def updateStateResponse(self,response):
        print("response changed from: ",self.response," to:",response)
        self.response = response

    def updateStateIncoming(self,state_id):
        print("added ",state_id," to: ",self.id)
        self.incomingStates.add(state_id)

    def updateStateWords(self,words):
        print("adding words")
        for word in words:
            if self.words.get(word) != None: #word exists
                self.words[word] += 1
            else: #create new key
                self.words[word] = 1
