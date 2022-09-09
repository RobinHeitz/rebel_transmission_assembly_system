import PySimpleGUI as sg
sg.theme("DarkTeal10")



font_headline = "Helvetiva 25"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"


layout = [
    [sg.Text("Fehler hinzufügen:", font=font_headline, background_color=sg.theme_background_color())],
    [sg.HorizontalSeparator()],

    [sg.Text("Beschreibung", font=font_normal)],
    [sg.Multiline(size=(None, 5))],

    [sg.Text("Montageschritt", font=font_normal)],
    [sg.Combo(["Val1", "Val2", "Val3"], expand_x=True, font=font_normal, readonly=True)],



    [sg.VPush()],

    [
        sg.Button("Abbrechen", button_color="red", size=(10,1), font=font_normal),
        sg.Push(),
        sg.Button("Speichern", button_color=sg.GREENS[3], size=(10,1), font=font_normal),
    ]
]