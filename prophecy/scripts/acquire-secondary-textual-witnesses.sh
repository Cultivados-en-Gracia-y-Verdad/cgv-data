#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-prophecy/.local/corpora}"
mkdir -p "$ROOT"

clone_pinned() {
  local repo="$1"
  local dest="$2"
  local commit="$3"

  if [[ ! -d "$dest/.git" ]]; then
    git clone --filter=blob:none "$repo" "$dest"
  fi
  git -C "$dest" fetch --all --tags --prune
  git -C "$dest" checkout --detach "$commit"
}

clone_pinned \
  "https://github.com/CenterBLC/LXX.git" \
  "$ROOT/lxx-centerblc" \
  "4829f3746c84d75576702498e75a68856358f289"

clone_pinned \
  "https://github.com/openscriptures/GreekResources.git" \
  "$ROOT/lxx-openscriptures-resources" \
  "dd5a2fd530ab3c6b748c174cec38966c356d8111"

clone_pinned \
  "https://github.com/ETCBC/syrnt.git" \
  "$ROOT/syrnt-etcbc" \
  "dae3eb6ff62b9b272fb503646796c25d248175ce"

download_zip() {
  local url="$1"
  local dest="$2"
  local zip_path="$dest/source.zip"

  mkdir -p "$dest"
  curl --fail --location --retry 3 "$url" --output "$zip_path"
  sha256sum "$zip_path" > "$dest/SHA256SUMS"
  unzip -o "$zip_path" -d "$dest/usfm"
}

download_zip \
  "https://ebible.org/Scriptures/heb_usfm.zip" \
  "$ROOT/hebrew-nt-delitzsch"

download_zip \
  "https://ebible.org/Scriptures/hebsg_usfm.zip" \
  "$ROOT/hebrew-nt-salkinson-ginsburg"

cat > "$ROOT/ACQUISITION-NOTES.txt" <<'EOF'
These corpora are secondary textual witnesses.

Canonical-language anchors remain:
- Hebrew and Aramaic for the Old Testament
- Greek for the New Testament

Do not commit the local corpus directory unless the exact text and annotation rights have been reviewed and the acquisition manifest permits redistribution.
The ETCBC Peshitta corpus does not include Revelation. A separate identified Syriac Revelation witness is still required.
EOF

printf 'Secondary witnesses acquired under %s\n' "$ROOT"
