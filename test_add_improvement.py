import PySimpleGUI as sg
from gui.add_improvement import add_improvement
from gui.shaded_overlay import shaded_overlay

def main():
    sg.theme("DarkTeal10")

    shaded_overlay(top_window = add_improvement.add_improvement_window)



if __name__ == "__main__":
    main()