#!/usr/bin/env bash

set -Eeuo pipefail

INPUT="librepastebin-piper.py"
OUTPUT="librepastebin-piper"

if [[ ! -f "$INPUT" ]]; then
    echo "Error: $INPUT was not found." >&2
    exit 1
fi

if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Error: PyInstaller is not installed." >&2
    echo "Install it with: python3 -m pip install pyinstaller" >&2
    exit 1
fi

echo "Building $INPUT as $OUTPUT..."

pyinstaller \
    --onefile \
    --clean \
    --name "$OUTPUT" \
    "$INPUT"

echo "Build completed successfully."
echo "Output file: dist/$OUTPUT"
