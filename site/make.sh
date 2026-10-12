#!/bin/sh
# Rebuild the site into site/dist and run the offline checks.
set -e
cd "$(dirname "$0")"
python3 build.py
python3 tests/check_site.py | tail -3
node tests/test_model.js | tail -1
if [ "$1" = "zip" ]; then
  rm -f ../release/inference-asic-atlas-site.zip
  mkdir -p ../release
  (cd dist && zip -qr -X ../../release/inference-asic-atlas-site.zip . -x '.*')
  echo "wrote release/inference-asic-atlas-site.zip"
fi
