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


def boolean_model(query: List[str], inverted_index: Dict) -> Set:
    """
    Uses the boolean model to search for relevant documents in an inverted index via recursion.

    Args:
        query: A list of strings with 'and', 'or', or 'but's.
        inverted_index: The inverted index to search through

    Returns:
        A set of strings with the names of the files that where found
    """
    if len(query) == 3:
        set1 = check(inverted_index.get(query[0]))
        set2 = check(inverted_index.get(query[2]))
        return combine(set1, set2, query[1])
    set2 = boolean_model(query[2:], inverted_index)
    set1 = check(inverted_index.get(query[0]))
    return combine(set1, set2, query[1])


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


def phrasal_search(query: List[str], inverted_matrix: Dict):
    and_query = copy.deepcopy(query)
    for i in reversed(range(1, len(and_query))):
        and_query.insert(i, 'and')
    docs = boolean_model(query, inverted_matrix)

    for d in docs:
        for
