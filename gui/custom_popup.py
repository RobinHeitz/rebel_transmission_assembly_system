import PySimpleGUI as sg
from typing import List, Tuple

font_headline = "Helvetiva 25"
font_headline_2 = "Helvetiva 17"
font_normal = "Helvetica 15"
font_small = "Helvetica 13"

sg.theme("DarkTeal10")


def popup_yes_no(title:str, message:str, **kwargs):
    """Shows modal window. Returns 'yes' or 'no' based on users btn interaction.
    
    Params: 
    - title (str): Title of popup.
    - message (str): Popup message.
    - error (bool, default = False): Red coloring of headline and buttons.
    - warning (bool, default = False): Yellow coloring of headline and buttons.
    """
   
    buttons = [("Ja", "yes"),("Nein", "no")]
    return __popup(title, message, buttons, **kwargs)


def popup_ok(title:str, message: str, **kwargs):
    btn_row = [("OK", "ok")]
    return __popup(title, message, btn_row, **kwargs)


def __popup(title:str, message: str, buttons:List[Tuple[str, str]], **kwargs) -> str:
    
    def __btns_layout(btn_row):
        btn_layout = [sg.Push()]
        for b_text, b_key in btn_row:
            btn_layout.append(
                sg.B(b_text, k=b_key, **btn_params)
            )
            btn_layout.append(sg.Push())
        return btn_layout
    
    btn_params = dict(
        size = (10,1),
        font=font_normal
    )
    
    title_params = dict(
        font=font_headline_2,
    )

    multi_line_params = dict(
        font=font_normal, 
        expand_x = True, 
        expand_y = True, 
        write_only = True, 
        horizontal_scroll = False, 
        no_scrollbar = True, 
        enable_events = False, 
        enter_submits = False,
        disabled = True,
    )
    if kwargs.get("warning", False):
        title_params["text_color"] = sg.YELLOWS[0]
        btn_params["button_color"] = ("#000000", sg.YELLOWS[0])
    
    elif kwargs.get("error", False):
        title_params["text_color"] = "#e01212"
        btn_params["button_color"] = ("#ffffff", "#e01212")

    layout = [
        [sg.Text(title, **title_params)],
        [sg.Multiline(message, **multi_line_params,)],
        __btns_layout(buttons),
    ]   

    window = sg.Window(title, layout, use_default_focus=False, finalize=True, modal=True, size=(350, 200), no_titlebar=True)
    event, values = window.read()
    window.close()
    return event





if __name__ == "__main__":
    title = "Keinen Fehler erkannt"
    description = "Die Messung ist in Ordnung, es wurde kein Fehler erkannt. Ist dir sonst noch ein Fehler aufgefallen?"
    answer = popup_yes_no(title, description, warning=True)
    print(answer)

    title = "Keine Behebungsmaßnahmen"
    message = "Es gibt aktuell keine weiteren Behebungsmaßnahmen. Wenn du den Fehler beheben kannst, füge die Maßnahme bitte hinzu."
    popup_ok(title, message, error=True)
