#! /bin/bash

INPUT_DIR_1="${1}"
INPUT_DIR_2="${2}"
URL_FILE="${3}"
OUTPUT_FILE="${4}"

./generate-html.py ${INPUT_DIR_1} ${INPUT_DIR_2} ${URL_FILE} ${OUTPUT_FILE}
