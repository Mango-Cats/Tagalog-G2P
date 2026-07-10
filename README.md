# Taglog-G2P

Tagalog **g**rapheme-to-**p**honeme (G2P) systems and data.

> Everything is still *cooking*. Systems, data, and this README are
> all subject to change.

## How To

Taglog-G2P is built on [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus)
(WFST-based G2P). Everything runs inside the project's Docker container:

```bash
docker build -t phonetisaurus .
docker run --rm -it -v "${PWD}:/work" phonetisaurus bash
```

On Windows PowerShell, the same two steps are wrapped in a script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./run_phonetisaurus.ps1
```

**Jupyter**: The experiments live in [notebook/](notebook/) — training,
evaluation, and error analysis are all notebook-driven.

## CLI: words → IPA phones

`tagalog_g2p.py` transcribes Tagalog words to IPA using the WFST trained
in [notebook/Wik_eval.ipynb](notebook/Wik_eval.ipynb) on
`data/extra data/clean_tgl_wik.csv` (`notebook/train/cwik_model.fst`).
No install step.

### Quick start

Run it inside the project container:

```bash
python tagalog_g2p.py araw               # ʔ a ɾ a w
python tagalog_g2p.py kamusta po         # two lines, one per word
python tagalog_g2p.py "kamusta po"       # same as above
```

Output is always the single best pronunciation as space-separated phones,
one line per input word.

### Behavior

- Decodes with the Phonetisaurus Python binding when available (the
  container's `/usr/local/bin/python3`), and otherwise falls back to
  shelling out to `phonetisaurus-g2pfst`.
- Input is NFC-normalized and lowercased (the model's alphabet is
  lowercase). Characters unseen in training are an error.
- The model emits no stress marks (the training dict has none), so
  output is unstressed broad IPA.

### Retraining

See [notebook/Wik_eval.ipynb](notebook/Wik_eval.ipynb), or run:

```bash
phonetisaurus-train --lexicon notebook/dicts/cwik_trainval.dict --seq2_del --model notebook/train/cwik_model
```

## Standalone executable

The CLI can be packaged as a single self-contained executable — model,
Phonetisaurus binding, and OpenFst libraries all bundled — so it runs
without Docker, Python, or a Phonetisaurus install. Build it inside the
project container:

```bash
./scripts/build-executable.sh        # → dist/tagalog-g2p (~13 MB)
```

Then copy `dist/tagalog-g2p` anywhere and run it directly:

```bash
./tagalog-g2p araw                   # ʔ a ɾ a w
```

The executable targets Linux x86_64 with glibc ≥ 2.31 (any mainstream
distro from ~2020 on, including WSL2). It is not a native Windows or
macOS binary — those platforms would need Phonetisaurus rebuilt natively
first.

## Moving Around

The project has three main parts:

1. [notebook/](notebook/): training and evaluation notebooks
   (`Pron_eval`, `Wik_eval`, `Aquino_eval`), plus their dictionaries,
   trained models, and outputs.
2. [utils/](utils/): Python helpers for alignment, G2P parsing,
   preprocessing, and accuracy metrics.
3. [scripts/](scripts/): shell scripts for collecting dataset file
   lists and building the standalone executable.
