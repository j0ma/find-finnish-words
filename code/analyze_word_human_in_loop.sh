#!/usr/bin/env bash

# This script is used to find the words with the most morphemes per word.
# The script will display the words with the most morphemes per word in the database and allow the user to amend the machine-generated segmentations.
# After the user has amended the segmentations, the script will reanalyze the words and display the results.

db=$1

./code/browser find-unique-words --db $1 \
    | bash code/add_segmented_column.sh \
    | bash code/add_nsegm_column.sh \
    | vipe \
    | cut -f1,2  \
    | bash code/add_nsegm_column.sh
