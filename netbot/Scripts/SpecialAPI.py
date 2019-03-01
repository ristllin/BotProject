#------imported libraries--------
import wikipedia
import random
import datetime
import requests
#------imported modules--------
from scripts.BadDb import *

def executeSpecial(command,userInput,TempMemory):
    """
    gets String "<API>:<Command>:<data>" passes command to relevant api
    :param command:
    :return: None
    """
    response = ""
    parsed = command.split(":") #parsed = [API,COMMAND,DATA]
    if len(parsed) == 3:
        api = parsed[0]
        command = parsed[1]
        data = parsed[2]
        if "internet" in api:
            response = internet(command, data, userInput)
            # response = " OMG they cut me off the internet :( \nI can't answer that now"
        elif "random" in api:
            response = randoms(command, data, userInput)
        elif "time" in api:
            response = time(command,data,userInput)
        elif "memory" in api:
            response = memory(command,data,userInput,TempMemory)
    return response

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

def memory(command,data,userInput, TempMemory):
    """
    saving temporary data for conversation
    saving it on computer...?
    :return:
    """
    if command == "remember":
        tmpdata = input("what should I remember?")
        data_name = input("what is it? how do you want to call it?")
        TempMemory.append((data_name,tmpdata)) #allows double saves
    if command == "retrieve":
        data_name = input("what is it called?")
        for slot in TempMemory:
            if slot[0] == data_name:
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

def internet(command,data,userInput):
    """
    internet related commands
    :param command:
    :param data:
    :param userInput:
    :return:
    """
    if command == "search":
        return internetSearch(userInput)
    if command == "weather":
        return internetWeather(command,data,userInput)

def internetSearch(userInput):
    """
    parses user command, removes from it words in bad DB and searches it in wikipedia
    :param userInput:
    :return:
    """
    try:
        result = ""
        content = userInput.split(" ")
        tmp = content.copy()
        for word in badsearchDb:
            if word in content:
                tmp.remove(word)
        content = " ".join(tmp)
        result = "\n: "+content
        try:
            info = str(wikipedia.summary(content, sentences=5))
        except wikipedia.exceptions.DisambiguationError as e:
            return "... \nCan you please be less ambiguous?"
        except wikipedia.exceptions.PageError as e:
            return "... \n So I was checking on wikipedia, and their page crashed."
        result += "... \nFound: "+info[:200]
        return str(result)
    except Exception as e:
        return "Failed " + e  # interconnection problems e.g.?

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
        result = ""
        otherdays = {"tomorrow","week","sunday","monday","tuesday","wednesday","thursday","friday","saturday"}
        for time in otherdays:
            if time in userInput:
                result += "I can only tell the weather now..."
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
            return result + "with this weather, I'd go with "+decision
        else:
            return result + "Weather: " + str(general)+ "\nTemp: " + str(temp) + " deg C" + "\nPressure: " + str(pressure) + " Hg"+ "\nWind: "+ str(wind )+ " Kmh" + "\nHumidity: "+ str(humidity) + "%"
    except Exception as e:
        return "Failed " + e  # interconnection problems e.g.?

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
            return "heads"
        else:
            return "tails"
    elif command == "pass": #generates password
        try:
            length = 10
            if "length" in userInput:
                num = "0"
                for char in userInput:
                    if not (char.isalpha() or char == " "):
                        num += char
                return int(num)
                length = int(num)
            return str("".join([chr(random.randint(33,126)) for i in range(int(length))]))
        except Exception as e:
            return "Failed in process " + e