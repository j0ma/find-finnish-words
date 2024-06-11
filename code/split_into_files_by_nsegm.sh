#!/usr/bin/env bash

export dest_folder=$1
if [ -z ${dest_folder} ]
then
    # If no destination folder is provided, create a temporary folder
    # Log this to stderr
    dest_folder=$(mktemp -d)
    echo "No destination folder provided. Using temporary folder: ${dest_folder}" >&2
fi

cat - \
    | tqdm --desc "Splitting by number of segments into ${dest_folder}" \
    | while read line; do nsegm=$(echo $line | tr " " "\n" | tail -n1); echo $line >> ${dest_folder}/nsegm-${nsegm}.txt; done
