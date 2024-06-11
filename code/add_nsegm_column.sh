#!/usr/bin/env bash

. code/utils.sh

cat - |
    while read line; do
        # grab segmented word from last column
        word=$(echo "${line}" | awk '{print $NF}')
        nsegm=$(count_segments "${word}")

        # finally print original line and number of segments
        printf "%s\t%s\n" "${line}" "${nsegm}"
    done
