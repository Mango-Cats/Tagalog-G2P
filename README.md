# Taglog-G2P
Repository for the development of systems and data related to Tagalog G2P.

## How to run WFST:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./run_phonetisaurus.ps1

## CLI: word → IPA

`tagalog_g2p.py` transcribes a single Tagalog word to IPA using the WFST
trained in `notebook/Wik_eval.ipynb` on `data/extra data/clean_tgl_wik.csv`
(`notebook/train/cwik_model.fst`). Run it inside the project container
(needs `phonetisaurus-g2pfst` on PATH); stdlib only, no install step.

```
python tagalog_g2p.py kamusta            # kamusta   (joined IPA, single best)
python tagalog_g2p.py --phones araw      # ʔ a ɾ a w (space-separated phones)
python tagalog_g2p.py -n 3 kamusta       # top 3 candidates, one per line
python tagalog_g2p.py -m other.fst word  # use a different model (or set $TAGALOG_G2P_MODEL)
```

Input is NFC-normalized and lowercased (the model's alphabet is lowercase).
Characters unseen in training are an error by default; `--no-strict` prints
the degraded output with a warning instead. Note: this model emits no stress
marks (the training dict has none), so output is unstressed broad IPA.

To retrain the model, see `notebook/Wik_eval.ipynb`, or run:

```
phonetisaurus-train --lexicon notebook/dicts/cwik_trainval.dict --seq2_del --model notebook/train/cwik_model
```
