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

    def _filter_stopwords(self, word_list: typing.List[str]):
        return [w for w in word_list if w not in self.stop_words]

    def tokenize(self, file_path: str, contents: str) -> File:
        wordlist, linklist = self._parse_raw(contents)
        wordlist = self._filter_stopwords(wordlist)
        return File(file_path, contents, wordlist, linklist)
