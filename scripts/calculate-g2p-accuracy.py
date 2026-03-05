#!/usr/bin/env python3

"""
calculate-g2p-accuracy.py
---------------------------------
Utility script used in the Taglog-G2P project to compute phone-level
error statistics between G2P-generated transcriptions and human-verified
reference transcriptions.

What it does:
- Reads two file lists: one containing paths to generated (test) CSVs and
  one containing paths to reference (gold) CSVs. Each list has one CSV
  file path per line.
- For every CSV listed, it converts CSV -> transaction records -> phoneme
  sequences (using helpers in `g2p_parsing`) and stores them in lookups.
- It then aligns each test phoneme sequence to its reference using
  `align_trxn` from `alignment` and accumulates the edit distance.

Outputs:
- total phones in reference: total number of reference phonemes
- total edit distance: total substitution+insertion+deletion counts
- phone error rate: edit distance divided by total reference phones

Usage example (run from repository root):
python scripts/calculate-g2p-accuracy.py

Notes:
- The script expects `csv-test-files.txt` and `csv-testref-files.txt` to
  exist in the current working directory (they do in `scripts/`).
- This file focuses on accumulating statistics — deeper per-file or
  per-phone reports are available by modifying the accumulation logic.
"""

from g2p_parsing import csv2trxn, trxn2phon, clean_csv
from alignment import align_trxn


def _safe_strip(s):
    """Return stripped string or empty string if None."""
    return s.strip() if s else ""


if __name__ == "__main__":

    # Files that list CSVs (one path per line). These are relative to
    # the working directory; the repository includes `scripts/csv-*.txt`.
    test_list = "csv-test-files.txt"
    ref_list = "csv-testref-files.txt"

    # lookups map an utterance identifier -> list of phones (phoneme sequence)
    test_lookup = dict()
    ref_lookup = dict()

    # running totals used to compute the phone error rate
    total_ref_phones = 0
    total_edit_distance = 0
    total_mismatches = 0

    with open(test_list, "r") as test_list_file, open(ref_list, "r") as ref_list_file:

        # Build test lookup: for each CSV in the test list, parse -> convert
        for line in test_list_file:
            path = _safe_strip(line)
            if not path:
                continue
            clean_csv(path)
            test_lookup.update(trxn2phon(csv2trxn(path)))

        # Build reference lookup similarly
        for line in ref_list_file:
            path = _safe_strip(line)
            if not path:
                continue
            clean_csv(path)
            ref_lookup.update(trxn2phon(csv2trxn(path)))

        for key in ref_lookup.keys():
            if key not in test_lookup:
                continue

            test_trxn = test_lookup[key]
            ref_trxn = ref_lookup[key]

            # count reference phones for the denominator of error rate
            total_ref_phones += len(ref_trxn)

            # perform alignment; align_out[2] is edit distance
            align_out = align_trxn(test_trxn, ref_trxn)
            total_edit_distance += align_out[2]

            if align_out[2] > 0:
                total_mismatches += 1

    # Print summary statistics. If total_ref_phones is zero, avoid ZeroDivisionError.
    print("total phones in reference:", total_ref_phones)
    print("total edit distance:      ", total_edit_distance)
    if total_ref_phones:
        print("phone error rate:         ", total_edit_distance / total_ref_phones)
    else:
        print("phone error rate:         ", "N/A (no reference phones found)")
    print(
        "word error rate:         ",
        (total_mismatches / len(ref_lookup)),
    )
