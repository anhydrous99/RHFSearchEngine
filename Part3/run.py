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
