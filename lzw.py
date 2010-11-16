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

if __name__ == "__main__":
    import os
    import json

    output, keycodes = "output.bin", "keycodes.json"
    print ("Outputting the compressed data to \n\t{0}\nand the corresponding "
           "keycodes to \n\t{1}".format(os.path.join(os.getcwd(), output),
                                        os.path.join(os.getcwd(), keycodes)))

    with open(output, "wb") as op, open(keycodes, "w") as json_op:
        compressed = compress("aaaavvabbabasdfbwbabababadfnbbbasdfwbbbbasdfawn"
                              "ekrjnzxcvzxcvzbxcvbababdfbbbbabaaaabbababababa")
        # or try: compress(open("/path/to/huckleberry/finn/.txt/").read())
        for i in compressed:
            try:
                op.write(struct.pack("<I", i))
            except struct.error:
                json_op.write(json.dumps(i, sort_keys=True, indent=4))

"""
To decode:
    output = open("output.bin")
    json_keycodes = open("keycodes.json")

    import json
    keycodes = json.load(json_keycodes)

    decompress(output, keycodes)
"""
