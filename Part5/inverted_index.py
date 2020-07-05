""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 5

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

File Details:
    Wraps the model function together with the inverted index to abstract for ease of use and clean code in run.py.
"""

from models import boolean_model, vector_model, phrasal_search
from scipy.stats import pearsonr
from joblib import Parallel, delayed
from itertools import chain
from zipfile import ZipFile
from pathlib import Path
from typing import List
from tqdm import tqdm
import multiprocessing
import pandas as pd
import numpy as np
import collections
import html2text
import pickle
import gzip
import re
import os

File = collections.namedtuple('File', ['filepath', 'contents', 'text_contents', 'wordlist', 'linklist'])
InvEntry = collections.namedtuple('InvEntry', ['df', 'docs'])


def _corr(word_list1, word_list2):
    words = set(word_list1)
    words.update(word_list2)
    words = list(words)
    vec1 = np.zeros(len(words))
    vec2 = np.zeros(len(words))
    word_set1 = collections.Counter(word_list1)
    word_set2 = collections.Counter(word_list2)

    for word in word_set1:
        idx = words.index(word)
        vec1[idx] = word_set1[word]
    for word in word_set2:
        idx = words.index(word)
        vec2[idx] = word_set2[word]
    r, p = pearsonr(vec1, vec2)
    return r


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
        self._link_extractor_1 = re.compile(r'\s+href=(?:(.*?>)).*?>(.*?)')
        # List of stopwords, storing as dictionary speeds up search to O(1)
        stop_word_path = 'stopwords.txt'
        with open(stop_word_path, encoding='utf8') as f:
            tmp_swords = f.readlines()
        tmp_swords = [w.strip(' \n') for w in tmp_swords]  # Strip spaces and end-line characters
        self._stop_words = collections.Counter(tmp_swords)

        cache_path = Path('cache.data')
        if cache_path.exists() and cache_path.is_file():
            print('Cache file found - Importing Cache')
            with gzip.open(cache_path, 'rb') as g_file:
                self._file_list, self._inverted_index, self._doc_corr, self._doc_tfidf = pickle.load(g_file)
        else:
            # Create a file list
            self._file_list = []
            indexed_files = set()
            base_path = Path('rhf/')
            counter = tqdm(desc='Links Crawled', unit='link')
            with ZipFile('rhf.zip') as zipfile:

                def add(file_path: Path):
                    try:
                        with zipfile.open(str(file_path.as_posix())) as html_file:
                            try:
                                contents = html_file.read().decode('utf-8')
                            except UnicodeDecodeError:
                                return []
                    except KeyError:
                        return []
                    idx_file = self._parse(contents, str(file_path.as_posix()))
                    if file_path not in indexed_files:
                        self._file_list.append(idx_file)
                        indexed_files.add(file_path)
                    counter.update()
                    output = []
                    for link in idx_file.linklist:
                        link = (file_path.parent / link).resolve()
                        link = Path(os.path.relpath(link, '.'))
                        if link.suffix == '.html' and link not in indexed_files:
                            output.append(link)
                    return output

                idx_file_path = base_path / 'index.html'
                queue = collections.deque(add(idx_file_path))
                while len(queue) != 0:
                    queue.extend(add(queue.pop()))

            counter.close()
            print(f'Pages found: {len(self._file_list)}')

            # Calculate the document frequency and idf
            # The counter container is great!! :D
            df = collections.Counter()
            for file in self._file_list:
                df.update(file.wordlist)
            # Using idf = log_2 (N / (df + 1)) + 1
            idf = {k: np.log2(len(self._file_list) / (v + 1)) + 1 for k, v in dict(df).items()}

            for file in self._file_list:
                for idx, word in enumerate(file.wordlist):
                    if word not in self._inverted_index:
                        self._inverted_index[word] = InvEntry(df[word], {})
                    if file.filepath not in self._inverted_index[word].docs:
                        self._inverted_index[word].docs[file.filepath] = {'freq': 1, 'tf-idf': idf[word], 'postings': [idx]}
                    else:
                        self._inverted_index[word].docs[file.filepath]['freq'] += 1
                        self._inverted_index[word].docs[file.filepath]['tf-idf'] += idf[word]
                        self._inverted_index[word].docs[file.filepath]['postings'].append(idx)

            # Create Document TF-IDF List
            self._doc_tfidf = {}
            for file in tqdm(self._file_list, desc='Generating Document TF-IDF List', unit='doc'):
                self._doc_tfidf[file.filepath] = {}
                for idx, word in enumerate(file.wordlist):
                    if word in self._inverted_index and file.filepath in self._inverted_index[word].docs:
                        self._doc_tfidf[file.filepath][word] = self._inverted_index[word].docs[file.filepath]['tf-idf']

            # Calculate Document Correlation List
            def corr_list(file_list: List[File], doc1: File):
                tmp = {}
                cutoff = 0.01
                for doc2 in file_list:
                    if doc1 == doc2:
                        continue
                    corr = _corr(doc1.wordlist, doc2.wordlist)
                    if corr != np.nan and corr > cutoff:
                        tmp[doc2.filepath] = corr
                return {doc1.filepath: tmp}

            results = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(corr_list)(self._file_list, doc) for doc in
                                          tqdm(self._file_list, desc='Calculating Correlations', unit='doc'))
            print('Post-processing correlations')
            self._doc_corr = {list(r.keys())[0]: list(r.values())[0] for r in results}
            # Save cache
            with gzip.open(cache_path, 'wb') as g_file:
                pickle.dump((self._file_list, self._inverted_index, self._doc_corr, self._doc_tfidf), g_file)

    def filter_stopwords(self, word_list: List[str]):
        """
        Filters stop words from a word list.

        Args:
            word_list: The word list to filter

        Returns:
            The filtered word list
        """
        return [w for w in word_list if w not in self._stop_words]

    def _parse(self, file_contents: str, file_path: str) -> File:
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
        link_list_1 = self._link_extractor_1.findall(file_contents)
        # Format links into proper list of links
        link_list = [obj[0] for obj in link_list]
        for link in link_list_1:
            for l in link:
                if l != '':
                    if l[-1] == '>':
                        link_list.append(l[:-1])
                    else:
                        link_list.append(l)
        link_list = set([link for link in link_list if 'mailto' not in link and ':' not in link and '-' not in link])
        link_list = list(link_list)
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

    def query_ref(self, query: List[str], calc_rec=True):
        """
        Runs the algorithm listed in the Query Reformation (Part 4) Project

        Args:
            query: A list of words to query.
            calc_rec: Whether to calculate recommendations

        Returns:
            Two query results.
        """
        results = self.query(query)
        subquery = self.filter_stopwords(query)

        # Create tf-idf matrix
        files = list(results)
        tfidf = np.array([[self._doc_tfidf[f][q] if q in self._doc_tfidf[f] else 0 for q in subquery] for f in files])

        file_similarity = collections.OrderedDict()
        for idx, tfidf_file in enumerate(tfidf):
            file_similarity[files[idx]] = tfidf_file.sum() / (np.linalg.norm(tfidf_file) * np.sqrt(tfidf_file.shape[0]))
        # Sort the ordered dict -- Filter top ranked documents -- a sixteenth of the documents
        file_similarity = collections.OrderedDict(
            sorted(file_similarity.items(), key=lambda x: x[1], reverse=True)[:len(file_similarity) // 16])
        files_dict = {file.filepath: file.wordlist for file in self._file_list}
        K = [files_dict[f] for f in file_similarity]
        K = set(chain.from_iterable(K))
        K.update(subquery)
        K = list(K)
        K = self.filter_stopwords(K)

        # Get query indexes
        idxes = np.array([K.index(q) for q in subquery])
        tfidf = np.array([[self._doc_tfidf[f][k] if k in self._doc_tfidf[f] else 0 for k in K] for f in files])
        tfidf = tfidf.transpose()
        # Normalize according to columns (documents)
        tfidf_norms = np.apply_along_axis(np.linalg.norm, 1, tfidf).reshape(-1, 1)
        tfidf = tfidf / tfidf_norms
        corr = np.matmul(tfidf[idxes], tfidf.transpose())
        # Get the 4 largest indexes
        flat = corr.flatten()
        n = len(idxes) + 4
        if n < len(flat):
            ind = np.argpartition(flat, -n)[-n:]
            ind = ind[np.argsort(-flat[ind])]
            ind = np.unravel_index(ind, corr.shape)[1]

            for idx in ind:
                subquery.append(K[idx])

        if calc_rec:
            subquery_results = self.query(subquery)
            return results, subquery_results, self._gen_rec(file_similarity.keys()), self._gen_rec(subquery_results)

        return results, self.query(subquery)

    def _gen_rec(self, a_set):
        if len(a_set) == 0:
            return []
        doc_corr = {}
        n_recs = 5
        for a in a_set:
            doc_corr[a] = self._doc_corr[a]
        doc_df = pd.DataFrame(doc_corr).fillna(0)
        largest_np = doc_df.values

        vec_sum = np.average(largest_np, axis=1)

        if vec_sum.shape[0] < n_recs:
            n_recs = vec_sum.shape[0]

        ind = np.argpartition(vec_sum, -n_recs)[-n_recs:]

        output_l = []
        for i in ind:
            output_l.append(doc_df.index.values[i])
        return output_l

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
            return next(x for x in self._file_list if x.filepath == file_path)
        except StopIteration:
            return None
