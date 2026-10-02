# Taglog-G2P

Tagalog grapheme-to-phoneme (G2P) conversion with a WFST model trained with
[Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus) on
[WikiPron](https://github.com/CUNY-CL/wikipron) pronunciation data.

```console
$ python tagalog_g2p.py araw kamusta
ʔ a ɾ a w
k a m u s t a
```

## Results

Phone error rate (PER) and word error rate (WER) on the held-out Wiktionary
test split (2,171 words):

| Model | PER | WER |
| --- | --- | --- |
| WFST (Phonetisaurus, this repo) | **0.88%** | **6.08%** |
| ByT5 ([filipino-byt5-g2p](https://huggingface.co/lowestofthelow/filipino-byt5-g2p)) | 1.64% | 9.07% |

10-fold cross-validation PER of the WFST model: 1.03% ± 0.12%.

## Installation

Everything runs in a Docker container that builds Phonetisaurus and its
dependencies (see the [`Dockerfile`](Dockerfile)). From the repository root:

```bash
docker build -t phonetisaurus .
docker run --rm -it -v "${PWD}:/work" phonetisaurus bash
```

On Windows PowerShell, [`run_phonetisaurus.ps1`](run_phonetisaurus.ps1) runs
both commands:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./run_phonetisaurus.ps1
```

## Usage

### Command line

Inside the container:

```bash
python tagalog_g2p.py araw            # ʔ a ɾ a w
python tagalog_g2p.py "kamusta po"    # one line per word
```

Each word gets its best pronunciation as space-separated broad IPA phones,
without stress marks. Input is lowercased and NFC-normalized; characters the
model never saw in training are an error.

### Standalone executable

Bundle the CLI, model and Phonetisaurus libraries into one file that runs
without Docker or Python:

```bash
./scripts/build-executable.sh    # builds dist/tagalog-g2p (~13 MB)
./dist/tagalog-g2p araw
```

The executable runs on Linux x86_64 with glibc 2.31 or newer, including WSL2.

## Notebooks

Run them in this order inside the container:

| Notebook | Description |
| --- | --- |
| [`Aquino_eval`](notebook/Aquino_eval.ipynb) | Baseline, cleaned-data and tuned models on the Aquino & Tsang speech-corpus transcriptions |
| [`Pron_eval`](notebook/Pron_eval.ipynb) | Baseline and tuned models on the `train.tsv`/`test.tsv` pronunciation splits |
| [`Wik_eval`](notebook/Wik_eval.ipynb) | The final model: 80/10/10 split, 10-fold cross-validation, test PER and error analysis. Writes `notebook/train/cwik_model.fst`, the model the CLI uses |
| [`ByT5_eval`](notebook/ByT5_eval.ipynb) | A neural ByT5 model on the same test split, compared with the WFST model. Run `Wik_eval` first; needs `torch` and `transformers` (`pip install -r requirements.txt`) |

Raw data goes in `data/`, which isn't tracked in git. The notebooks write
their splits, models, predictions and error reports under `notebook/`.

## Project structure

```
├── tagalog_g2p.py   # command-line tool
├── notebook/        # evaluation notebooks and the trained model
├── utils/           # alignment and scoring helpers (third-party, see NOTICE)
├── scripts/         # data preparation and executable build scripts
└── Dockerfile       # Phonetisaurus, OpenFst and MITLM build
```

## Data and citations

- **WikiPron** (Apache 2.0; the Wiktionary data is CC BY-SA 3.0):
  Lee, J. L., Ashby, L. F. E., Garza, M. E., Lee-Sikka, Y., Miller, S.,
  Wong, A., McCarthy, A. D., & Gorman, K. (2020). Massively multilingual
  pronunciation mining with WikiPron [Dataset].
  https://github.com/CUNY-CL/wikipron
- **Speech-corpus transcriptions and `utils/` code**: Aquino, Tsang, Lucas &
  de Leon (2019). G2P and ASR techniques for low-resource phonetic
  transcription of Tagalog, Cebuano, and Hiligaynon. *ISMAC 2019*.
  https://doi.org/10.1109/ISMAC.2019.8836168

## License

[MIT](LICENSE), except the code in [`utils/`](utils/), which is adapted from
Aquino & Tsang's project and isn't covered by it. See [NOTICE](NOTICE).
