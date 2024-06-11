#!/usr/bin/env bash

word=$1

temp=$(mktemp)
cat <<EOF > $temp
Give me a Finnish sentence that uses the word "$word".
Output a JSON of the form '{"sentence": "<sentence you generate>", "word": <word>}'.
Do not output ANYTHING else. Only the JSON. I will be piping the output into jq.
EOF

chatblade -c4 -sero < $temp | jq -r '.sentence'

rm $temp
