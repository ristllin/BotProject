FILEPATH = r"./StatesDB.txt"
LEARNINGMODE = True #Main operating mode
STRONGMODE = False #Every sentence taught is repeated until it is first result in score for given input
DEBUG = True
HITSCONST = 4  # Factor in scoring algo, how many points each hit worths
RELATIONCONST = 3  # connection exists between nodes
SCORECONST = 1  # adding up matching words weight
MAXENHANCMENTITER = 3 # maximum amount of iterations to improve a sentence