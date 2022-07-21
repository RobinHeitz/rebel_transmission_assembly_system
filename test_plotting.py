
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
                position=i, 
                millis = 2891283, 
                )
        )
    sorted_ = sorted(data)
    return [i.position for i in sorted_], [i.current for i in sorted_]



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




