#!/usr/bin/env python3
"""tagalog-g2p: print the IPA transcription of a single Tagalog word.

Uses the Phonetisaurus WFST trained in notebook/Wik_eval.ipynb on
data/extra data/clean_tgl_wik.csv (notebook/train/cwik_model.fst).

Usage:
    python tagalog_g2p.py kamusta            # kamusta   (joined IPA)
    python tagalog_g2p.py --phones araw      # ʔ a ɾ a w
    python tagalog_g2p.py -n 3 kamusta       # 3 candidates, one per line
"""
import argparse
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ENV_MODEL = "TAGALOG_G2P_MODEL"
DEFAULT_MODEL = Path(__file__).resolve().parent / "notebook" / "train" / "cwik_model.fst"
BINARY = "phonetisaurus-g2pfst"
# Phonetisaurus prints this to stderr (not stdout) for each input character it
# cannot map; we scrape it to detect out-of-alphabet input.
UNKNOWN_SYM = re.compile(r"Symbol: '(.+?)' not found in input symbols table")


def resolve_model(model_arg):
    """Pick the model .fst to use and confirm it exists on disk.

    Resolution order: explicit -m/--model argument, then the TAGALOG_G2P_MODEL
    environment variable, then the model shipped in this repo. Raises
    RuntimeError with a fix-it message if the chosen path is not a file.
    """
    path = Path(model_arg or os.environ.get(ENV_MODEL) or DEFAULT_MODEL)
    if not path.is_file():
        raise RuntimeError(
            f"G2P model not found: {path}. Pass -m/--model, set ${ENV_MODEL}, "
            "or run from the Taglog-G2P repo (notebook/train/cwik_model.fst)."
        )
    return path


def transcribe(word, model, nbest):
    """Run the WFST decoder on one word and return its pronunciations.

    Returns (prons, unknown): `prons` is a list of up to `nbest` phone lists
    (best first), and `unknown` is the sorted set of input characters the model
    had no symbol for. Raises RuntimeError if the decoder binary is missing or
    exits non-zero.
    """
    try:
        proc = subprocess.run(
            [BINARY, f"--model={model}", f"--word={word}", f"--nbest={nbest}"],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(f"{BINARY} not found on PATH (run inside the project container)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"{BINARY} failed: {e.stderr.strip()}")

    unknown = sorted(set(UNKNOWN_SYM.findall(proc.stderr)))
    # Each stdout line is: word\tscore\tspace-separated phones. Keep the phones,
    # skipping any blank/malformed lines.
    prons = []
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[2].strip():
            prons.append(parts[2].split())
    return prons, unknown


def main(argv=None):
    """Parse arguments, transcribe the word, and print the IPA (exit code 0/1)."""
    parser = argparse.ArgumentParser(
        description="Tagalog grapheme-to-phoneme (IPA) using a Phonetisaurus WFST."
    )
    parser.add_argument("word", help="word to transcribe")
    parser.add_argument("-m", "--model",
                        help=f"path to .fst model (default: notebook/train/cwik_model.fst; env {ENV_MODEL})")
    parser.add_argument("-n", "--nbest", type=int, default=1,
                        help="number of candidate pronunciations (default 1)")
    parser.add_argument("--phones", action="store_true",
                        help="print space-separated phones instead of a joined IPA string")
    parser.add_argument("--no-strict", action="store_true",
                        help="warn instead of failing on characters unseen in training")
    args = parser.parse_args(argv)

    # The model's grapheme alphabet is lowercase and NFC; match it, and reject
    # empty or multi-token input (this tool handles one word at a time).
    word = unicodedata.normalize("NFC", args.word).strip().lower()
    if not word or any(ch.isspace() for ch in word):
        parser.error(f"expected a single non-empty word, got {args.word!r}")

    try:
        model = resolve_model(args.model)
        prons, unknown = transcribe(word, model, args.nbest)
        # Unknown characters are silently dropped by the decoder, so its output
        # is unreliable; fail loudly unless the user opted out with --no-strict.
        if unknown:
            msg = (f"{word!r}: character(s) not in the model alphabet: "
                   f"{', '.join(map(repr, unknown))}; output would be unreliable")
            if not args.no_strict:
                raise RuntimeError(msg)
            print(f"tagalog-g2p: warning: {msg}", file=sys.stderr)
        if not prons:
            raise RuntimeError(f"no pronunciation produced for {word!r}")
    except RuntimeError as e:
        print(f"tagalog-g2p: error: {e}", file=sys.stderr)
        return 1

    # One line per candidate: joined IPA string, or space-separated phones.
    for phones in prons:
        print(" ".join(phones) if args.phones else "".join(phones))
    return 0


if __name__ == "__main__":
    sys.exit(main())
