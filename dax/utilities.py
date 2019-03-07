import itertools as it
import json
import HTMLParser

h = HTMLParser.HTMLParser()


def decode_url_json_string(json_string):
    strings = json.loads(h.unescape(json_string),
                         object_pairs_hook=parse_json_pairs)
    return strings


# TODO: BenM/assessor_of_assessor/document me!
# useful function for preventing key-value pairs in serialized json from being
# auto-converted to unicode
def parse_json_pairs(pairs):
    sink_pairs = []
    for k, v in pairs:
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        sink_pairs.append((k, v))
    return dict(sink_pairs)


def groupby_to_dict(source, group_pred):
    results = dict()

    for k, v in it.groupby(source, group_pred):
        d = results.get(k, list())
        d.extend(list(v))
        results[k] = d

    return results


def groupby_groupby_to_dict(source, outer_pred, inner_pred):
    return {
        k: groupby_to_dict(v, inner_pred)
        for k, v in groupby_to_dict(source, outer_pred).items()
    }

def find_with_pred(items, pred):
    for i in items:
        if pred(i):
            return i
    return None
