#!/usr/bin/env bash
set -euo pipefail

# =========================
# Config (override via env)
# =========================
RPI_USER="${RPI_USER:-team3}"
RPI_HOST="${RPI_HOST:-192.168.86.67}"
RPI_DEPLOY_DIR="${RPI_DEPLOY_DIR:-/home/$RPI_USER/apps/cluster_ui}"
TARGET_BIN="${TARGET_BIN:-cluster_ui}"

# =========================
# Resolve key paths
# =========================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_DIR="$GUI_DIR/ClusterUI_0820"
REPO_ROOT="$(cd "$GUI_DIR/../.." && pwd)"
BUILD_DIR="$APP_DIR/build"
TOOLCHAIN_FILE="$APP_DIR/toolchains/rpi-aarch64.cmake"
SYSROOT_SYNC="$SCRIPT_DIR/sysroot_sync.sh"

echo "🔍 Using repo root: $REPO_ROOT"
echo "📂 Using app dir:  $APP_DIR"

# =========================
# Pre-flight checks
# =========================
command -v cmake >/dev/null || { echo "[ERR] cmake not found."; exit 1; }
command -v ninja >/dev/null || { echo "[ERR] ninja not found. Install it: sudo apt-get install ninja-build"; exit 1; }
[[ -f "$APP_DIR/CMakeLists.txt" ]] || { echo "[ERR] CMakeLists.txt not found in $APP_DIR"; exit 1; }
[[ -f "$TOOLCHAIN_FILE" ]] || { echo "[ERR] Toolchain file not found: $TOOLCHAIN_FILE"; exit 1; }

# =========================
# 1) Sysroot sync + fix
# =========================
if [[ -x "$SYSROOT_SYNC" ]]; then
  "$SYSROOT_SYNC"
else
  echo "[WARN] $SYSROOT_SYNC not executable or missing. Skipping sysroot sync."
fi

# =========================
# 2) Configure & build
# =========================
echo "[INFO] Configuring & building…"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cmake -S "$APP_DIR" -B "$BUILD_DIR" -G Ninja -DCMAKE_TOOLCHAIN_FILE="$TOOLCHAIN_FILE"
cmake --build "$BUILD_DIR" -- -v

# =========================
# 3) Deploy to Pi
# =========================
echo "[INFO] Deploying to ${RPI_USER}@${RPI_HOST}:$RPI_DEPLOY_DIR"
ssh -o StrictHostKeyChecking=no "$RPI_USER@$RPI_HOST" "mkdir -p '$RPI_DEPLOY_DIR'"
# binary
scp "$BUILD_DIR/$TARGET_BIN" "$RPI_USER@$RPI_HOST:$RPI_DEPLOY_DIR/$TARGET_BIN"
# assets (images directory if present)
if [[ -d "$APP_DIR/images" ]]; then
  rsync -a --delete "$APP_DIR/images/" "$RPI_USER@$RPI_HOST:$RPI_DEPLOY_DIR/images/"
fi

# =========================
# 4) Restart on Pi
# =========================
echo "[INFO] Restarting app on Pi…"
ssh "$RPI_USER@$RPI_HOST" "pkill -x '$TARGET_BIN' >/dev/null 2>&1 || true; nohup '$RPI_DEPLOY_DIR/$TARGET_BIN' >/dev/null 2>&1 &"

echo "[INFO] Done. App running on $RPI_HOST."
