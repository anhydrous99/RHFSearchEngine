

def combine(set1, set2, t):
    if t == 'and':
        return set1.intersection(set2)
    elif t == 'or':
        return set1.union(set2)
    elif t == 'but':
        return set1.difference(set2)


def check(value):
    if value is None:
        return set()
    return set(value.docs.keys())


def boolean_model(query, inverted_index):
    if len(query) == 3:
        set1 = check(inverted_index.get(query[0]))
        set2 = check(inverted_index.get(query[2]))
        return combine(set1, set2, query[1])
    set2 = boolean_model(query[2:], inverted_index)
    set1 = check(inverted_index.get(query[0]))
    return combine(set1, set2, query[1])
