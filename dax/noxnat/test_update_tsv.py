import os, sys

import pandas as pd


def _read_tsv(filename):
    df = pd.read_csv(filename, sep="\t" )
    return df


def _save_tsv(df, filename):
    pass


def _load(tsvdir):
    data = {}
    tables = ['subjects', 'sessions', 'scans', 'assessors']

    for t in tables:
        data[t] = _read_tsv(f'{tsvdir}/{t}.tsv').fillna('')
        print(t, len(data[t]))

    return data

def update(tsvdir):
    data = _load(tsvdir)

    for k, df in data:
        print(k, len(df))
        df.head()


if __name__ == '__main__':
    tsvdir = sys.argv[1]

    update(tsvdir)
