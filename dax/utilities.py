import json
import HTMLParser

h = HTMLParser.HTMLParser()

def decode_url_json_string(json_string):
    print json_string
    json_string = h.unescape(json_string)
    print json_string
    # json_string = str(json_string)
    # strings = json.loads(json_string,
    #                   object_hook=parse_json,
    #                   object_pairs_hook=parse_json_pairs)
    strings = json.loads(json_string)
    return map(lambda s: str(s), strings)



def parse_json(pairs):
    print pairs
    return dict(pairs)

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
