import numpy as np
import time
import matplotlib.pyplot as plt
from random import random

plt.ion()

class DynamicUpdate():
    #Suppose we know the x range
    min_x = 0
    max_x = 10

    def __init__(self) -> None:
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], 'o')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(self.min_x, self.max_x)
        #Other stuff
        self.ax.grid()

    def update_graph(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def __call__(self):
        xdata = []
        ydata = []
        for x in np.arange(0,10,0.5):
            xdata.append(x)
            ydata.append(np.exp(-x**2)+10*np.exp(-(x-7)**2))
            self.update_graph(xdata, ydata)
            time.sleep(1)
        return xdata, ydata


if __name__ == "__main__":
    d = DynamicUpdate()
    # d()

    x_data = []
    y_data = []
    x_val = 0

    while True:
        x_data.append(x_val)
        y_data.append((random()+1)*500)
        x_val += 1
        d.update_graph(x_data, y_data)
        time.sleep(1)


    



    

