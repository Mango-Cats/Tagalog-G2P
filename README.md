# Taglog-G2P: WFST Grapheme-to-Phoneme Conversion Project on Tagalog.

**Dataset**: Lee, J. L., Ashby, L. F.E., Garza, M. E., Lee-Sikka, Y., Miller, S., Wong, A., McCarthy, A. D., & Gorman, K. (2020). Massively multilingual pronunciation mining with WikiPron [Dataset]. https://github.com/CUNY-CL/wikipron

**Motivation**: Grapheme-to-phoneme (G2P) conversion is a core component of speech technologies such as text-to-speech and automatic speech recognition, yet low-resource languages like Tagalog have little pronunciation data to train on.

**Goal**: Train and evaluate WFST-based (Phonetisaurus) G2P models for Tagalog on Wiktionary pronunciation data, analyze their errors, and package the best model as a standalone command-line tool.

## Set Up

> This project runs inside a [Docker](https://www.docker.com/) container, which provides [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus) and all other dependencies (see the [`Dockerfile`](Dockerfile)).

1. Simply clone the repository.
2. Run `docker build -t phonetisaurus .` to build the container image.
3. Run `docker run --rm -it -v "${PWD}:/work" phonetisaurus bash` to enter the container.

On Windows PowerShell, steps 2–3 are wrapped in a script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./run_phonetisaurus.ps1
```

## Model

We use a **WFST joint-sequence model** trained with Phonetisaurus. The final
model (`notebook/train/cwik_model.fst`) is trained in
[`notebook/Wik_eval.ipynb`](notebook/Wik_eval.ipynb) on cleaned WikiPron
Tagalog data, and every model is scored by phone error rate (PER) on a
held-out Tagalog test set.

## CLI: words → IPA phones

`tagalog_g2p.py` transcribes Tagalog words to IPA using the final model.
No install step — run it inside the container:

```bash
python tagalog_g2p.py araw               # ʔ a ɾ a w
python tagalog_g2p.py kamusta po         # two lines, one per word
python tagalog_g2p.py "kamusta po"       # same as above
```

Output is always the single best pronunciation as space-separated phones,
one line per input word. Input is NFC-normalized and lowercased (the
model's alphabet is lowercase); characters unseen in training are an
error. The model emits no stress marks (the training dict has none), so
output is unstressed broad IPA.

To retrain the model, see [`notebook/Wik_eval.ipynb`](notebook/Wik_eval.ipynb), or run:

```bash
phonetisaurus-train --lexicon notebook/dicts/cwik_trainval.dict --seq2_del --model notebook/train/cwik_model
```

### Standalone executable

The CLI can be packaged as a single self-contained executable — model,
Phonetisaurus binding, and OpenFst libraries all bundled — so it runs
without Docker, Python, or a Phonetisaurus install. Build it inside the
container, then copy `dist/tagalog-g2p` anywhere and run it directly:

```bash
./scripts/build-executable.sh        # → dist/tagalog-g2p (~13 MB)
./dist/tagalog-g2p araw              # ʔ a ɾ a w
```

The executable targets Linux x86_64 with glibc ≥ 2.31 (any mainstream
distro from ~2020 on, including WSL2). It is not a native Windows or
macOS binary — those platforms would need Phonetisaurus rebuilt natively
first.

## Notebooks

View the notebooks enumerated below, also view the notebooks in the order
indicated. Each one both trains models and analyzes their errors; run them
inside the Docker container.

1. [`notebook/Aquino_eval.ipynb`](notebook/Aquino_eval.ipynb): trains and
   evaluates models on the Aquino & Tsang Tagalog speech-corpus
   transcriptions — a baseline model, a model on cleaned data, and a
   hyperparameter-optimized model — with error analysis and conclusions.
1. [`notebook/Pron_eval.ipynb`](notebook/Pron_eval.ipynb): trains and
   evaluates baseline and tuned models from the `train.tsv`/`test.tsv`
   pronunciation splits, reporting PER and WER, with error analysis
   including vowel-height confusions (o↔u, e↔i).
1. [`notebook/Wik_eval.ipynb`](notebook/Wik_eval.ipynb): the final phonemic
   evaluation on cleaned WikiPron data — coverage-safe 80/10/10 split,
   10-fold cross-validation, held-out test PER — with error analysis of
   glottal-stop position and vowel-height confusions. Trains the model
   shipped with the CLI.

## Data

The pronunciation data used in the project is mined from Wiktionary by the
WikiPron project (Lee et al., 2020), available at
[github.com/CUNY-CL/wikipron](https://github.com/CUNY-CL/wikipron) under the
Apache 2.0 license (the underlying Wiktionary data is CC BY-SA 3.0). The
speech-corpus transcriptions come from Aquino, Tsang, Lucas & de Leon's
University of the Philippines Diliman project (*DSP01: A hybrid
grapheme-to-phoneme and speech recognition system for automated phonetic
transcription of speech data in Tagalog, Cebuano, and Hiligaynon*;
published as "G2P and ASR techniques for low-resource phonetic
transcription of Tagalog, Cebuano, and Hiligaynon," ISMAC 2019,
https://doi.org/10.1109/ISMAC.2019.8836168), which the helper code in
[`utils/`](utils/) is also adapted from — see [NOTICE](NOTICE).

Raw data is expected in the `data/` directory (not tracked in git); the
processed dictionaries and train/test splits the notebooks produce live in
[`notebook/dicts/`](notebook/dicts/).

## License

This project is licensed under the [MIT License](LICENSE), with one
exception: the helper code in [`utils/`](utils/) is adapted from Aquino &
Tsang's project (see [Data](#data) above) and is not covered by that
license. See [NOTICE](NOTICE) for details.
