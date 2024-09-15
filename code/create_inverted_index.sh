#!/usr/bin/env bash

export language=${language:-"fi"}

process_single_line () {
    local out_folder=$1
    local sentence_idx=$2
    local input_file=$3

    head -n ${sentence_idx} ${input_file} | tail -n 1 \
        | tr " " "\n" \
        | sort | uniq \
        | while read word
        do 
            local dedicated_output_file="${out_folder}/${word}.txt"
            touch ${dedicated_output_file}
            echo "${sentence_idx}" >> "${dedicated_output_file}"
        done
}

export -f process_single_line

input_file=$1
output_folder=$2

parallel --progress -N0 "process_single_line $output_folder {#} ${input_file}" :::: ${input_file}
