#!/usr/bin/env bash

# This script transforms a stream of words into a TSV with the original word and its segmented version

# Temporary files to hold the original and segmented words
temp_for_orig=$(mktemp)
temp_for_seg=$(mktemp)

# Read from stdin, segment the words, and output the original and segmented words
cat - | tee $temp_for_orig | bash code/segment_words.sh > $temp_for_seg

# Paste the original and segmented words into a TSV
paste $temp_for_orig $temp_for_seg

# Cleanup
rm $temp_for_orig $temp_for_seg
