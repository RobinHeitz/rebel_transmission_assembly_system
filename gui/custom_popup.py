import PySimpleGUI as sg
from typing import List, Tuple, Optional

from gui.gui_helpers import Colors, BtnColors, Fonts

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
    return popup(title, message, buttons, **kwargs)


def popup_ok(title:str, message: str, **kwargs):
    btn_row = [("OK", "ok")]
    return popup(title, message, btn_row, **kwargs)


def popup(title:str, message: str, buttons:List[Tuple[str, str, Optional[str]]], **kwargs) -> str:
    
    def __btns_layout(btn_row):
        btn_layout = [sg.Push()]
        
        for b_text, b_key, *args in btn_row:
            params = {**btn_params}
            
            if "warning" in args:
                params["button_color"] = BtnColors.yellow
            elif "error" in args:
                params["button_color"] = BtnColors.red
            elif "green" in args:
                params["button_color"] = BtnColors.green
            
            btn_layout.append(
                sg.B(b_text, k=b_key, **params)
            )
            btn_layout.append(sg.Push())
        return btn_layout
    
    btn_params = dict(
        size = (10,1),
        font=Fonts.font_normal
    )
    
    title_params = dict(
        font=Fonts.font_headline_2,
    )

    multi_line_params = dict(
        font=Fonts.font_normal, 
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
        title_params["text_color"] = Colors.yellow
    
    elif kwargs.get("error", False):
        title_params["text_color"] = Colors.red

    layout = [
        [sg.Text(title, **title_params)],
        [sg.Multiline(message, **multi_line_params,)],
        __btns_layout(buttons),
    ]   

    window = sg.Window(title, layout, use_default_focus=False, finalize=True, modal=True, size=(330,220), no_titlebar=True)
    event, values = window.read()
    window.close()
    return event





if __name__ == "__main__":
    # title = "Weitere Fehler?"
    # description = "Die Messung ist in Ordnung, es wurde kein Fehler erkannt. Ist dir sonst noch ein Fehler aufgefallen?"
    # answer = popup_yes_no(title, description, warning=True)
    # print(answer)

    # title = "Keine Behebungsmaßnahmen"
    # message = "Es gibt aktuell keine weiteren Behebungsmaßnahmen. Wenn du den Fehler beheben kannst, füge die Maßnahme bitte hinzu."
    # popup_ok(title, message, error=True)

    title = "Test"
    message = "Es gibt keine weiteren Behebungsmaßnahmen, Getriebe ist Ausschuss. Wenn du den Fehler beheben kannst, füge die Maßnahme bitte hinzu."
    popup(title, message, [("Ja", "yes", "error"), ("Nein", "no", "green")])