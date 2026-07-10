# -*- mode: python ; coding: utf-8 -*-
# One-file, self-contained tagalog-g2p executable: bundles tagalog_g2p.py,
# the Phonetisaurus C++ binding, the OpenFst libraries, and the trained model.
# Build inside the project container with scripts/build-executable.sh.
import glob

# The binding is installed as an old-style egg; locate it rather than pin the
# Python minor version.
egg = glob.glob("/usr/local/lib/python3.*/site-packages/phonetisaurus-*.egg")[0]

a = Analysis(
    ["tagalog_g2p.py"],
    pathex=[egg],
    binaries=[
        # OpenFst loads this plugin via dlopen, so PyInstaller's dependency
        # scan cannot discover it.
        ("/usr/local/lib/fst/ngram-fst.so", "."),
    ],
    datas=[("notebook/train/cwik_model.fst", ".")],
    hiddenimports=["Phonetisaurus"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="tagalog-g2p",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
)
