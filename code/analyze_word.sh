#!/usr/bin/env bash

SEGMENT_MARKER=${SEGMENT_MARKER:--}

count_segments() {
    local analyzed_word=$1
    echo "${analyzed_word}" \
        | tr "${SEGMENT_MARKER}" "\n" \
        | grep -v '^\s*$' \
        | wc -l
}

export -f count_segments

count_segments $(cat -)
