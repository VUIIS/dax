import os, sys

import pandas as pd


def _read_tsv(filename):
    return pd.read_csv(filename, sep="\t" )


def update(tsvdir):
    data = {}
    tables = ['subjects', 'sessions', 'scans', 'assessors']

    for t in tables;
        data[t] = _read_tsv( f'{tsvdir}/{t}.tsv')
        print(t, len(data[t]), data[t].head())


if __name__ == '__main__':
    tsvdir = sys.argv[1]

    update(tsvdir)
