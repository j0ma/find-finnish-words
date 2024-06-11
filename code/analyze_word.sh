#!/usr/bin/env bash

. code/utils.sh

# working dir
temp_dir=$(mktemp -d)

# first output all the words there
cat - > ${temp_dir}/words

# then segment all the words
cat ${temp_dir}/words | bash code/segment_words.sh > ${temp_dir}/segmented_words

# then count the segments
cat ${temp_dir}/segmented_words | while read segmword; do count_segments $segmword >> ${temp_dir}/segment_counts; done

# finally paste everything togehter
## first the header
printf "%s\t%s\t%s\n" "word" "segmented_word" "segment_count" > ${temp_dir}/output
## then the data
paste ${temp_dir}/words ${temp_dir}/segmented_words ${temp_dir}/segment_counts > ${temp_dir}/output

# output the result
cat ${temp_dir}/output
