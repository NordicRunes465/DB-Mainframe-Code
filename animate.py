import background_shuffler
import Variables as V
import PySimpleGUI as sg
import time

'''what we can do is with the GUI... each time a button is hit, change the variable to the specified
background, then re run the background_shuffler at a decent time. We can also hid the channel once a button is hit, then possibly make the fLayout reappear
for a couple seconds... just in case the user wishes to change the background again'''


layout = [[sg.Button('Summer', key='Summer', size=(10,1)),
                     sg.Button('Campfire', key='Campfire', size=(10,1))],
          [sg.Button('nighttime', key='Night', size=(10,1))],
          [sg.Button('Confirm', key='Confirm', size=(10,1))]]

window = sg.Window('Background Changer', layout, resizable=False, finalize=True, grab_anywhere=True, size = (300,200))

running = True
while True:
    event, values = window.read(timeout=1000, timeout_key='__TIMEOUT__',close=False)
    if event == sg.WINDOW_CLOSED:
        break

    elif event == 'Summer':
        V.number = 1
    elif event == 'Campfire':
        V.number = 2
    elif event == 'nighttime':
        V.number = 3
    elif event == 'Confirm':
        background_shuffler.shuffle(.13)
        sg.window.alpha_channel = 1

window.close()
