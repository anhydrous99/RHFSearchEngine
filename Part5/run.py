""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 5

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

Usage:
    The files stopwords.txt, inverted_index.py, models.py, output_gui.py, and run.py must be in the same directory as
    Jan.zip. This project is dependent on 5 libraries: html2text, numpy, pandas, joblib, and PySimpleGUI. To install::

        $ pip install html2text numpy PySimpleGUI pandas joblib

    Part 5's algorithm is in the class InvertedIndex, in the member functions _gen_rec and query_ref. For quick starts
    the cache file cache.data is required. If the cache.data file is not detected it will be generated. With a
    Ryzen 7 3800X 8-Core processor the process takes about an hour, part of the processes is ran in a multi-process
    manner to take advantage of multiple cores. It still took an hour! So, it is highly recommended to have the
    cache.data file in the same directory as all the other source files, together with the stopwords.txt and rhf.zip
    file.

    To run:

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
            if event.query != '' or event.query != ['']:
                results = inverted_index.query_ref(event.query, True if event.use_rec == 1 else False)
                if len(results) != 0:
                    gui.set_results(*results)
        elif event.gui_event == GUIEvent.DISPLAY:  # When pressing display
            selected = gui.get_selected()
            if selected is not None:
                result = inverted_index.get_file(selected)
                if result is not None:
                    gui.set_file_contents(result.text_contents)
        elif event.gui_event == GUIEvent.CLOSE:  # When pressing close or exit on the gui
            break


if __name__ == '__main__':
    main()
