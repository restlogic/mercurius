#!/usr/bin/env python3
import pickle
import argparse

def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--in-file", 
        default="prefix-summary-agg-group.pkl",
    )

    parser.add_argument(
        "--out-file",
        required=True,
    )

    parser.add_argument(
        "--key",
        required=True,
    )

    return parser


def preprocess_pkl(IN_FILE, OUT_FILE, KEY):
    with open(IN_FILE, 'rb') as f:
        d = pickle.load(f)
        with open(OUT_FILE, 'wb') as f2:
            pickle.dump(d[KEY], f2)
            print(d[KEY])


def main():
    parser = argparse.ArgumentParser(prog='preprocess_pkl')
    add_arguments(parser)
    args = parser.parse_args()

    IN_FILE = args.in_file
    OUT_FILE = args.out_file
    KEY = args.key
    preprocess_pkl(IN_FILE=IN_FILE, OUT_FILE=OUT_FILE, KEY=KEY)


if __name__ == '__main__':
    main()