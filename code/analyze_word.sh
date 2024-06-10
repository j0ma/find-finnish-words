#!/usr/bin/env bash

SEGMENT_MARKER=${SEGMENT_MARKER:--}

count_segments() {
    local analyzed_word=$1
    echo "${analyzed_word}" \
        | tr "${SEGMENT_MARKER}" "\n" \
        | grep -v '^\s*$' \
        | wc -l \
        | cut -f1 -d' '
}

augment_with_count() {
    local analyzed_word=$1
    local count=$(count_segments "${analyzed_word}")
    echo "${analyzed_word} ${count}"
}

segment_word () {
    local word=$1
    echo ${word} | bash code/segment_words.sh
}

analyze_with_count() {
    local word=$1
    echo $word
    local analyzed_word=$(segment_word "${word}")
    local count=$(count_segments "${analyzed_word}")
    printf "%s\t%s\t%s\n" "${word}" "${analyzed_word}" "${count}"
}

export -f count_segments
export -f augment_with_count
export -f segment_word
export -f analyze_with_count

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
