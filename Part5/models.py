""" CSCI 6370.01 Information Retrieval & Web Search - Project Part 5

Authors:
    Armando Herrera (ID: 20217690) Team Lead
    Ulvi Bajarani (ID: 20539914)

File Details:
    Contains all of the model functions.
"""

from typing import List, Dict, Set
import numpy as np
import collections
import copy


def combine(set1: Set[str], set2: Set[str], t: str) -> Set[str]:
    """
    Combines two sets with either intersection, union, or difference depending on t, when t is 'and' calculate the
    intersection, when t is 'or' calculate the union, and when t is 'but' calculate the difference of the sets.

    Args:
        set1:
        set2:
        t:

    Returns:
        A combined set
    """
    if t == 'and':
        return set1.intersection(set2)
    elif t == 'or':
        return set1.union(set2)
    elif t == 'but':
        return set1.difference(set2)


def check(value) -> Set:
    if value is None:
        return set()
    return set(value.docs.keys())


def boolean_model(query: List[str], inverted_index: Dict):
    """
    Use the boolean model to search for relevant documents in an inverted index.

    Args:
        query: A list of string with 'and', 'or', or 'but's.
        inverted_index: The inverted index to search through

    Returns:
        A set of strings with the names of the files that where found
    """
    initial_set = set()
    for idx in range(0, len(query), 2):
        if idx == 0:
            initial_set.update(inverted_index[query[0]].docs)
        else:
            initial_set = combine(initial_set, inverted_index[query[idx]].docs, query[idx - 1])
    return initial_set


def vector_model(query: List[str], inverted_matrix: Dict) -> List:
    """
    Uses the vector space model to search for relevant documents in an inverted index.

    Args:
        query: A list of strings with words to query
        inverted_matrix: The inverted index to search through

    Returns:
        A list of strings with the names of the files that where found
    """
    query = collections.Counter(query)
    searches = [{doc: inverted_matrix[q].docs[doc] for doc in inverted_matrix[q].docs} if inverted_matrix.get(
        q) is not None else None for q in query]

    # Create tfidf matrix
    files = set()
    for search in searches:
        if search is not None:
            for doc in search:
                files.add(doc)
    files = list(files)
    tfidf = np.zeros((len(files), len(query)))
    for y_idx, search in enumerate(searches):
        if search is not None:
            for doc in search:
                x_idx = files.index(doc)
                tfidf[x_idx, y_idx] = search[doc]['tf-idf']

    # Create query vector
    q = np.array(list(query.values()))
    cossim = np.dot(tfidf, q) / (np.linalg.norm(tfidf) * np.linalg.norm(q))
    files_dict = {f: cossim[files.index(f)] for f in files}
    files.sort(key=lambda k: files_dict[k], reverse=True)
    return files


def phrasal_sub_search(t1: str, t2: str, docs: Set[str], inverted_index: Dict) -> Set[str]:
    """
    A sub-search utility function for the prasal search, it uses phrasal search for only two terms,
    This is used multiple times in the full search.

    Args:
        t1: The first term to phrasal search for
        t2: The second term to phrasal search for
        docs: A Pre-selected set of documents where both terms occur
        inverted_index: The inverted index to search through

    Returns:
        A sub-set, from the docs set, of documents where the terms are neighbors.
    """
    output_set = set()
    for doc in docs:
        stop = False
        for p1 in inverted_index[t1].docs[doc]['postings']:
            if stop:
                break
            for p2 in inverted_index[t2].docs[doc]['postings']:
                if p1 > p2:
                    continue
                if abs(p1 - p2) == 1:
                    stop = True
                    output_set.add(doc)
                    break
    return output_set


def phrasal_search(query: List[str], inverted_index: Dict) -> List[str]:
    """
    Uses the phrasal search algorithm to search for, not only terms, but phrases. Searches through an inverted index.

    Args:
        query: The query terms.
        inverted_index: The inverted index to search through

    Returns:
        A list of strings with the names of the files that where found
    """
    docs = None
    if len(query) != 1:
        and_query = copy.deepcopy(query)
        for i in reversed(range(1, len(and_query))):
            and_query.insert(i, 'and')
        docs = boolean_model(and_query, inverted_index)
    else:
        return vector_model(query, inverted_index)

    R = collections.Counter()
    for idx in range(1, len(query)):
        R.update(phrasal_sub_search(query[idx - 1], query[idx], docs, inverted_index))

    # Filter dicts
    output = []
    for k in R.keys():
        if R[k] == len(query) - 1:
            output.append(k)
    return output
