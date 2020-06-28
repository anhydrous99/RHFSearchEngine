""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 4

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

File Details:
    The class in this file abstracts the GUI.
"""


from typing import Union, List, Set
import PySimpleGUI as psg
from enum import Enum
import collections

GUIReturn = collections.namedtuple('GUIReturn', ['gui_event', 'query'])


class GUIEvent(Enum):
    CLOSE = 1
    DISPLAY = 2
    QUERY = 3


class OutputGUI:
    def __init__(self):
        """
        Initiates the GUI
        """
        self.layout = [[psg.Text('Enter the query'), psg.InputText()],
                       [psg.Button('Ok'), psg.Button('Cancel'), psg.Button('Display'),
                        psg.Radio('Box 1', 1, default=True), psg.Radio('Box 2', 1)],
                       [psg.Listbox([], size=(50, 20), select_mode=psg.LISTBOX_SELECT_MODE_SINGLE),
                        psg.Listbox([], size=(50, 20), select_mode=psg.LISTBOX_SELECT_MODE_SINGLE),
                        psg.Multiline(size=(51, 21), disabled=True)]]

        self.window = psg.Window('Search Webpages', self.layout, location=(40, 40),
                                 return_keyboard_events=True)

    def get_gui_event(self) -> GUIReturn:
        """
        Gets the current GUI event.

        Returns:
            A GUIReturn item with the event and values for the query.
        """
        while True:
            event, values = self.window.read()
            if event == psg.WIN_CLOSED or event == 'Cancel' or event == 'Escape:27':
                return GUIReturn(GUIEvent.CLOSE, [])
            if event != 'Ok' and event != '\r' and event != 'Display' and values[0] != '':
                continue
            if event == 'Display':
                return GUIReturn(GUIEvent.DISPLAY, [])
            break
        query = values[0].split(' ')  # Split based on spaces
        query = [q.lower() for q in query]  # Convert to lower case
        return GUIReturn(GUIEvent.QUERY, query)

    def get_selected(self):
        """
        Gets the currently selected item from the Listbox. If there are none it returns a None.

        Returns:
            The selected Item, None otherwise.
        """
        if self.layout[1][3].get():
            values = self.layout[2][0].get()
        else:
            values = self.layout[2][1].get()
        return values[0] if len(values) != 0 else None

    def set_results(self, result_s: Union[List[str], Set[str]], result_sprime=None):
        """
        Set the results of a query on the GUI.

        Args:
            result_s: The first query results.
            result_sprime: The second query results.
        """
        if isinstance(result_s, Set):
            result_s = list(result_s)
        self.layout[2][0].Update(values=result_s)

        if result_sprime is not None:
            if isinstance(result_sprime, Set):
                result_sprime = list(result_s)
            self.layout[2][1].Update(values=result_sprime)

    def set_file_contents(self, contents: str):
        """
        Sets the Multiline object with the contents of a file.

        Args:
            contents: Said contents.
        """
        self.layout[2][2].Update(value=contents)
