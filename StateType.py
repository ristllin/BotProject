#from StateFunctions import *
from constants import *
from BadDb import *


class State:
    #states are not added to DB automatically! must use writeState to add, and also use it after updates.
    def __init__(self,id,incomingStates={0},response="Undefined",words={},origin="",special="Null"):
        self.id = id #int
        self.words = words #{"word1":#Hits,"word2":#Hits,...,"wordN":#Hits}
        self.incomingStates = incomingStates #{12,134,86}
        self.origin = origin #original sentance that created this state "get me the password to 34"
        self.response = response #"this is the message you should respond"
        self.special = special #<api name>:<command>:<data>

    def __repr__(self):
        return "ID: "+str(self.id)+"; Response: "+self.response+"; Origin Sentance:"+self.origin+" special: "+self.special

    def printFullState(self):
        print("ID: "+str(self.id)+"; Response: "+self.response+"; Origin Sentance:"+self.origin+";\n Words:"+str(self.words)+"\n Incoming State:"+str(self.incomingStates))+"\n Special:"+str(self.special)

    def updateStateResponse(self,response):
        # print("response changed from: ",self.response," to:",response)
        self.response = response

    def updateStateIncoming(self,state_id):
        # print("added or updated incoming state:",state_id," to state: ",self.id)
        self.incomingStates.add(state_id)

    def updateStateSpecial(self,special):
        # print("added or updated incoming state:",state_id," to state: ",self.id)
        self.special = special

    def updateStateWords(self,words):
        words = words.split(" ")
        for word in words:
            word.replace(" ","")
        if "" in words:
            words.remove("")
        # print("new words: ", words)  # debug
        for word in words:
            if self.words.get(word) != None: #word exists
                if word not in limited:
                    self.words[word] += 1
                elif self.words[word] < limited[word]:
                    self.words[word] += 1
            else: #create new key
                self.words[word] = 1