from typing import Union, List, Set
import PySimpleGUI as psg
from enum import Enum

class GUIEvent(Enum):
    CLOSE = 1
    DISPLAY = 2
    QUERY = 3


class OutputGUI:
    def __init__(self):
        self.layout = [[psg.Text('Enter the query'), psg.InputText()],
                       [psg.Button('Ok'), psg.Button('Cancel'), psg.Button('Display')],
                       [psg.Listbox([], size=(50, 20)),
                        psg.Multiline(size=(51, 21), disabled=True)]]

        self.window = psg.Window('Search Webpages', self.layout, location=(40, 40),
                                 return_keyboard_events=True)

    def get_gui_event(self):
        while True:
            event, values = self.window.read()
            if event == psg.WIN_CLOSED or event == 'Cancel' or event == 'Escape:27':
                return GUIEvent.CLOSE, []
            if event != 'Ok' and event != '\r' and event != 'Display':
                continue
            if event == 'Display':
                return GUIEvent.DISPLAY, []
            break
        query = values[0].split(' ')  # Split based on spaces
        query = [q.lower() for q in query]  # Convert to lower case
        return GUIEvent.QUERY, query

    def set_results(self, results: Union[List[str], Set[str]]):
        self.layout[2][0].Update(values=results)
