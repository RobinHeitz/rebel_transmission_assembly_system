import PySimpleGUI as sg
from gui.add_failure import add_failure
from gui.add_improvement import add_improvement
from gui import shaded_overlay

def main():
    sg.theme("DarkTeal10")

    shaded_overlay.shaded_overlay(top_window = add_failure.add_failure_window)


    # add_failure.add_failure_window()



if __name__ == "__main__":
    main()