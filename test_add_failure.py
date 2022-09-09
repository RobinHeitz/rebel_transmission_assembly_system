import PySimpleGUI as sg
from gui.add_failure import add_failure
from gui.add_improvement import add_improvement

def main():
    sg.theme("DarkTeal10")
    # add_failure.add_failure_window()
    add_improvement.add_improvement_window()



if __name__ == "__main__":
    main()