#!/bin/bash

SEARCH_PATH="../data/_clean/valref"

counter(){
    for file in "$1"/*
    do
        if [ -d "$file" ]
        then
            counter "$file"
        else
            if [ "${file: -4}" == ".csv" ]
            then
                echo "$file"
            fi
        fi
    done
}

counter "$SEARCH_PATH" > ../notebook/paths/csv-clean-valref-files.txt
