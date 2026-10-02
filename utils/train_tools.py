"""Phonetisaurus training helper shared by the evaluation notebooks."""
import shutil
import subprocess
from pathlib import Path


def train_model(lexicon, model_name, model_dir, work_dir, *flags):
    """Train a Phonetisaurus model, keeping only its .fst.

    phonetisaurus-train writes <model_name>.corpus, .arpa and .fst into
    work_dir (a temp dir); only the .fst is copied into model_dir, which is
    created if missing. Extra phonetisaurus-train options go in `flags`.
    Returns the CompletedProcess (stderr holds the training log).
    """
    work_dir, model_dir = Path(work_dir), Path(model_dir)
    result = subprocess.run(
        [
            "phonetisaurus-train",
            "--lexicon", str(lexicon),
            "--dir_prefix", str(work_dir),
            "--model_prefix", model_name,
            *map(str, flags),
        ],
        capture_output=True, text=True,
    )
    fst = work_dir / f"{model_name}.fst"
    if fst.is_file():
        model_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(fst, model_dir / fst.name)
    return result
