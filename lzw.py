import argparse
import json
import os
import sys

import struct
from itertools import count

def compress(string):
    """
    The last yielded value will be the dict of keycodes.
    """
    symbol_count = count(1)
    words = {symbol : symbol_count.next() for symbol in set(string)}

    w = ""
    for letter in string:
        if w + letter in words:
            w += letter
        else:
            words[w + letter] = symbol_count.next()
            yield words[w]
            w = letter
    yield words

def decompress(compressed_file, keycodes):
    keycodes = {v : k for k, v in keycodes.iteritems()}

    output = []
    while True:
        next_key = compressed_file.read(4)
        if not next_key:
            return "".join(output)
        output.append(keycodes[struct.unpack("<I", next_key)[0]])

def parse_for_compress(args):
    compressed = compress(args.infile.read())
    for i in compressed:
        try:
            args.outfile.write(struct.pack("<I", i))
        except struct.error:
            args.keycode_file.write(json.dumps(i, sort_keys=True,
                                                  indent=4))

def parse_for_decompress(args):
    keycodes = json.load(args.keycode_file)
    args.outfile.write(decompress(args.infile, keycodes))

def main():
    description = ("Output an LZW compressed binary file and JSON dict"
                   "containing the keycodes for decompression, or decompress a"
                   "previously LZW compressed file.")
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers()
    parser_comp = subparsers.add_parser("compress")
    parser_comp.add_argument("--infile", nargs="?",
                             type=argparse.FileType("r"), default=sys.stdin)
    parser_comp.add_argument("--outfile", nargs="?",
                             type=argparse.FileType("wb"),
                             default=os.path.join(os.getcwd(), "output.bin"))
    parser_comp.add_argument("--keycode-file", nargs="?",
                             type=argparse.FileType("w"),
                             default=os.path.join(os.getcwd(), "keycodes.json"))
    parser_comp.set_defaults(func=parse_for_compress)
    parser_decomp = subparsers.add_parser("decompress")
    parser_decomp.add_argument("--infile", nargs="?",
                               type=argparse.FileType("rb"),
                               default=os.path.join(os.getcwd(), "output.bin"))
    parser_decomp.add_argument("--keycode-file", nargs="?",
                               type=argparse.FileType("r"),
                             default=os.path.join(os.getcwd(), "keycodes.json"))
    parser_decomp.add_argument("--outfile", nargs="?",
                               type=argparse.FileType("w"), default=sys.stdout)
    parser_decomp.set_defaults(func=parse_for_decompress)

    args = parser.parse_args()
    args.func(args)
    args.infile.close()
    args.outfile.close()
    args.keycode_file.close()

if __name__ == "__main__":
    main()
