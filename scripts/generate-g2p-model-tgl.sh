#!/bin/bash

./get-csv-train-tgl-files.sh

./get-log-train-tgl-files.sh

./create-dict-tgl.py

phonetisaurus-train --lexicon train_tgl.dict --seq2_del
