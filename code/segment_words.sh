#!/usr/bin/env bash

SEGMENT_MARKER=${SEGMENT_MARKER:--}

# First grab all the omorfi functionality
. $(which omorfi.bash)

# Then just segment what came in
cat - | \
    python_wrap omorfi-segment.py \
        -s $(omorfi_find segment) \
        -S $(omorfi_find labelsegment) \
        --segment-marker ${SEGMENT_MARKER} \
        --split-derivs \
        -O segments
