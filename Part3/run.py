""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 3

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

Usage:
    The files stopwords.txt, tok.py, models.py, and run.py must be in the same directory as Jan.zip. This project is
    dependent on 3 libraries: html2text, numpy, and PySimpleGUI. To install::

        $ pip install html2text numpy PySimpleGUI

    This project was built using python version 3.8 so any other python version is considered to be untested, it might
    work but it is not guaranteed unless you are using version 3.8. The GUI has 6 elements, the first, a text entry
    where queries are made, an ok button to run the query, a cancel button to exit the program, a display button to
    display found file contents, and a ListBox text output where the results of the query is shown, and a MultiLine to
    display file contents. You can also run a query by pressing the Enter key or you can also exit the program by
    pressing the Escape key. To run:

        $ python run.py
"""

from inverted_index import InvertedIndex
from output_gui import OutputGUI, GUIEvent


def main():
    inverted_index = InvertedIndex()
    gui = OutputGUI()

    while True:
        event = gui.get_gui_event()

        # When pressing OK
        if event.gui_event == GUIEvent.QUERY:
            results = inverted_index.query(event.query)
            if len(results) != 0:
                gui.set_results(results)
        elif event.gui_event == GUIEvent.DISPLAY: # When pressing display
            selected = gui.get_selected()
            if selected is not None:
                result = inverted_index.get_file(selected)
                if result is not None:
                    gui.set_file_contents(result.text_contents)
        elif event.gui_event == GUIEvent.CLOSE: # When pressing close or exit on the gui
            break


if __name__ == '__main__':
    main()
