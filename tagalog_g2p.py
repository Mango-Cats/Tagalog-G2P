#!/usr/bin/env python3
"""tagalog-g2p: print the IPA phones of one or more Tagalog words.

Uses the Phonetisaurus WFST trained in notebook/Wik_eval.ipynb on
data/extra data/clean_tgl_wik.csv (notebook/train/cwik_model.fst).

Output is always the best (top-1) pronunciation as space-separated phones,
one line per input word.

Usage:
    python tagalog_g2p.py araw               # ʔ a ɾ a w
    python tagalog_g2p.py kamusta po         # two lines, one per word
    python tagalog_g2p.py "kamusta po"       # same as above
"""
import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

MODEL = Path(__file__).resolve().parent / "notebook" / "train" / "cwik_model.fst"
BINARY = "phonetisaurus-g2pfst"
# Phonetisaurus prints this to stderr (not stdout) for each input character it
# cannot map; we scrape it to detect out-of-alphabet input.
UNKNOWN_SYM = re.compile(r"Symbol: '(.+?)' not found in input symbols table")


def resolve_model():
    """Confirm the repo's model .fst exists on disk and return its path."""
    if not MODEL.is_file():
        raise RuntimeError(
            f"G2P model not found: {MODEL}. Run from the Taglog-G2P repo "
            "(notebook/train/cwik_model.fst)."
        )
    return MODEL


def transcribe(word, model):
    """Run the WFST decoder on one word and return its best pronunciation.

    Returns (phones, unknown): `phones` is the top-1 phone list (or None if
    the decoder produced nothing), and `unknown` is the sorted set of input
    characters the model had no symbol for. Raises RuntimeError if the decoder
    binary is missing or exits non-zero.
    """
    try:
        proc = subprocess.run(
            [BINARY, f"--model={model}", f"--word={word}", "--nbest=1"],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(f"{BINARY} not found on PATH (run inside the project container)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"{BINARY} failed: {e.stderr.strip()}")

    unknown = sorted(set(UNKNOWN_SYM.findall(proc.stderr)))
    # Each stdout line is: word\tscore\tspace-separated phones. Keep the first
    # well-formed line's phones.
    phones = None
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[2].strip():
            phones = parts[2].split()
            break
    return phones, unknown


def main(argv=None):
    """Parse arguments, transcribe each word, and print the phones (exit code 0/1)."""
    parser = argparse.ArgumentParser(
        description="Tagalog grapheme-to-phoneme (IPA) using a Phonetisaurus WFST."
    )
    parser.add_argument("words", nargs="+", help="word(s) to transcribe")
    args = parser.parse_args(argv)

    # The model's grapheme alphabet is lowercase and NFC; match it. Splitting
    # after joining also handles quoted multi-word input ("kamusta po").
    words = unicodedata.normalize("NFC", " ".join(args.words)).lower().split()
    if not words:
        parser.error("expected at least one non-empty word")

    try:
        model = resolve_model()
        for word in words:
            phones, unknown = transcribe(word, model)
            # Unknown characters are silently dropped by the decoder, so its
            # output is unreliable; fail loudly.
            if unknown:
                raise RuntimeError(
                    f"{word!r}: character(s) not in the model alphabet: "
                    f"{', '.join(map(repr, unknown))}; output would be unreliable"
                )
            if not phones:
                raise RuntimeError(f"no pronunciation produced for {word!r}")
            # Best pronunciation as space-separated phones, one line per word.
            print(" ".join(phones))
    except RuntimeError as e:
        print(f"tagalog-g2p: error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
