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

from g2p_parsing import *
from alignment import *

def calculate_accuracy(csv_test_list, csv_ref_list):

    test_lookup = dict()
    ref_lookup = dict()

    total_ref_phones = 0
    total_edit_distance = 0

    with open(csv_test_list, "r") as test_list_file, open(csv_ref_list, "r") as ref_list_file:

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

            if align_out[2] > 0:
                with open("./errors/alignment_errors.txt", "a") as error_file:
                    error_file.write(key + "\n")
                    error_file.write("test: " + " ".join(align_out[0]) + "\n")
                    error_file.write("ref:  " + " ".join(align_out[1]) + "\n")
                    error_file.write("edit distance: " + str(align_out[2]) + "\n\n")

    print("total phones in reference:", total_ref_phones)
    print("total edit distance:      ", total_edit_distance)
    print("phone error rate:         ", total_edit_distance / total_ref_phones)
