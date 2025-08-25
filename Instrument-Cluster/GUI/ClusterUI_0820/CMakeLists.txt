cmake_minimum_required(VERSION 3.16)
project(ClusterUI_0820 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Auto-moc/uic/rcc
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Try Qt6 first, fall back to Qt5
find_package(Qt6 COMPONENTS Core Gui Qml Quick DBus QUIET)
if (Qt6_FOUND)
  set(QT_VER 6)
  set(QT Qt6)
else()
  find_package(Qt5 REQUIRED COMPONENTS Core Gui Qml Quick DBus)
  set(QT_VER 5)
  set(QT Qt5)
endif()

# --- Executable sources (C++ 만) ---
add_executable(ClusterUI_0820
    main.cpp
    PiRacerBridge.cpp
    PiRacerBridge.h
)

# --- QRC 리소스 명시적으로 추가 (가장 중요) ---
if (QT_VER EQUAL 6)
  qt_add_resources(APP_RES qml.qrc)       # Qt6
else()
  qt5_add_resources(APP_RES qml.qrc)      # Qt5
endif()
target_sources(ClusterUI_0820 PRIVATE ${APP_RES})

target_link_libraries(ClusterUI_0820
    PRIVATE
      ${QT}::Core
      ${QT}::Gui
      ${QT}::Qml
      ${QT}::Quick
      ${QT}::DBus
)

set_target_properties(ClusterUI_0820 PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

message(STATUS "Building with Qt${QT_VER}")

