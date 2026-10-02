#!/usr/bin/python3

"""
ECE 198: Special Problems in Electronics and Communications Engineering
DSP01 - A hybrid grapheme-to-phoneme and speech recognition system for automated phonetic transcription of speech data in Tagalog, Cebuano, and Hiligaynon
2014-06313 Aquino, Angelina A.
2014-06489 Tsang, Joshua Lijandro L.
"""

import os

from g2p_parsing import *

def create_dict(log_list, csv_list, dict_name):
    '''
    < create-dict.py >
    creates a pronunciation dictionary using vocabulary from LOG files and corresponding transcriptions thereof from CSV files
    '''
    utt_lookup = dict()
    trxn_lookup = dict()
    utt_trxn_set = set()
    utt_trxn_list = list()

    with open(log_list, "r") as log_list_file, open(
        csv_list, "r"
    ) as csv_list_file, open(dict_name, "w") as dict_file:

        for line in log_list_file:
            utt_lookup.update(clean_utt(log2utt(line.strip())))
            # print(utt_lookup)
            pass

        for line in csv_list_file:
            clean_csv(line.strip())
            trxn_lookup.update(csv2trxn(line.strip()))
            # print(trxn_lookup)
            pass

        for key in trxn_lookup.keys():
            utt = utt_lookup[key]
            trxn = trxn_lookup[key]

            if len(utt) != len(trxn):
                print(key)
                print(len(utt), utt_lookup[key])
                print(len(trxn), trxn_lookup[key])
            else:
                for i in range(len(utt)):
                    utt_trxn_set.add((utt[i], trxn[i]))

        utt_trxn_list = list(utt_trxn_set)
        utt_trxn_list.sort()

        for utt, trxn in utt_trxn_list:
            dict_file.write(utt + "\t" + trxn + "\n")


def create_trxn(log_test, wlist_g2p_name, out_dir):
    '''
    create_trxn
    encodes CSV file transcriptions of utterances in LOG files using a dictionary containing words and G2P-generated pronunciations
    the CSV files are written to out_dir; returns the path of a file listing them
    '''
    utt_lookup = dict()
    trxn_lookup = dict()
    wlist_g2p = dict()

    csv_files = list()

    out_dir = str(out_dir).replace(os.sep, "/")
    os.makedirs(out_dir, exist_ok=True)

    with open(log_test, "r") as log_test_file, open(
        wlist_g2p_name, "r"
    ) as wlist_g2p_file:

        for line in log_test_file:
            utt_lookup.update(clean_utt(log2utt(line.strip())))

            csv_name = ".".join(line.strip().split("/")[-1].split(".")[:-1]) + ".csv"
            csv_files.append(out_dir + "/" + csv_name)

        for line in wlist_g2p_file:
            pair = line.strip().split("\t")
            wlist_g2p[pair[0]] = pair[1]

        trxn_lookup.update(utt2trxn(utt_lookup, wlist_g2p))

        for csv_address in csv_files:
            trxn2csv(trxn_lookup, csv_address)

    csv_list_name = out_dir + "/csv-list.txt"
    with open(csv_list_name, "w") as csv_list_file:
        for csv_address in csv_files:
            csv_list_file.write(csv_address + "\n")

    return csv_list_name


def create_wlist(log_test, wlist_name):
    '''
    create_wlist
    creates a wordlist file using vocabulary from LOG files
    '''
    utt_lookup = dict()
    wlist = dict()

    with open(log_test, "r") as log_test_file, open(wlist_name, "w") as wlist_file:

        for line in log_test_file:
            utt_lookup.update(clean_utt(log2utt(line.strip())))

        wlist.update(utt2wlist(utt_lookup))

        for word in wlist.keys():
            wlist_file.write(word + "\n")
