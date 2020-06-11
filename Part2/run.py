import numpy as np
import collections
from zipfile import ZipFile
from tok import Tokenizer
import PySimpleGUI as GUI_Interface

InvEntry = collections.namedtuple('InvEntry', ['df', 'docs'])


def main():
    with ZipFile('Jan.zip') as zipfile:
        file_path_list = zipfile.namelist()
        n = len(file_path_list)
        tokenizer = Tokenizer()

        # Create a list of File types that store all information pertaining to an html file.
        # In he third period, the task says to use a hash map but I believe that we don't need to use a hash map.
        # The index of the list would be the same as the unique numerical id of a hash map.
        file_list = []
        for path in file_path_list:
            with zipfile.open(path) as html_file:
                contents = html_file.read().decode('utf-8')
                df = tokenizer.tokenize(path, contents)
                file_list.append(df)

    # Calculate the document frequency and idf
    # The counter container is great!! :D
    df = collections.Counter()
    for file in file_list:
        df.update(file.wordlist)
    # Using idf = log_2 (N / (df + 1)) + 1
    idf = {k: np.log2(n / (v + 1)) + 1 for k, v in dict(df).items()}

    # Create the inverted index
    inverted_index = {}
    for file in file_list:
        for idx, word in enumerate(file.wordlist):
            if word not in inverted_index:
                inverted_index[word] = InvEntry(df[word], {})
            if file.filename not in inverted_index[word].docs:
                inverted_index[word].docs[file.filename] = {'freq': 1, 'tf-idf': idf[word], 'postings': [idx]}
            else:
                inverted_index[word].docs[file.filename]['freq'] += 1
                inverted_index[word].docs[file.filename]['tf-idf'] += idf[word]
                inverted_index[word].docs[file.filename]['postings'].append(idx)

    # Create GUI
    layout = [[GUI_Interface.Text('Enter the query'), GUI_Interface.InputText()],
              [GUI_Interface.Button('Ok')]]
    window = GUI_Interface.Window('Search Webpages', layout, location=(40, 40), size=(400, 100))
    event, values = window.read()
    print(values[0])


if __name__ == "__main__":
    main()
