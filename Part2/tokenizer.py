import collections
import typing
import html2text
import re

File = collections.namedtuple('File', ['filepath', 'contents', 'wordlist', 'linklist'])


class Tokenizer:
    """
    This Tokenizer class will take care of taking in a text and parsing it to as the problem description
    for Task 1 says, "ignore html tags, non-textual contents such as image." It shall extract words and urls
    It will also remove all stop-words.
    """

    def __init__(self):
        # Initiate the html parser
        self._html2text = html2text.HTML2Text()
        self._html2text.ignore_images = True
        self._html2text.ignore_emphasis = True
        self._html2text.escape_all = True

        # Initiate the word/link extractors, uses regular expression
        self._word_extractor = re.compile(r'[^\W_0123456789]+')
        self._link_extractor = re.compile(
            r'[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)')

        # List of stopwords, storing as dictionary speeds up search to O(1)
        stop_word_path = 'stopwords.txt'
        with open(stop_word_path) as f:
            tmp_swords = f.readlines()
        tmp_swords = [w.strip(' \n') for w in tmp_swords]  # Strip spaces and end-line characters
        self.stop_words = collections.Counter(tmp_swords)

    def _parse_raw(self, file_contents):
        raw_txt = self._html2text.handle(file_contents)
        wordlist = [w.lower() for w in self._word_extractor.findall(raw_txt)]
        linklist = self._link_extractor.findall(raw_txt)
        return wordlist, linklist

    def _filter_stopwords(self, word_list: typing.List[str]):
        """
        Uses dict stop word object, O(1), to filter a word list. This function s O(n) where n is the number of
        words to filter.

        :param word_list:
        :return:
        """
        return [w for w in word_list if w not in self.stop_words]

    def tokenize(self, file_path: str, contents: str) -> File:
        wordlist, linklist = self._parse_raw(contents)
        wordlist = self._filter_stopwords(wordlist)
        return File(file_path, contents, wordlist, linklist)
