from models import boolean_model, vector_model, phrasal_search
from typing import List
from zipfile import ZipFile
import collections
import html2text
import ntpath
import re

File = collections.namedtuple('File', ['filename', 'filepath', 'contents', 'wordlist', 'linklist'])
InvEntry = collections.namedtuple('InvEntry', ['df', 'docs'])


class InvertedIndex:
    def __init__(self):
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
        file_list = []
        indexed_files = set()
        with ZipFile('rhf.zip') as zipfile:
            idx_file_path = 'rhf/index.html'
            with zipfile.open(idx_file_path) as html_file:
                contents = html_file.read().decode('utf-8')
                idx_file = self._parse(contents, idx_file_path)
                file_list.append(idx_file)
                indexed_files.add(idx_file_path)
            print(idx_file.linklist)
            # TODO

    def filter_stopwords(self, word_list: List[str]):
        return [w for w in word_list if w not in self._stop_words]

    def _parse(self, file_contents, file_path):
        # Parse text into a more digestible format
        raw_txt = self._html2text.handle(file_contents)
        # Extract all words, I am retaining repeat words
        word_list = [w.lower() for w in self._word_extractor.findall(raw_txt)]
        # Extract all links
        link_list = self._link_extractor.findall(file_contents)
        # Format links into proper list of links
        link_list = [obj[0] for obj in link_list]
        word_list = self.filter_stopwords(word_list)
        return File(ntpath.basename(file_path), file_path, file_contents, word_list, link_list)

    def __len__(self):
        return len(self._inverted_index)

    def __setitem__(self, key, value):
        self._inverted_index[key] = value

    def __getitem__(self, item):
        return self._inverted_index[item]

    def query(self, query):
        if query[0][0] != '"' and query[-1][-1] != '"':
            # Boolean model
            if 'and' in query or 'or' in query or 'but' in query:
                if len(query) < 3:
                    print('Error: you need at least to words for boolean model.')
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

    def boolean_query(self, query):
        return boolean_model(query, self._inverted_index)

    def vector_query(self, query):
        return vector_model(query, self._inverted_index)

    def phrasal_query(self, query):
        return phrasal_search(query, self._inverted_index)
