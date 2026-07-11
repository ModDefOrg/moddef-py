#!/usr/bin/env sh
# Sync the vendored generated protobuf modules from the moddef repo
# (regenerate there first: buf generate). CI diffs for drift.
set -eu
src="${1:-../moddef/gen/python/moddef/v1}"
dst="$(dirname "$0")/../src/moddef/v1"
cp "$src"/*_pb2.py "$src"/*_pb2.pyi "$dst"/
echo "synced $(ls "$dst" | grep -c _pb2) files from $src"
