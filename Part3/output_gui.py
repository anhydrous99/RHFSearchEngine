from typing import Union, List, Set
import PySimpleGUI as GUI_Interface


class OutputGUI:
    def __init__(self):
        self.layout = [[GUI_Interface.Text('Enter the query'), GUI_Interface.InputText()],
                       [GUI_Interface.Button('Ok'), GUI_Interface.Button('Cancel')],
                       [GUI_Interface.Multiline(size=(30, 30)),
                        GUI_Interface.Multiline(size=(30, 30))]]

        self.window = GUI_Interface.Window('Search Webpages', self.layout, location=(40, 40), size=(500, 500),
                                           return_keyboard_events=True)

    def get_query(self):
        event, values = self.window.read()
        if event == GUI_Interface.WIN_CLOSED or event == 'Cancel' or event == 'Escape:27':
            return 'break'
        if event != 'Ok' and event != '\r':
            return 'do_nothing'
        query = values[0].split(' ')  # Split based on spaces
        query = [q.lower() for q in query]  # Convert to lower case
        return query

    def set_results(self, results: Union[List[str], Set[str]]):
        pass  # Put search results here
