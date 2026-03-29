# ============================================================
# Phonetisaurus G2P — Multi-stage Dockerfile
#
# Build stage  : compiles OpenFst 1.7.2 + MITLM + Phonetisaurus
# Runtime stage: copies only the artifacts needed to run
#
# Fully self-contained — no local Phonetisaurus source needed.
# All deps are cloned/downloaded during the build.
#
# Build:
#   docker build -t phonetisaurus .
#
# Run (interactive, mount your data under /work):
#   docker run --rm -it -v $(pwd):/work phonetisaurus bash
#
# Quick smoke-test (no mount needed):
#   docker run --rm phonetisaurus "phonetisaurus-g2pfst --help"
# ============================================================

# ── Build stage ──────────────────────────────────────────────
# Pinned to Debian Bullseye (GCC 10) — OpenFst 1.7.2 fails to compile
# with GCC 14 (Bookworm/Trixie) due to unique_ptr assignment changes in C++14+
FROM python:3.10-bullseye AS build

WORKDIR /build

# --- System build deps ----------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        g++ \
        autoconf \
        autoconf-archive \
        automake \
        libtool \
        make \
        gfortran \
        wget \
        tar \
        gawk \
    && rm -rf /var/lib/apt/lists/*

# --- OpenFst 1.7.2 -------------------------------------------
# Required flags: --enable-far for archive support,
#                 --enable-ngram-fsts for phonetisaurus training
RUN wget -q http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.7.2.tar.gz \
    && tar -xzf openfst-1.7.2.tar.gz \
    && cd openfst-1.7.2 \
    && ./configure \
        --enable-static \
        --enable-shared \
        --enable-far \
        --enable-ngram-fsts \
    && make -j"$(nproc)" \
    && make install \
    && ldconfig \
    && cd /build && rm -rf openfst-1.7.2 openfst-1.7.2.tar.gz

# --- MITLM (language model estimation) -----------------------
# Needed by the phonetisaurus-train wrapper (estimate-ngram)
RUN git clone --depth 1 https://github.com/mitlm/mitlm.git \
    && cd mitlm \
    && autoreconf -i \
    && ./configure \
    && make -j"$(nproc)" \
    && make install \
    && ldconfig \
    && cd /build && rm -rf mitlm

# --- Python binding dep --------------------------------------
RUN pip3 install --no-cache-dir pybindgen

# --- Phonetisaurus -------------------------------------------
RUN git clone --depth 1 https://github.com/AdolfVonKleist/Phonetisaurus.git /build/phonetisaurus

WORKDIR /build/phonetisaurus

RUN ./configure --enable-python \
    && make -j"$(nproc)" \
    && make install \
    && ldconfig

# Install the Python package from the python/ subdirectory
RUN cd python \
    && cp ../.libs/Phonetisaurus.so . \
    && python3 setup.py install


# ── Runtime stage ────────────────────────────────────────────
FROM python:3.10-slim-bullseye AS runtime

# gfortran runtime is needed by MITLM shared lib at run time
RUN apt-get update && apt-get install -y --no-install-recommends \
        gfortran \
        curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
        pandas \
        unidecode \
        jupyterlab

WORKDIR /setup

# --- Python package ------------------------------------------
COPY --from=build /build/phonetisaurus/python/ .
COPY --from=build /build/phonetisaurus/.libs/Phonetisaurus.so .
RUN python3 setup.py install

# --- OpenFst shared libs & plugins ---------------------------
# Use globs — soname version depends on build env, not the OpenFst version
COPY --from=build /usr/local/lib/fst/        /usr/local/lib/fst/
COPY --from=build /usr/local/lib/libfst*.so* /usr/local/lib/

# --- MITLM shared lib ----------------------------------------
# Copy the versioned .so and create the soname symlink so the
# dynamic linker can resolve libmitlm.so.1 at runtime.
COPY --from=build /usr/local/lib/libmitlm.so.1.0.0      /usr/local/lib/
RUN ln -sf /usr/local/lib/libmitlm.so.1.0.0 /usr/local/lib/libmitlm.so.1

# --- Executables ---------------------------------------------
COPY --from=build /usr/local/bin/phonetisaurus-align     /usr/local/bin/
COPY --from=build /usr/local/bin/phonetisaurus-arpa2wfst /usr/local/bin/
COPY --from=build /usr/local/bin/phonetisaurus-g2pfst    /usr/local/bin/
COPY --from=build /usr/local/bin/phonetisaurus-g2prnn    /usr/local/bin/
COPY --from=build /usr/local/bin/estimate-ngram          /usr/local/bin/
COPY --from=build /usr/local/bin/rnnlm                   /usr/local/bin/

# Wrapper scripts (phonetisaurus-train, phonetisaurus-apply, etc.)
COPY --from=build /build/phonetisaurus/src/scripts/      /usr/local/bin/

RUN ldconfig

# --- Working directory for user data -------------------------
# Mount your lexicons / word lists here:
#   docker run --rm -it -v $(pwd):/work phonetisaurus bash
WORKDIR /work

CMD ["/bin/bash"]
