
from hw_interface.definitions import MessageMovementCommandReply

from gui.plotting import GraphPlotter

import PySimpleGUI as sg

from random import random

import threading, time

layout = [
    [sg.Canvas(size=(400,400), k="canvas")],
    [sg.Button("Test")]
]



def get_data():

    data = []
    for i in range(350):
        data.append(
            MessageMovementCommandReply(
                current = random() *200+100, 
                position=1000.5 +i, 
                millis = 2891283, 
                )
        )
    sorted_ = sorted(data)
    # return [i.position for i in sorted_], [i.current for i in sorted_]
    x = [1069.4705818965517, 1069.6344827586206, 1069.860452586207, 1070.0650862068965, 1070.278448275862, 1070.49375, 1070.704202586207, 1070.9214439655173, 1071.140625, 1071.3501077586207, 1071.557650862069, 1071.7603448275863, 1071.9717672413794, 1072.171551724138, 1072.3868534482758, 1072.6050646551723, 1072.8203663793104, 1073.0259698275863, 1073.2335129310345, 1073.4691810344827, 1073.667025862069, 1073.8852370689656, 1074.0956896551725, 1074.3080818965518, 1074.5321120689655, 1074.750323275862, 1074.9627155172413, 1075.181896551724, 1075.3681034482759, 1075.579525862069, 1075.7977370689655, 1076.0033405172414, 1076.2196120689655]
    y = [0, 445, 445, 445, 445, 445, 445, 356, 356, 267, 267, 356, 356, 356, 356, 356, 356, 356, 356, 356, 445, 445, 445, 445, 356, 356, 356, 267, 356, 356, 356, 356, 356]
    return x, y


def update_graph_thread(window:sg.Window):
    while True:
        time.sleep(.5)
        x, y = get_data()
        window.write_event_value("UPDATE", dict(x=x, y=y))
        
def update_graph(event, values):
    d = values[event]
    x, y = d.get('x'), d.get('y')
    global graph_plotter
    graph_plotter.plot_data(x, y)
    # graph_plotter.plot_update(x,y)

if __name__ == "__main__":


    window = sg.Window("Testing Stuff.", layout, size=(800,800), finalize=True)
    
    x_data, y_data = get_data()

    graph_plotter = GraphPlotter(window["canvas"])
    graph_plotter.plot_data(x_data, y_data)

    threading.Thread(target=update_graph_thread, args=(window,), daemon=True).start()

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        
        if event == "UPDATE":
            update_graph(event, values)

       
       
    window.close()




