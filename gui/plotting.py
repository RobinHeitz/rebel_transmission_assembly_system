import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import time, threading

min_x = 0
max_x = 360

class GraphPlotter:
    fig_agg = None
    lines = None

    def __init__(self, canvas) -> None:
        self.canvas = canvas
        self.figure = plt.figure()

    
    def plot_data(self, data_x, data_y):

        if self.lines:
            line = self.lines.pop(0)
            line.remove()


        self.lines = plt.plot(data_x, data_y)
        self.draw_figure_in_canvas()
    
    def draw_figure_in_canvas(self):
        if self.fig_agg is not None: self.fig_agg.get_tk_widget().forget()
        self.fig_agg = FigureCanvasTkAgg(self.figure, self.canvas.TKCanvas)
        self.fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.fig_agg.draw()

