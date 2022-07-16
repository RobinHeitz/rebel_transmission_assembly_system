import PySimpleGUI as sg
import numpy as np

def update():
    r = np.random.randint(1,100)
    text_elem = window['-text-']
    text_elem.update("This is a random integer: {}".format(r))

# Define the window's contents/ layout

layout = [
    [sg.Button("Generate", enable_events=True, key="-FUNCTION-", font="Helvetica 16")],
    [sg.Text("This is a random integer: ", size=(25,1), key="-text-", font="Helvetica 16")]
    ]

# Create window
window = sg.Window("Generate random integers", layout, size=(800,500))

# Event loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == "-FUNCTION-":
        update()
window.close()