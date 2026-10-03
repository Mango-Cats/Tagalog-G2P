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

The G2P wasn't picked just for having the lowest score. One candidate from each main family of G2P,
rule-based, statistical and neural, each built for Filipino or covering it, was scored by phone
error rate (PER) on the same held-out Wiktionary test split (2,171 words) and the same 10
cross-validation folds, and the differences were tested for significance
([`G2P_compare`](notebook/G2P_compare.ipynb)). The decision rule was fixed before the results:
the lowest test PER, a significant lead over every other candidate, and the lowest mean fold PER.

| Candidate | Family | Test PER | Test WER | Fold PER (10 folds) |
| --- | --- | --- | --- | --- |
| Epitran `tgl-Latn` (Mortensen et al., 2018) | rule-based | 4.80% | 28.79% | 5.23% ± 0.25%\* |
| **WFST** (Phonetisaurus, this repo) | statistical | **0.81%** | **5.85%** | **0.99% ± 0.06%** |
| [filipino-byt5-g2p](https://huggingface.co/lowestofthelow/filipino-byt5-g2p) (Marqueses et al., 2026) | neural, existing model | 1.07% | 6.77% | 1.21% ± 0.13%\* |
| CharsiuG2P fine-tuned on this data (Zhu et al., 2022) | neural, same data as the WFST | not run yet (needs a GPU) | | |

\* Scored on each fold without retraining; the WFST model is retrained on each fold.

The WFST model meets the rule. Its lead is significant over both other candidates (paired
bootstrap 95% CI and Wilcoxon signed-rank test with Holm correction): +0.26 PER points over
filipino-byt5-g2p (95% CI 0.04 to 0.50) and +3.99 over Epitran (95% CI 3.63 to 4.35).
filipino-byt5-g2p was trained on labels from the same Wiktionary source, and 38.5% of the test
words appear in its training sentences. On the test words it hasn't seen, its PER is 1.17%,
against 0.71% for the WFST model.

The fine-tuned CharsiuG2P is the controlled neural comparison: it learns from exactly the same data
as the WFST model. It joins the table once [`ByT5_finetune`](notebook/ByT5_finetune.ipynb) has run
on a GPU.

Before splitting, 11 broken source entries are dropped: 4 with symbols outside the Filipino phoneme
inventory (e.g. tone numbers) and 7 truncated transcriptions (`insenso` as /sj/).

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

The notebooks come in two stages. Run each stage in the order listed.

**1. Earlier experiments**, which set the WFST's settings:

| Notebook | What it does |
| --- | --- |
| [`Aquino_eval`](notebook/Aquino_eval.ipynb) | WFST models on the Aquino & Tsang speech-corpus transcriptions: a baseline (default settings with `--seq2_del`), a model on cleaned data, and a grid search over the settings |
| [`Pron_eval`](notebook/Pron_eval.ipynb) | Checks whether the grid-search settings carry over to the WikiPron splits. They don't, so the baseline settings are kept |

**2. Choosing the G2P**, with every candidate on the same Wiktionary test split and folds:

| Notebook | Candidate | Runs in |
| --- | --- | --- |
| [`Wik_eval`](notebook/Wik_eval.ipynb) | WFST (statistical). Writes the test split, validation split and folds every candidate shares, and `notebook/train/cwik_model.fst`, the model the CLI uses | container |
| [`Epitran_eval`](notebook/Epitran_eval.ipynb) | Epitran `tgl-Latn` (rule-based) | container |
| [`ByT5_eval`](notebook/ByT5_eval.ipynb) | filipino-byt5-g2p (neural, existing model), including the test words it saw in training | container (a CPU is enough) |
| [`ByT5_finetune`](notebook/ByT5_finetune.ipynb) | CharsiuG2P fine-tuned and cross-validated on the WFST's data (neural, controlled) | Windows with an NVIDIA GPU, in `.venv-windows` (setup at the top of the notebook) |
| [`G2P_compare`](notebook/G2P_compare.ipynb) | All candidates side by side, significance tests, the choice of G2P and the limits of the comparison. Rerun it after `ByT5_finetune` to add the fine-tuned model | container |

The candidate notebooks need `torch`, `transformers`, `epitran` and `scipy` on top of the
container's packages: `pip install -r requirements.txt`.

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
- **filipino-byt5-g2p** (the ByT5 model in `ByT5_eval`): Marqueses, L. B., Silva, P. G. G.,
  Cabatay, C., Tan, E. A., & Laguna, A. F. (2026). Towards stress-aware sentence-level Filipino
  G2P with weakly-supervised ByT5 fine-tuning. *NLPIR 2026*. https://arxiv.org/abs/2609.09974
- **Epitran**: Mortensen, D. R., Dalmia, S., & Littell, P. (2018). Epitran: Precision G2P for many
  languages. *LREC 2018*. https://aclanthology.org/L18-1429/
- **CharsiuG2P** (the base model in `ByT5_finetune`): Zhu, J., Zhang, C., & Jurgens, D. (2022). ByT5
  model for massively multilingual grapheme-to-phoneme conversion. *Interspeech 2022*.
  https://arxiv.org/abs/2204.03067
- **Speech-corpus transcriptions and `utils/` code**: Aquino, Tsang, Lucas &
  de Leon (2019). G2P and ASR techniques for low-resource phonetic
  transcription of Tagalog, Cebuano, and Hiligaynon. *ISMAC 2019*.
  https://doi.org/10.1109/ISMAC.2019.8836168

## License

[MIT](LICENSE), except the code in [`utils/`](utils/), which is adapted from
Aquino & Tsang's project and isn't covered by it. See [NOTICE](NOTICE).
