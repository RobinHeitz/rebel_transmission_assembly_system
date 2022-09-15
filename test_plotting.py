
from hw_interface.definitions import MessageMovementCommandReply

from gui.plotting import GraphPlotter

import PySimpleGUI as sg

from random import random, randint

import threading, time

layout = [
    [sg.Canvas(size=(400,400), k="canvas")],
]



def get_data():
    print("get_data")
    data = []
    for i in range(randint(250,500)):
        data.append(
            MessageMovementCommandReply(
                current = random() *200+100, 
                position=1000.5 +i, 
                tics = 50000 + 1031.111*i,
                millis = 2891283, 
                )
        )
    sorted_ = sorted(data)
    return [i.tics for i in sorted_],[i.current for i in sorted_]
 

def update_graph_thread(window:sg.Window):
    while True:
        time.sleep(2)
        x, y = get_data()
        window.write_event_value("UPDATE", dict(x=x, y=y))
        
def update_graph(event, values):
    
    d = values[event]
    x, y = d.get('x'), d.get('y')
    print("update graph", "x = ", len(x))
    graph_plotter.plot_data(x, y)

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




