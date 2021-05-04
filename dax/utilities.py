import itertools as it
import json
import html
import fnmatch
import yaml
import os
import shutil
import re
import smtplib
from email.mime.text import MIMEText

from .errors import DaxError


def decode_url_json_string(json_string):
    """
    Load a string representing serialised json into
    :param json_string:
    :return:
    """
    strings = json.loads(html.unescape(json_string),
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
        if isinstance(k, str):
            k = k.encode('utf-8').decode()
        if isinstance(v, str):
            v = v.encode('utf-8').decode()
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
        for k, v in list(groupby_to_dict(source, outer_pred).items())
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
    return ','.join([x.strip() for x in list_arg.split(',')])


def extract_exp(expression, full_regex=False):
    """Extract the experession with or without full_regex.

    :param expression: string to filter
    :param full_regex: using full regex
    :return: regex Object from re package
    """
    if not full_regex:
        exp = fnmatch.translate(expression)
    return re.compile(exp)


def clean_directory(directory):
    """
    Remove a directory tree or file

    :param directory: The directory (with sub directories if desired that you
     want to delete). Also works with a file.
    :return: None

    """
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
        else:
            os.remove(fpath)


def check_image_format(fpath):
    """
    Check to see if a NIfTI file or REC file are uncompress and runs gzip via
     system command if not compressed

    :param fpath: Filepath of a NIfTI or REC file
    :return: the new file path of the gzipped file.

    """
    if fpath.endswith('.nii') or fpath.endswith('.rec'):
        os.system('gzip %s' % fpath)
        fpath = '%s.gz' % fpath
    return fpath


def read_yaml(yaml_file):
    """Functio to read a yaml file and return the document info

    :param yaml_file: yaml file path
    """
    with open(yaml_file, "r") as yaml_stream:
        try:
            return yaml.load(yaml_stream, Loader=yaml.FullLoader)
        except yaml.error.YAMLError as exc:
            err = 'YAML File {} could not be loaded properly. Error: {}'
            raise DaxError(err.format(yaml_file, exc))
    return None


def send_email(smtp_from, smtp_host, smtp_pass, to_addr, subject, content):
    """
    Send an email
    :param content: content of the email
    :param to_addr: address to send the email to
    :param subject: subject of the email
    :return: None
    """

    # Create the container (outer) email message.
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = smtp_from
    msg['To'] = ','.join(to_addr)

    # Send the email via our SMTP server
    smtp = smtplib.SMTP(smtp_host)
    smtp.starttls()
    smtp.login(smtp_from, smtp_pass)
    smtp.sendmail(smtp_from, to_addr, msg.as_string())
    smtp.quit()


def send_email_netrc(smtp_host, to_addr, subject, content):
    import netrc

    (smtp_from, _, smtp_pass) = netrc.netrc().authenticators(smtp_host)

    send_email(smtp_from, smtp_host, smtp_pass, to_addr, subject, content)
