""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 4

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

Usage:
    The files stopwords.txt, tok.py, models.py, and run.py must be in the same directory as Jan.zip. This project is
    dependent on 3 libraries: html2text, numpy, sckit-learn, and PySimpleGUI. To install::

        $ pip install html2text numpy PySimpleGUI scikit-learn

    Two boxes show the two results from the raw query and from the algorithm described in Part 4. Since, in part 3,
    crawling didn't get everything I used a very broad regex with a lot of false positives. I believe this is because
    some html page's "a" tags are not proper html format.
    They are formatted as:
    <a href=url>
    Instead of
    <a HREF="url"> or <a href='href'> or <a HREF='url> or <a href="url">
    Anyway, the the number of articles, since python's frame size is large, this program hit the recursion limit.
    I changed those to a non-recursive version. Recursion in python is a bad idea, lol.
    Btw, box 1 has the raw results and box 2 has the results from the part 3 algo.

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
            if event.query != '':
                results = inverted_index.query_ref(event.query)
                if len(results) != 0:
                    gui.set_results(*results)
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
