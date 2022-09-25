import PySimpleGUI as sg

sg.theme("DarkTeal10")



class Fails:
    def __init__(self, name, imps):
        self.name = name
        self.imps = imps

    def __str__(self):
        return f"Fehler {self.name}"

def main():
    ...
    
    f1 = Fails("1", ["Behebung #1 zu Fehler 1","Behebung #2 zu Fehler 1","Behebung #3 zu Fehler 1"])
    f2 = Fails("2", ["Behebung #1 zu Fehler 2","Behebung #2 zu Fehler 2",])
    f3 = Fails("3", ["Behebung #1 zu Fehler 3","Behebung #2 zu Fehler 3","Behebung #3 zu Fehler 3"])
    f4 = Fails("4", ["Behebung #1 zu Fehler 4","Behebung #2 zu Fehler 4"])
    
    values = [f1, f2, f3, f4]

    layout = [
        [sg.Combo(values, default_value=values[0], size=(20,5), font="Helvetica 15", enable_events=True, k="-COMBO-")],
        [
            sg.Listbox(f1.imps, k="-LIST-",default_values=[], size=(20,5), font="Helvetica 15")
        ],
    ]

    window = sg.Window("Combobox", layout, size=(300,300), finalize=True, location=(0,0),resizable=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        
        elif event == "-COMBO-":
            ...
            sel_fail = values[event]
            list_box = window["-LIST-"]
            list_box.update(sel_fail.imps,)

        



if __name__ == "__main__":
    main()