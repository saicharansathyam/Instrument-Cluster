#!/usr/bin/env bash
set -euo pipefail

# =========================
# Config (override via env)
# =========================
RPI_USER="${RPI_USER:-team3}"
RPI_HOST="${RPI_HOST:-192.168.86.67}"
SYSROOT_DIR="${SYSROOT_DIR:-$HOME/rpi-sysroot}"

# Remote sources to mirror
SRC_LIST=(
  "/lib/aarch64-linux-gnu"
  "/usr/include"
  "/usr/lib/aarch64-linux-gnu"
  "/usr/lib/aarch64-linux-gnu/cmake"
  "/usr/lib/pkgconfig"
  "/usr/share/pkgconfig"
  "/usr/lib/qt5"
)

echo "[SYSROOT] Syncing Raspberry Pi sysroot to $SYSROOT_DIR..."
mkdir -p "$SYSROOT_DIR"

# ========= rsync (preserve symlinks) =========
for SRC in "${SRC_LIST[@]}"; do
  DEST="$SYSROOT_DIR$SRC"
  echo "[SYSROOT] Sync $SRC -> $DEST"
  mkdir -p "$DEST"
  rsync -a --delete -e ssh "$RPI_USER@$RPI_HOST:$SRC/" "$DEST/"
done
echo "[SYSROOT] Done. Sysroot at: $SYSROOT_DIR"

# ========= Symlink repair =========
echo "[SYSROOT] Checking for broken symlinks..."

warn_unresolved() {
  local link="$1"
  local tgt="$2"
  echo "[SYSROOT] WARNING: Unresolved $( [[ "$tgt" = /* ]] && echo "symlink" || echo "relative symlink") $link -> $tgt"
}

repair_link() {
  local link="$1"
  local tgt="$2"
  local linkdir; linkdir="$(dirname "$link")"

  if [[ "$tgt" = /* ]]; then
    # Absolute target -> map into sysroot
    local mapped="$SYSROOT_DIR$tgt"
    if [[ -e "$mapped" ]]; then
      # Rewrite to relative within sysroot
      local rel
      rel="$(python3 - <<PY
import os,sys
print(os.path.relpath("$mapped","$linkdir"))
PY
)"
      ln -snf "$rel" "$link"
      echo "[SYSROOT] Fixing $link -> $tgt (=> $rel)"
    else
      warn_unresolved "$link" "$tgt"
    fi
  else
    # Relative target -> resolve from linkdir
    if [[ -e "$linkdir/$tgt" ]]; then
      # Good as-is
      :
    else
      warn_unresolved "$link" "$tgt"
    fi
  fi
}

# Walk all symlinks under SYSROOT_DIR
while IFS= read -r -d '' link; do
  tgt="$(readlink "$link" || true)"
  [[ -z "${tgt:-}" ]] && continue
  if [[ "$tgt" = /* ]]; then
    # absolute link
    if [[ ! -e "$SYSROOT_DIR$tgt" ]]; then
      # try repair by mapping absolute to sysroot
      repair_link "$link" "$tgt"
    fi
  else
    # relative link
    linkdir="$(dirname "$link")"
    [[ -e "$linkdir/$tgt" ]] || repair_link "$link" "$tgt"
  fi
done < <(find "$SYSROOT_DIR" -xtype l -print0)

echo "[SYSROOT] Symlink check complete."
