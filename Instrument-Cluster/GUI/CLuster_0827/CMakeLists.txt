cmake_minimum_required(VERSION 3.16)
project(ClusterUI_0820 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Force host Qt tools for cross-compilation
if(CMAKE_CROSSCOMPILING)
    message(STATUS "Cross-compiling: using host Qt tools")
    
    find_program(HOST_MOC moc PATHS /usr/bin NO_DEFAULT_PATH REQUIRED)
    find_program(HOST_UIC uic PATHS /usr/bin NO_DEFAULT_PATH REQUIRED)
    find_program(HOST_RCC rcc PATHS /usr/bin NO_DEFAULT_PATH REQUIRED)
    
    message(STATUS "Using host moc: ${HOST_MOC}")
    message(STATUS "Using host uic: ${HOST_UIC}")
    message(STATUS "Using host rcc: ${HOST_RCC}")
endif()

# Use pkg-config to find Qt5 (more reliable for cross-compilation)
find_package(PkgConfig REQUIRED)

# Find Qt5 modules using pkg-config
pkg_check_modules(Qt5Core REQUIRED Qt5Core)
pkg_check_modules(Qt5Gui REQUIRED Qt5Gui)
pkg_check_modules(Qt5Qml REQUIRED Qt5Qml)
pkg_check_modules(Qt5Quick REQUIRED Qt5Quick)
pkg_check_modules(Qt5DBus REQUIRED Qt5DBus)

message(STATUS "Qt5Core found: ${Qt5Core_FOUND}")
message(STATUS "Qt5Core version: ${Qt5Core_VERSION}")

# Manually run MOC on PiRacerBridge.h
add_custom_command(
    OUTPUT moc_PiRacerBridge.cpp
    COMMAND ${HOST_MOC} ${CMAKE_CURRENT_SOURCE_DIR}/PiRacerBridge.h -o moc_PiRacerBridge.cpp
    DEPENDS PiRacerBridge.h
    COMMENT "Running MOC on PiRacerBridge.h"
)

# Manually run RCC on qml.qrc
add_custom_command(
    OUTPUT qrc_qml.cpp
    COMMAND ${HOST_RCC} ${CMAKE_CURRENT_SOURCE_DIR}/qml.qrc -o qrc_qml.cpp
    DEPENDS qml.qrc main.qml
    COMMENT "Running RCC on qml.qrc"
)

# Define the executable
add_executable(ClusterUI_0820
    main.cpp
    PiRacerBridge.cpp
    PiRacerBridge.h
    moc_PiRacerBridge.cpp
    qrc_qml.cpp
)

# Add include directories
target_include_directories(ClusterUI_0820 PRIVATE
    ${Qt5Core_INCLUDE_DIRS}
    ${Qt5Gui_INCLUDE_DIRS}
    ${Qt5Qml_INCLUDE_DIRS}
    ${Qt5Quick_INCLUDE_DIRS}
    ${Qt5DBus_INCLUDE_DIRS}
    ${CMAKE_CURRENT_SOURCE_DIR}  # For moc files
)

# Add compile flags
target_compile_options(ClusterUI_0820 PRIVATE
    ${Qt5Core_CFLAGS_OTHER}
    ${Qt5Gui_CFLAGS_OTHER}
    ${Qt5Qml_CFLAGS_OTHER}
    ${Qt5Quick_CFLAGS_OTHER}
    ${Qt5DBus_CFLAGS_OTHER}
)

# Link libraries
target_link_libraries(ClusterUI_0820
    PRIVATE
    ${Qt5Core_LIBRARIES}
    ${Qt5Gui_LIBRARIES}
    ${Qt5Qml_LIBRARIES}
    ${Qt5Quick_LIBRARIES}
    ${Qt5DBus_LIBRARIES}
)

# Set output directory
set_target_properties(ClusterUI_0820 PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

# Additional compiler flags
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(ClusterUI_0820 PRIVATE -Wall -Wextra)
endif()

# Pi-specific optimizations for release builds
if(CMAKE_BUILD_TYPE STREQUAL "Release" AND CMAKE_CROSSCOMPILING)
    target_compile_options(ClusterUI_0820 PRIVATE -O3 -ffast-math)
endif()

# Install rule
install(TARGETS ClusterUI_0820 RUNTIME DESTINATION bin)

message(STATUS "")
message(STATUS "=== Build Configuration ===")
message(STATUS "Cross-compiling: ${CMAKE_CROSSCOMPILING}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "==========================")