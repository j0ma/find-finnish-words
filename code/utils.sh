#!/usr/bin/env bash

export SEGMENT_MARKER=${SEGMENT_MARKER:--}

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
