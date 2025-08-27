#!/bin/bash
# Cross-compilation build script for ClusterUI_0820
# Place this file at: ~/Desktop/SEAME projects/Instrument-Cluster/Instrument-Cluster/GUI/CLuster_0827/build-rpi.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ClusterUI_0820 Cross-Compilation for Raspberry Pi 4 ===${NC}"

# Check if we're in the right directory
EXPECTED_DIR="CLuster_0827"
CURRENT_DIR=$(basename "$PWD")
if [ "$CURRENT_DIR" != "$EXPECTED_DIR" ]; then
    echo -e "${RED}Error: Please run this script from the CLuster_0827 directory${NC}"
    echo -e "${YELLOW}Current directory: $PWD${NC}"
    echo -e "${YELLOW}Expected to be in: ~/Desktop/SEAME projects/Instrument-Cluster/Instrument-Cluster/GUI/CLuster_0827${NC}"
    exit 1
fi

# Environment setup
echo -e "${BLUE}Setting up environment...${NC}"
export RPI_SYSROOT=$HOME/rpi-sysroot

# Check if sysroot exists
if [ ! -d "$RPI_SYSROOT" ]; then
    echo -e "${RED}Error: Sysroot directory not found at $RPI_SYSROOT${NC}"
    echo -e "${YELLOW}Please set up your sysroot first by copying libraries from your Raspberry Pi${NC}"
    echo -e "${YELLOW}See the previous setup guide for instructions.${NC}"
    exit 1
fi

# Check if cross-compiler is installed
if ! command -v aarch64-linux-gnu-gcc &> /dev/null; then
    echo -e "${RED}Error: Cross-compiler not found${NC}"
    echo -e "${YELLOW}Please install it with: sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu${NC}"
    exit 1
fi

# Check if host Qt tools are available
if ! command -v moc &> /dev/null; then
    echo -e "${RED}Error: Qt host tools not found${NC}"
    echo -e "${YELLOW}Please install them with: sudo apt install qtbase5-dev-tools${NC}"
    exit 1
fi

# Check if pkg-config is available
if ! command -v pkg-config &> /dev/null; then
    echo -e "${RED}Error: pkg-config not found${NC}"
    echo -e "${YELLOW}Please install it with: sudo apt install pkgconf pkg-config${NC}"
    exit 1
fi

# PKG_CONFIG setup for finding Qt in sysroot
export PKG_CONFIG_PATH="$RPI_SYSROOT/usr/lib/aarch64-linux-gnu/pkgconfig:$RPI_SYSROOT/usr/lib/pkgconfig"
export PKG_CONFIG_SYSROOT_DIR="$RPI_SYSROOT"

echo -e "${GREEN}✓ Cross-compiler found: $(aarch64-linux-gnu-gcc --version | head -n1)${NC}"
echo -e "${GREEN}✓ Sysroot: $RPI_SYSROOT${NC}"
echo -e "${GREEN}✓ Qt tools: $(moc -v 2>&1)${NC}"
echo -e "${GREEN}✓ pkg-config: $(pkg-config --version)${NC}"

# Create cmake directory if it doesn't exist
mkdir -p cmake

# Check if toolchain file exists
if [ ! -f "cmake/RPiToolchain.cmake" ]; then
    echo -e "${RED}Error: Toolchain file not found at cmake/RPiToolchain.cmake${NC}"
    echo -e "${YELLOW}Please create the toolchain file first.${NC}"
    exit 1
fi

# Create and enter build directory
echo -e "${BLUE}Setting up build directory...${NC}"
BUILD_DIR="build-rpi"
rm -rf $BUILD_DIR  # Clean previous build
mkdir -p $BUILD_DIR
cd $BUILD_DIR

echo -e "${BLUE}Configuring with CMake...${NC}"

# Configure with CMake
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/RPiToolchain.cmake \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr/local \
      -DCMAKE_VERBOSE_MAKEFILE=ON \
      .. || {
    echo -e "${RED}CMake configuration failed!${NC}"
    exit 1
}

echo -e "${BLUE}Building ClusterUI_0820...${NC}"

# Build with all available cores
make -j$(nproc) || {
    echo -e "${RED}Build failed!${NC}"
    exit 1
}

echo -e "${GREEN}=== Build Successful! ===${NC}"
echo -e "${GREEN}Binary location: $(pwd)/ClusterUI_0820${NC}"
echo -e "${GREEN}Binary size: $(ls -lh ClusterUI_0820 | awk '{print $5}')${NC}"

# Check if binary is properly cross-compiled
echo -e "${BLUE}Verifying cross-compilation...${NC}"
FILE_INFO=$(file ClusterUI_0820)
echo -e "${GREEN}File info: $FILE_INFO${NC}"

if echo "$FILE_INFO" | grep -q "aarch64"; then
    echo -e "${GREEN}✓ Successfully cross-compiled for ARM64/aarch64${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Binary might not be properly cross-compiled${NC}"
fi

echo -e "${BLUE}=== Deployment Instructions ===${NC}"
echo -e "${YELLOW}To deploy to your Raspberry Pi:${NC}"
echo -e "1. Copy binary: ${GREEN}scp $(pwd)/ClusterUI_0820 team3@YOUR_PI_IP:~/${NC}"
echo -e "2. SSH to Pi: ${GREEN}ssh team3@YOUR_PI_IP${NC}"
echo -e "3. Make executable: ${GREEN}chmod +x ClusterUI_0820${NC}"
echo -e "4. Run: ${GREEN}./ClusterUI_0820${NC}"
echo ""
echo -e "${YELLOW}Note: Make sure Qt5 and required libraries are installed on your Pi:${NC}"
echo -e "${GREEN}sudo apt install qtbase5-dev qtdeclarative5-dev qtquickcontrols2-5-dev libqt5dbus5 qml-module-qtgraphicaleffects${NC}"
