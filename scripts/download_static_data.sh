#!/usr/bin/env bash
set -euo pipefail

# Usage: download.sh <csv|txt> <URL>
#
# Examples:
#   ./download.sh csv https://example.com/data.csv
#   ./download.sh txt https://example.com/data.zip

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATIC_DATA_DIR="$SCRIPT_DIR/../static_data"

# CSV download: just fetch and save
handle_csv_download() {
  mkdir -p "$STATIC_DATA_DIR"
  echo "Downloading CSV from $URL..."
  if curl -fSL "$URL" -o "$STATIC_DATA_DIR/$(basename "$URL")"; then
    echo "CSV saved to $STATIC_DATA_DIR/$(basename "$URL")"
  else
    echo "Failed to download CSV" >&2
    exit 1
  fi
}

handle_zip_download() {
  TMPDIR="$(mktemp -d)"
  trap 'rm -rf "$TMPDIR"' EXIT

  curl -fSL "$URL" -o "$TMPDIR/archive.zip"
  unzip -p "$TMPDIR/archive.zip" "$ELD_TXT" > "$TMPDIR/$ELD_TXT"

  mkdir -p "$STATIC_DATA_DIR"
  mv "$TMPDIR/$ELD_TXT" "$STATIC_DATA_DIR/$(basename "${ELD_TXT%.*}").csv"
  echo "TXT extracted and renamed to CSV at $STATIC_DATA_DIR/$(basename "${ELD_TXT%.*}").csv"
}

dispatch() {
  local ext="${1:-}"
  URL="${2:-}"
  ELD_TXT="LD2011_2014.txt"

  if [[ -z "$ext" ]]; then
    echo "No extension provided (must be 'csv' or 'zip')" >&2
    exit 1
  elif [[ "$ext" == "csv" ]]; then
    handle_csv_download
  elif [[ "$ext" == "zip" ]]; then
    handle_zip_download
  else
    echo "Invalid extension: '$ext' (must be 'csv' or 'zip')" >&2
    exit 1
  fi
}
dispatch "$@"