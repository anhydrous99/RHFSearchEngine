""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 3

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

File Details:
    Wraps the model function together with the inverted index to abstract for ease of use and clean code in run.py.
"""

from models import boolean_model, vector_model, phrasal_search
from zipfile import ZipFile
from pathlib import Path
from typing import List
import collections
import html2text
import numpy as np
import re

File = collections.namedtuple('File', ['filepath', 'contents', 'text_contents', 'wordlist', 'linklist'])
InvEntry = collections.namedtuple('InvEntry', ['df', 'docs'])


class InvertedIndex:
    def __init__(self):
        """
        Initiates all regular expression/html2text engines as well as created a file list and the inverted index.
        Here we crawl our way through the html files starting from the index.html file at rhf/index.html.
        """
        self._inverted_index = {}
        # Initiate the html parser
        self._html2text = html2text.HTML2Text()
        self._html2text.ignore_links = True
        self._html2text.ignore_images = True
        self._html2text.ignore_emphasis = True
        self._html2text.escape_all = True
        # Initiate the word/link extractors, uses regular expression
        self._word_extractor = re.compile(r'[^\W_0123456789]+')
        # I am making a lot of assumptions about the format of the html here.
        # Until I see the html pages this is going to be used for, this should be fine
        self._link_extractor = re.compile(r'\s+HREF=(?:"([^"]+)"|\'([^\']+)\').*?>(.*?)')
        # List of stopwords, storing as dictionary speeds up search to O(1)
        stop_word_path = 'stopwords.txt'
        with open(stop_word_path, encoding='utf8') as f:
            tmp_swords = f.readlines()
        tmp_swords = [w.strip(' \n') for w in tmp_swords]  # Strip spaces and end-line characters
        self._stop_words = collections.Counter(tmp_swords)

        # Create a file list
        self.file_list = []
        indexed_files = set()
        base_path = Path('rhf/')
        with ZipFile('rhf.zip') as zipfile:
            idx_file_path = base_path / 'index.html'
            def add(file_path: Path):
                with zipfile.open(str(file_path.as_posix())) as html_file:
                    contents = html_file.read().decode('utf-8')
                    idx_file = self._parse(contents, file_path)
                    self.file_list.append(idx_file)
                    indexed_files.add(file_path)
                for link in idx_file.linklist:
                    link = (file_path.parent / link).resolve().relative_to('.')
                    if (link.suffix == '.html' or link.suffix == '.htm') and link not in indexed_files:
                        add(link)
            add(idx_file_path)

        # Calculate the document frequency and idf
        # The counter container is great!! :D
        df = collections.Counter()
        for file in self.file_list:
            df.update(file.wordlist)
        # Using idf = log_2 (N / (df + 1)) + 1
        idf = {k: np.log2(len(self.file_list) / (v + 1)) + 1 for k, v in dict(df).items()}

        for file in self.file_list:
            for idx, word in enumerate(file.wordlist):
                if word not in self._inverted_index:
                    self._inverted_index[word] = InvEntry(df[word], {})
                if file.filepath not in self._inverted_index[word].docs:
                    self._inverted_index[word].docs[file.filepath] = {'freq': 1, 'tf-idf': idf[word], 'postings': [idx]}
                else:
                    self._inverted_index[word].docs[file.filepath]['freq'] += 1
                    self._inverted_index[word].docs[file.filepath]['tf-idf'] += idf[word]
                    self._inverted_index[word].docs[file.filepath]['postings'].append(idx)

    def filter_stopwords(self, word_list: List[str]):
        """
        Filters stop words from a word list.

        Args:
            word_list: The word list to filter

        Returns:
            The filtered word list
        """
        return [w for w in word_list if w not in self._stop_words]

    def _parse(self, file_contents: str, file_path: Path) -> File:
        """
        Parses and individual file.

        Args:
            file_contents: Raw html-text file contents.
            file_path: The path, in the zip-file.

        Returns:
            A "File" named tuple with various information
        """
        # Parse text into a more digestible format
        raw_txt = self._html2text.handle(file_contents)
        # Extract all words, I am retaining repeat words
        word_list = [w.lower() for w in self._word_extractor.findall(raw_txt)]
        # Extract all links
        link_list = self._link_extractor.findall(file_contents)
        # Format links into proper list of links
        link_list = [obj[0] for obj in link_list]
        word_list = self.filter_stopwords(word_list)
        return File(file_path, file_contents, raw_txt, word_list, link_list)

    #  Various misc functions ----
    def __len__(self):
        return len(self._inverted_index)

    def __setitem__(self, key, value):
        self._inverted_index[key] = value

    def __getitem__(self, item):
        return self._inverted_index[item]
    # -----------------------------

    def query(self, query: List[str]):
        """
        Runs a query

        Args:
            query: A list of words to query.

        Returns:
            The query results.
        """
        if (len(query) != 0 and query[0] == '') or len(query) == 0:
            return set()
        if query[0][0] != '"' and query[-1][-1] != '"':
            # Boolean model
            if 'and' in query or 'or' in query or 'but' in query:
                if len(query) < 3:
                    print('Error: you need at least two words for boolean model.')
                results = self.boolean_query(query)
            else:  # Vector space model
                # Filter query for stop words
                query = self.filter_stopwords(query)  # No need for stop-words in the vector model
                results = self.vector_query(query)
        else:
            # Filter query for stop words
            query = self.filter_stopwords(query)  # No need for stop-words in the vector model
            query = [q.strip('"') for q in query]  # Strip " from strings
            results = self.phrasal_query(query)
        return results

    def boolean_query(self, query: List[str]):
        """
        Runs a boolean query.

        Args:
            query: A list of words to query.

        Returns:
            The query results.
        """
        return boolean_model(query, self._inverted_index)

    def vector_query(self, query: List[str]):
        """
        Runs a vector query.

        Args:
            query: A list of words to query.

        Returns:
            The query results.
        """
        return vector_model(query, self._inverted_index)

    def phrasal_query(self, query: List[str]):
        """
        Runs a phrasal query.

        Args:
            query: A list of words to query.

        Returns:
            The query results.
        """
        return phrasal_search(query, self._inverted_index)

    def get_file(self, file_path: str):
        """
        Gets a specific file from the file list.

        Args:
            file_path: The path to the file.

        Returns:
            The File.
        """
        try:
            return next(x for x in self.file_list if x.filepath == file_path)
        except StopIteration:
            return None
