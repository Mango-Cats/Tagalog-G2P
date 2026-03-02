#!/usr/bin/env python3

"""
ECE 198: Special Problems in Electronics and Communications Engineering
DSP01 - A hybrid grapheme-to-phoneme and speech recognition system for automated phonetic transcription of speech data in Tagalog, Cebuano, and Hiligaynon
2014-06313 Aquino, Angelina A.
2014-06489 Tsang, Joshua Lijandro L.
"""

"""
< calculate-g2p-accuracy.py >
compares the edit distance of G2P-generated .dict files against manually-verified .dict files
"""

from alignment import align_trxn  # function to compute edit distance / alignment


# --- helper to read .dict files ---
def load_dict(filename: str) -> dict:
    """
    Reads a .dict file into a dictionary: word -> list of phonemes
    """
    lookup = dict()
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # split on first tab (or first space if space-separated)
            if "\t" in line:
                word, pron = line.split("\t", 1)
            else:
                word, pron = line.split(" ", 1)
            lookup[word] = pron.split()  # list of phonemes
    return lookup


# --- main ---
if __name__ == "__main__":

    # replace CSV files with .dict files
    test_dict_file = "my_g2p_output.dict"  # your system's G2P predictions
    ref_dict_file = "my_reference.dict"  # manually verified phonetic transcriptions

    # read dict files
    test_lookup = load_dict(test_dict_file)
    ref_lookup = load_dict(ref_dict_file)

    total_ref_phones = 0
    total_edit_distance = 0

    # iterate over all reference words
    for key in ref_lookup.keys():
        if key not in test_lookup:
            print(f"WARNING: word '{key}' not in test dict")
            continue

        test_trxn = test_lookup[key]
        ref_trxn = ref_lookup[key]

        total_ref_phones += len(ref_trxn)

        align_out = align_trxn(test_trxn, ref_trxn)
        total_edit_distance += align_out[2]  # edit distance

    # final output
    print("total phones in reference:", total_ref_phones)
    print("total edit distance:      ", total_edit_distance)
    print("phone error rate:         ", total_edit_distance / total_ref_phones)
