import itertools as it
import json
import HTMLParser

h = HTMLParser.HTMLParser()


def decode_url_json_string(json_string):
    """
    Load a string representing serialised json into
    :param json_string:
    :return:
    """
    strings = json.loads(h.unescape(json_string),
                         object_pairs_hook=parse_json_pairs)
    return strings


# TODO: BenM/assessor_of_assessor/document me!
# useful function for preventing key-value pairs in serialized json from being
# auto-converted to unicode
def parse_json_pairs(pairs):
    """
    An object hook for the json.loads method. Used in decode_url_json_string.
    :param pairs:
    :return: A dictionary of parsed json
    """
    sink_pairs = []
    for k, v in pairs:
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        sink_pairs.append((k, v))
    return dict(sink_pairs)


def groupby_to_dict(source, group_pred):
    """
    Given a source iterable and a predicate defining how to group elements of
    the source iterable, convert the source iterable into a dictionary grouped
    by the key returned by the predicate.
    Example:
    source iterable: [{a:1, b:2}, (a:2, b:3}, {a:1, b:4}]
    group_pred: lambda x: x[a]

    results in:
    {
        1:[{a:1, b:2}, {a:1, b:4}],
        2:[{a:2, b:3}]
    }

    :param source: a keyless iterable (list or dictionary values or similar)
    :param group_pred: a function to determine the key by which each entry
    is grouped
    :return: the resulting dictionary of elements
    """
    results = dict()

    for k, v in it.groupby(source, group_pred):
        d = results.get(k, list())
        d.extend(list(v))
        results[k] = d

    return results


def groupby_groupby_to_dict(source, outer_pred, inner_pred):
    """
    Given a source iterable and two predicates defining how to group elements
    of the source iterable, convert the source iterable into a dictionary of
    dictionaries grouped by the keys returned by the predicate.

    :param source: a keyless iterable (list or dictionary values or similar)
    :param outer_pred: a function to determine the top level key by which each
    entry is grouped
    :param inner_pred: a function to determine the second level by which each
    entry is grouped
    :return: the resulting dictionary of dictionaries of elements
    """
    return {
        k: groupby_to_dict(v, inner_pred)
        for k, v in groupby_to_dict(source, outer_pred).items()
    }


def find_with_pred(items, pred):
    """
    Given a source iterable and a predicate defining how to identify an
    element, find and return the element if it is present, or None if the
    element is not found.

    :param items: a keyless iterable (list or dictionary values or similar)
    :param pred:
    :return: the element found by the predicate, or None
    """
    for i in items:
        if pred(i):
            return i
    return None


def strip_leading_and_trailing_spaces(list_arg):
    return ','.join(map(lambda x: x.strip(), list_arg.split(',')))
