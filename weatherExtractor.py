# Tyler Pressens
# 9/8/22
# Afternoon

# Weather API Project.
# A program to tell you the weather.

import PySimpleGUI as sg
import datetime as dt
import requests, json


def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.12
    fahrenheit = celsius * (9 / 5) + 32
    return celsius, fahrenheit


BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "c189de86d43ce000e3861d001042d9e4"
CITY = "Harpers Ferry"

hasCity = True
sg.theme("DarkTeal9")

layout = [[sg.Text("Weather Extractor", size=(60, 1), justification="center")],
          [sg.Text("Written By: Tyler Pressens", size=(60, 1), justification='center')],
          [sg.Image(filename="images/bg.png", key="-IMAGE")],
          [sg.Text("City Selection", justification="center")],
          [sg.InputText(key="citySelection", size=(30, 1), disabled=False)],
          [sg.Button("Search City", key="OK")], [sg.Button("Quit")],
          [sg.Multiline(key="-CANVAS-", size=(60, 10))]]

window = sg.Window("Weather Program - Tyler Pressens", layout,
                   location=(0, 0),
                   finalize=True,
                   element_justification="center",
                   font="Helvetica 18")

while True:
    event, values = window.read()
    if event == "OK" or event == sg.WIN_CLOSED:
        CITY = values["citySelection"]
        url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY
        response = requests.get(url).json()
        print(response)
        if 'Nothing to geocode' in dict.values(response) or 'city not found' in dict.values(response):
            window["-CANVAS-"].update("Invalid City", text_color='red', justification='center')
            CITY = "New York"
            print(CITY)
            hasCity = False

        else:
            hasCity = True

        if hasCity:
            window["-CANVAS-"].update(text_color='black', justification='center')
            temp_kelvin = response['main']['temp']
            temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
            feels_like_kelvin = response['main']['feels_like']
            feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)
            humidity = response['main']['humidity']
            wind_speed = response['wind']['speed']
            description = response['weather'][0]['description']
            sunrise_time = dt.datetime.utcfromtimestamp(response['sys']['sunrise'] + response['timezone'])
            sunset_time = dt.datetime.utcfromtimestamp(response['sys']['sunset'] + response['timezone'])

            window["-CANVAS-"].update(f"City: {CITY}\nTemperature: {temp_fahrenheit}F / {temp_celsius}C\n"
                                      f"Feels Like: {feels_like_fahrenheit}F / {feels_like_celsius}C\n"
                                      f"Humidity: {humidity}\n"
                                      f"Wind Speed: {wind_speed}\nSun Rises at: {sunrise_time} local time.\n"
                                      f"Sun Sets at {sunset_time} local time.\nWeather Report: {description}")
        else:
            window["-CANVAS-"].update("Invalid City")
    if event == "Quit" or event == sg.WIN_CLOSED:
        break

window.close()
