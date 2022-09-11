import PySimpleGUI as sg

# sg.main_get_debug_data()
print(sg.__version__)
print(sg.tclversion_detailed)

layout = [
    [
        sg.FileBrowse(
        "Bild auswählen",
        file_types=[("Bild-Dateien (PNG, JPG, etc.)", ".png", ".jpg"), ],
        enable_events=True,
        k="-FB-",
    ),
        sg.Image(size=(100, 100), k="-IMG-", visible=False),
    ]
]

window = sg.Window("Window title", layout, size=(500, 500), finalize=True)

while True:
    try:
        event, values = window.read()
    except KeyboardInterrupt:
        break

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    elif event == "-FB-":
        print("Image picker: ", values[event])

window.close()
