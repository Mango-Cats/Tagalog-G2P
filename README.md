# Taglog-G2P
Repository for the development of systems and data related to Tagalog G2P.

## How to run WFST:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./run_phonetisaurus.ps1

## CLI: words → IPA phones

`tagalog_g2p.py` transcribes Tagalog words to IPA using the WFST
trained in `notebook/Wik_eval.ipynb` on `data/extra data/clean_tgl_wik.csv`
(`notebook/train/cwik_model.fst`). Run it inside the project container
(needs `phonetisaurus-g2pfst` on PATH); stdlib only, no install step.

Output is always the single best pronunciation as space-separated phones,
one line per input word.

```
python tagalog_g2p.py araw               # ʔ a ɾ a w
python tagalog_g2p.py kamusta po         # two lines, one per word
python tagalog_g2p.py "kamusta po"       # same as above
```

Input is NFC-normalized and lowercased (the model's alphabet is lowercase).
Characters unseen in training are an error. Note: this model emits no stress
marks (the training dict has none), so output is unstressed broad IPA.

To retrain the model, see `notebook/Wik_eval.ipynb`, or run:

```
phonetisaurus-train --lexicon notebook/dicts/cwik_trainval.dict --seq2_del --model notebook/train/cwik_model
```
