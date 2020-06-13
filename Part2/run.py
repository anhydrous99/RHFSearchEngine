""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 2

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

Usage:
    The files stopwords.txt, tok.py, models.py, and run.py must be in the same directory as Jan.zip. This project is
    dependent on 3 libraries: html2text, numpy, and PySimpleGUI. To install::

        $ pip install html2text numpy PySimpleGUI

    This project was built using python version 3.8 so any other python version is considered to be untested, it might
    work but it is not guaranteed unless you are using version 3.8. The GUI has 4 elements, the first, a text entry
    where queries are made, an ok button to run the query, a cancel button to exit the program, and a multiline text
    output where the results of the query is shown. You can also run a query by pressing the Enter key or you can also
    exit the program by pressing the Escape key. To run:

        $ python run.py

Queries:
    As per the requirements of this part of the project there are 3 types of queries that are possible:
    * Boolean Model - This query is activated when the words `and`, `or`, and/or `but` are detected.
        Example Query:
            music or cats
        Output:
            fab.html
            hippos.html
            kitty.html
            3 results
    * Vector Space Model - This query is activated when there is a single word query or when there are no `and`,
        `or`, and/or `but` words detected.
        Example Query:
            music hot
        Output:
            hippos.html
            fab.html
            gravies.html
            galant.html
            4 results
    * Phrasal Search - This query type is activated when quotes, ", are detected around the query.
        Example Query:
            "movies and real life"
        Output:
            armed.html
            1 results
"""

import numpy as np
import collections
from zipfile import ZipFile
from tok import Tokenizer
from models import boolean_model, vector_model, phrasal_search
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
              [GUI_Interface.Button('Ok'), GUI_Interface.Button('Cancel')],
              [GUI_Interface.Multiline(disabled=True, size=(None, 200))]]
    window = GUI_Interface.Window('Search Webpages', layout, location=(40, 40), size=(350, 200),
                                  return_keyboard_events=True)

    # Event loop
    while True:
        event, values = window.read()
        if event == GUI_Interface.WIN_CLOSED or event == 'Cancel' or event == 'Escape:27':
            break
        if event != 'Ok' and event != '\r':
            continue
        query = values[0].split(' ')  # Split based on spaces
        query = [q.lower() for q in query]  # Convert to lower case
        if query[0][0] != '"' and query[-1][-1] != '"':
            # Boolean model
            if 'and' in query or 'or' in query or 'but' in query:
                if len(query) < 3:
                    print('Error: you need at least to words for boolean model.')
                results = boolean_model(query, inverted_index)
                update(results, layout[2][0])
            else:  # Vector space model
                # Filter query for stop words
                query = tokenizer.filter_stopwords(query)  # No need for stop-words in the vector model
                results = vector_model(query, inverted_index)
                update(results, layout[2][0])
        else:
            # Filter query for stop words
            query = tokenizer.filter_stopwords(query)  # No need for stop-words in the vector model
            query = [q.strip('"') for q in query]  # Strip " from strings
            results = phrasal_search(query, inverted_index)
            update(results, layout[2][0])


def update(results, interface):
    out_str = ''
    for result in results:
        out_str += result + '\n'
    out_str += f'{len(results)} results'
    interface.Update(value=out_str)


if __name__ == "__main__":
    main()
