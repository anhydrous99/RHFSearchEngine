""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 2

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

File Details:
    Contains a class for parsing html files.
"""

import collections
import typing
import html2text
import ntpath
import re

File = collections.namedtuple('File', ['filename', 'filepath', 'contents', 'wordlist', 'linklist'])


class Tokenizer:
    """
    This Tokenizer class will take care of taking in a text and parsing it to as the problem description
    for Task 1 says, "ignore html tags, non-textual contents such as image." It shall extract words and urls
    It will also remove all stop-words.
    """

    def __init__(self):
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
        self.stop_words = collections.Counter(tmp_swords)

    def _parse_raw(self, file_contents):
        # Parse text into a more digestible format
        raw_txt = self._html2text.handle(file_contents)
        # Extract all words, I am retaining repeat words
        wordlist = [w.lower() for w in self._word_extractor.findall(raw_txt)]
        # Extract all links
        linklist = self._link_extractor.findall(file_contents)
        # Format links into proper list of links
        linklist = [obj[0] for obj in linklist]
        return wordlist, linklist

    def filter_stopwords(self, word_list: typing.List[str]):
        return [w for w in word_list if w not in self.stop_words]

    def tokenize(self, file_path: str, contents: str) -> File:
        """
        This function parses an html file to a word list a list of links. It is organized into a named tuple.

        Args:
            file_path: A string with the file path, for the html file
            contents: The contents of the html file

        Returns:
            A file named tuple, with the file name, file path, the contents of the html file, a list of words
            extracted from the file, and a list of links extracted from the file.
        """
        wordlist, linklist = self._parse_raw(contents)
        wordlist = self.filter_stopwords(wordlist)
        return File(ntpath.basename(file_path), file_path, contents, wordlist, linklist)
