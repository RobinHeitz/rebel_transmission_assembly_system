import PySimpleGUI as sg

layout = [

    [sg.Text("Test")],
    [sg.Text("Test2")],
]

if __name__ == "__main__":
    window = sg.Window("Testing plotting", layout, size=(800,500))

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

  
  
    

    window.close()