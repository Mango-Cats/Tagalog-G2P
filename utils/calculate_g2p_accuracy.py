#!/usr/bin/env python3

"""
ECE 198: Special Problems in Electronics and Communications Engineering
DSP01 - A hybrid grapheme-to-phoneme and speech recognition system for automated phonetic transcription of speech data in Tagalog, Cebuano, and Hiligaynon
2014-06313 Aquino, Angelina A.
2014-06489 Tsang, Joshua Lijandro L.
"""

"""
< calculate-g2p-accuracy.py >
compares the edit distance of G2P-generated CSV files against manually-verified transcriptions
"""

import os

from g2p_parsing import *
from alignment import *

def calculate_accuracy(csv_test_list, csv_ref_list, file_name):

    test_lookup = dict()
    ref_lookup = dict()

    total_ref_phones = 0
    total_edit_distance = 0

    ops_dict = {}

    error_dict = {}

    with open(csv_test_list, "r") as test_list_file, open(csv_ref_list, "r") as ref_list_file:

        os.makedirs("./errors", exist_ok=True)
        with open("./errors/" + file_name + "_errors.txt", "w") as f:
            pass

        for line in test_list_file:
            clean_csv(line.strip())
            test_lookup.update(trxn2phon(csv2trxn(line.strip())))

        for line in ref_list_file:
            clean_csv(line.strip())
            ref_lookup.update(trxn2phon(csv2trxn(line.strip())))

        for key in ref_lookup.keys():
            
            test_trxn = test_lookup[key]
            ref_trxn = ref_lookup[key]
            
            total_ref_phones += len(ref_trxn)

            align_out = align_trxn(test_trxn, ref_trxn)
            total_edit_distance += align_out[2]

            for op in align_out[3]:
                if op not in ops_dict:
                    ops_dict[op] = 0
                ops_dict[op] += 1

            if align_out[2] > 0:

                error_dict[key] = align_out

                with open("./errors/" + file_name + "_errors.txt", "a") as error_file:
                    error_file.write(key + "\n")
                    error_file.write("test: " + " ".join(align_out[0]) + "\n")
                    error_file.write("ref:  " + " ".join(align_out[1]) + "\n")
                    error_file.write("edit distance: " + str(align_out[2]) + "\n\n")
                

    print("total phones in reference:", total_ref_phones)
    print("total edit distance:      ", total_edit_distance)
    print("phone error rate:         ", total_edit_distance / total_ref_phones)

    if len(ops_dict) > 0:
        with open("./errors/" + file_name + "_ops.txt", "w") as ops_file:
            for op, count in sorted(ops_dict.items(), key=lambda item: item[1], reverse=True):
                ops_file.write(f"Gold: {op[0]}, Pred: {op[1]}: {count}\n")
    return ops_dict, error_dict

def compute_per_cv(held_out_lines, apply_stdout):
    """
    Compute PER for a CV fold.
    held_out_lines : list of 'word p1 p2 ...' strings (gold standard)
    apply_stdout   : stdout from phonetisaurus-apply (word\tphonemes per line)
    """
    pred = {}
    for line in apply_stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            pred[parts[0]] = parts[1].split()

    total_ref = 0
    total_edit = 0
    for line in held_out_lines:
        parts = line.split()
        if len(parts) < 2:
            continue
        word, gold = parts[0], parts[1:]
        hypothesis = pred.get(word, [])
        total_ref += len(gold)
        total_edit += align_trxn(gold, hypothesis)[2]

    return total_edit / total_ref if total_ref > 0 else 1.0
