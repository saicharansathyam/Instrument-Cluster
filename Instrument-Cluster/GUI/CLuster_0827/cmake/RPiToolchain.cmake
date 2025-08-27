# CMake toolchain for Raspberry Pi 4 cross-compilation
# Place this file at: ~/Desktop/SEAME projects/Instrument-Cluster/Instrument-Cluster/GUI/ClusterUI_0820/cmake/RPiToolchain.cmake

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Specify the cross compiler
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# Sysroot path - use environment variable
if(NOT DEFINED ENV{RPI_SYSROOT})
    message(FATAL_ERROR "RPI_SYSROOT environment variable not set. Please set it to your sysroot path.")
endif()

set(CMAKE_SYSROOT $ENV{RPI_SYSROOT})
set(CMAKE_FIND_ROOT_PATH $ENV{RPI_SYSROOT})

# Search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
# Search for libraries and headers in the target directories
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Qt5 specific settings for cross-compilation
set(QT_CROSS_COMPILE ON)

# Force using host Qt tools (Ubuntu tools, not Pi tools)
set(CMAKE_AUTOMOC_MOC_EXECUTABLE "/usr/bin/moc")
set(CMAKE_AUTOUIC_UIC_EXECUTABLE "/usr/bin/uic") 
set(CMAKE_AUTORCC_RCC_EXECUTABLE "/usr/bin/rcc")

# Compiler flags optimized for Raspberry Pi 4 (Cortex-A72, aarch64)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mcpu=cortex-a72")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcpu=cortex-a72")

# Additional Pi-specific optimizations
set(CMAKE_C_FLAGS_RELEASE "-O3 -DNDEBUG -ffast-math")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -ffast-math")

# PKG_CONFIG settings for finding Qt libraries in sysroot
set(ENV{PKG_CONFIG_PATH} "$ENV{RPI_SYSROOT}/usr/lib/aarch64-linux-gnu/pkgconfig:$ENV{RPI_SYSROOT}/usr/lib/pkgconfig")
set(ENV{PKG_CONFIG_SYSROOT_DIR} "$ENV{RPI_SYSROOT}")

# Fix Qt5 qmake and tool paths for cross-compilation
set(Qt5Core_DIR "$ENV{RPI_SYSROOT}/usr/lib/aarch64-linux-gnu/cmake/Qt5Core")
set(Qt5_DIR "$ENV{RPI_SYSROOT}/usr/lib/aarch64-linux-gnu/cmake/Qt5")

# Override Qt tool paths to use host versions
set(QT_QMAKE_EXECUTABLE "/usr/bin/qmake" CACHE FILEPATH "Host qmake" FORCE)

# Tell CMake to ignore missing qmake in sysroot
set(CMAKE_DISABLE_FIND_PACKAGE_Qt5LinguistTools TRUE)