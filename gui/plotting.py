import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import logging 

class GraphPlotter:
    fig_agg = None
    lines = None
    line = None

    def __init__(self, canvas) -> None:
        self.canvas = canvas
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_autoscaley_on(True)


    def plot_data(self, data_x, data_y):
        logging.warning("*"*10)
        logging.warning("plot_data():")
        logging.warning("*"*10)
        
        def _plot(data_x, data_y):
            self.line.set_xdata(data_x)
            self.line.set_ydata(data_y)
            self.ax.relim()
            self.ax.autoscale_view()
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()
        
        if not self.line:
            self.line, = self.ax.plot(data_x, data_y, "r-")
            _plot(data_x, data_y)
            self.__draw_figure_in_canvas()
        else:
            _plot(data_x, data_y)
        
    
    def __draw_figure_in_canvas(self):
        if self.fig_agg is not None: self.fig_agg.get_tk_widget().forget()
        self.fig_agg = FigureCanvasTkAgg(self.figure, self.canvas.TKCanvas)
        self.fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.fig_agg.draw()

