#------imported libraries--------
import wolframalpha
import wikipedia
import random
import datetime
import requests
import re
#------imported modules--------
from BadDb import *

def executeSpecial(command,userInput,TempMemory,RawInput):
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
            internet(command, data, userInput,RawInput)
        elif "random" in api:
            randoms(command, data, userInput)
        elif "time" in api:
            time(command,data,userInput)
        elif "memory" in api:
            memory(command,data,userInput,TempMemory)

def time(command,data,userInput):
    """
    Time related commands
    :param command:
    :param data:
    :param userInput:
    :return:
    """
    if command == "time":
        print(str(datetime.datetime.now()))

def memory(command,data,userInput,TempMemory):
    """
    saving temporary data for conversation
    saving it on computer...?
    :return:
    """
    if command == "remember":
        tmpdata = input("say it: ")
        data_name = data
        TempMemory.append((data_name,tmpdata)) #allows double saves
    if command == "retrieve":
        for slot in TempMemory:
            if slot[0] == data:
                print(slot[1])
                break
    if command == "getName":
        for slot in TempMemory:
            if slot[0] == "name":
                return slot[1]
    if command == "setName":
        for slot in TempMemory:
            if slot[0] == "name":
                slot[1] = userInput

def internet(command,data,userInput,RawInput):
    """
    internet related commands
    :param command:
    :param data:
    :param userInput:
    :return:
    """
    if command == "search": #wikipedia
        if data == "multiple":
            multiSearch(RawInput)
        else:
            internetSearch(userInput)
    if command == "weather": #weather status
        internetWeather(command,data,userInput)
    if command == "wolfram": #gets raw user input
        internetWolfram(RawInput)


def internetSearch(userInput):
    """
    parses user command, removes from it words in bad DB and searches it in wikipedia
    :param userInput:
    :return:
    """
    try:
        content = userInput.split(" ")
        tmp = content.copy()
        for word in badsearchDb:
            if word in content:
                tmp.remove(word)
        content = " ".join(tmp)
        print("searching: ",content)
        info = wikipedia.summary(content, sentences=5)
        print(info[:200])
    except Exception as e:
        print("Failed ", e)  # interconnection problems e.g.?

def multiSearch(userInput):
    """
    parses user command, removes from raw input words in bad DB, splits it into sub terms and searches it in wikipedia
    :param userInput:
    :return:
    """
    try:
        content = userInput.split(" ")
        tmp = content.copy()
        for bad_word in badsearchDb:
            for word in content:
                clean_word = re.sub(r'\W+', '', word) #remove all non alpha-numeric
                if ("," not in word) and (bad_word == clean_word) and (word in tmp):
                    tmp.remove(word)
                    break
        content = " ".join(tmp)
        content = content.replace(" ","").split(",")
        print("searching for:",content)
        for word in content:
            try:
                info = wikipedia.summary(word, sentences=5)
                print(word+": ",info[:200] )
            except Exception as er:
                print("couldn't work out:", word)
    except Exception as e:
        print("Failed ", e)  # interconnection problems e.g.?

def internetWeather(command,special_data,userInput):
    """
    searches Weather data and gives wear recommendations
    :param command:
    :param special_data:
    :param userInput:
    :return:
    """
        # openweatherapi key - 47c0157cd7e7c5cf1f19a97abc04edbc
    try:
        otherdays = {"tomorrow","week","sunday","monday","tuesday","wednesday","thursday","friday","saturday"}
        for time in otherdays:
            if time in userInput:
                print("I can only tell the weather now...")
        weather_data = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Israel&APPID=47c0157cd7e7c5cf1f19a97abc04edbc').json()
        temp = str(weather_data["main"]['temp'] - 273.15)
        pressure = str(weather_data["main"]['temp'])
        general = str(weather_data["weather"][0]['description'])
        wind = str(weather_data["wind"]['speed'])
        humidity = str(weather_data["main"]['humidity'])
        if "wear" in special_data:
            clothing = [(-50,0,"something very warm"),(1,14,"something warm"),(15,19,"a sweatshirt"),(20,24,"something light"),(25,100,"something short")]
            decision = clothing[0][1]
            for cloth in clothing:
                if cloth[0]<=int(float(temp)) and cloth[1]>=int(float(temp)):
                    decision = cloth[2]
                    break
            if int(float(temp)) < 15 and int(float(humidity)) > 90:
                decision += " and take an umbrella."
            print("with this weather, I'd go with "+decision)
        else:
            print("Weather: ", general, "\nTemp: ", temp + " deg C", "\nPressure: ", pressure + " Hg", "\nWind: ",wind + " Kmh", "\nHumidity: ", humidity + "%")
    except Exception as e:
        print("Failed ", e)  # interconnection problems e.g.?

def internetWolfram(userInput):
    """
    Gets raw user input, transfers to wolframAlpha
    :param userInput: String (with signs)
    :return: String
    """
    try:
        client = wolframalpha.Client("2TYLUH-6Q2KRKXA2U")
        res = client.query(userInput)
        res = res["pod"][1]["subpod"]["plaintext"]
        print(res)
        return str(res)
    except Exception as e:
        return "Hmm.. seems my friend is having trouble helping me with this answer..." + str(e)

def randoms(command,data,userInput):
    """
    random related commands
    :param command:
    :param data:
    :param userInput:
    :return:
    """
    if command == "coin":
        toss = random.randint(0, 1)
        if toss == 0:
            print("heads")
        else:
            print("tails")
    elif command == "pass": #generates password
        try:
            length = 10
            if "length" in userInput:
                num = "0"
                for char in userInput:
                    if not (char.isalpha() or char == " "):
                        num += char
                print(int(num))
                length = int(num)
            print("".join([chr(random.randint(33,126)) for i in range(int(length))]))
        except Exception as e:
            print("Failed in process ",e)