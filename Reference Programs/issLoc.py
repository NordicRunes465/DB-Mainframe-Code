import requests
import json
from geopy.geocoders import Nominatim
import PySimpleGUI as sg
from time import sleep
from playsound import playsound
import logging

logging.basicConfig(filename='ISSLog', format='%(asctime)s - %(message)s', level=logging.WARNING)

# API key and base address for reverse geocoding

def getCountryName(countryCode):
    nameUrl = f"http://www.geognos.com/api/en/countries/info/{countryCode}.json"
    response = requests.get(nameUrl)
    responseString = response.content.decode('utf-8')
    responseDict = json.loads(responseString)
    fullName = responseDict['Results']['Name']
    return fullName


def getisslocation():
    # Base url for iss location and the call
    issBase = "http://api.open-notify.org/"
    call = "iss-now.json"
    #Let's get the ISS location
    getLocation = issBase + call
    response = requests.get(getLocation)
    locString = response.content.decode('utf-8')
    locDict = json.loads(locString)
    longitude = locDict['iss_position']['longitude']
    latitude = locDict['iss_position']['latitude']
    return latitude, longitude

def getplaceonearth(latitude, longitude):
    # Using Longitude and Latitude Get the location
    weatherAPIKey = "86a92c2efb9281610d50cc115f91ac95"
    wBase = "http://api.openweathermap.org/geo/1.0/reverse?"
    wCall = f"lat={latitude}&lon={longitude}&limit=1&appid={weatherAPIKey}"
    getPlaceCall = wBase + wCall
    placeOnEarth = requests.get(getPlaceCall)
    placeString = placeOnEarth.content.decode('utf-8')
    placeDict = json.loads(placeString)
    if len(placeDict) == 0:
        return None, None, None


    city = placeDict[0]['name']
    country = placeDict[0]['country']
    cName = getCountryName(country)
    logging.warning(f"A place was found, {city} located in {cName}")
    #playsound('ding.mp3')
    return city, country, cName

def getOceanName(latitude, longitude):
    oBase = "http://api.geonames.org/extendedFindNearbyJSON?"
    oCall = f"lat={latitude}&lng={longitude}&username=robert.w.ball"
    oceanCall = oBase + oCall
    oName = requests.get(oceanCall)
    return oName


#Set up the fLayout
layout = [[sg.Text('Where is the ISS??', justification= 'center', relief='flat', size=(30, 1))],
          [sg.Text('Latitude:   '), sg.InputText("",enable_events=False,size=(20,1),readonly=True,key='lat')],
          [sg.Text('Longitude: '), sg.InputText("",enable_events=False,size=(20,1),readonly=True,key='lon')],
          [sg.Multiline("", enable_events=False,size=(40,4) ,key='results')],
          [sg.Button('Refresh', enable_events=True, bind_return_key=True, key='refresh'),
            sg.Text('Count Down to next check: '),
            sg.InputText("",enable_events=False, size=(8, 1), key='countdown')],
          [sg.StatusBar("",key='-status-')]]


window = sg.Window('ISS Watcher!!', layout, resizable=True,finalize=True, alpha_channel=1, grab_anywhere=True)
timeToCheck = True
secondCount = 0
#playsound('ding.mp3')
logging.warning('Program Started...')
window['-status-'].update("This is my status bar")
while True:
    if timeToCheck:
        lat, lon = getisslocation()
        city, country, fcountry = getplaceonearth(lat, lon)
        window['lat'].update(lat)
        window['lon'].update(lon)
        if city is None:
            oceanName = getOceanName(lat,lon)
            window['results'].update(f"The ISS is currently over an ocean!!")
        else:
            message = f"The ISS is currently over {city} in {fcountry}"
            window['results'].update(message)
        timeToCheck = False
        secondCount = 0

    event, values = window.read(timeout=1000,timeout_key='__TIMEOUT__',close=False)
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'refresh':
        timeToCheck = True
        secondCount = 0
    elif event == '__TIMEOUT__':
        sleep(1)
        secondCount += 1
        timeLeft = (300 - secondCount) / 60
        countDown = round(timeLeft,2)
        window['countdown'].update(countDown)

    if secondCount > 300:
        timeToCheck = True


window.close()


