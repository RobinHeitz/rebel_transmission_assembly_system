import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from logs.setup_logger import setup_logger
import logging


class GraphPlotter:
    fig_agg = None
    lines = None
    line = None

    limit_line = None
    logger = setup_logger("plotting", logging.DEBUG)



    def __init__(self, canvas) -> None:
        self.canvas = canvas
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_autoscaley_on(True)

    def __plot(self, data_x, data_y, limit):
        self.logger.info(f"_plot()| limit: {limit}")
        self.line.set_xdata(data_x)
        self.line.set_ydata(data_y)
        # self.line.set_label("Label Test")
        # self.ax.legend()

        if limit != None and self.limit_line == None:
            if self.limit_line == None:
                self.limit_line = self.ax.axhline(y=limit, color="red", linestyle="dashed")
                self.logger.info(f"Numb of lines: {self.ax.lines}")

        elif limit == None and self.limit_line != None:
            self.limit_line.remove()
            del self.limit_line

        self.ax.set_title("Stromaufnahme eines Bewegungsablaufs")
        self.ax.set_ylabel("Strom [mA]")
        self.ax.set_xlabel("Zeitstempel")
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def plot_data(self, data_x, data_y, limit = None):
        self.logger.info(f"plot_data; limit = {limit}")

        if not self.line:
            self.line, = self.ax.plot(data_x, data_y, "r-", color="blue")
            self.__plot(data_x, data_y, limit)
            self.__draw_figure_in_canvas()
        else:
            self.__plot(data_x, data_y, limit)
        
    
    def __draw_figure_in_canvas(self):
        if self.fig_agg is not None: self.fig_agg.get_tk_widget().forget()
        self.fig_agg = FigureCanvasTkAgg(self.figure, self.canvas.TKCanvas)
        self.fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.fig_agg.draw()

