#!/bin/bash

OUTPUT="repo_dump.txt"

find . \
  -type d \( \
    -name .git -o \
    -name .venv -o \
    -name __pycache__ -o \
    -name .pytest_cache \
  \) -prune -o \
  -type f \
  ! -name "$OUTPUT" \
  -print | sort | while read file
do
    echo "==================================================" >> "$OUTPUT"
    echo "FILE: $file" >> "$OUTPUT"
    echo "==================================================" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo -e "\n\n" >> "$OUTPUT"
done

echo "Wrote $OUTPUT"
