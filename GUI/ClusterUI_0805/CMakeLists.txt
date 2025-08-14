cmake_minimum_required(VERSION 3.14)
project(ClusterUI_0805 VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Qt5/Qt6 겸용 (DBus/QuickControls2 포함)
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Quick DBus QuickControls2)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Quick DBus QuickControls2)

# ✅ 실제 경로로 수정
set(PROJECT_SOURCES
    main.cpp
    PiRacerBridge.cpp
    PiRacerBridge.h
    qml.qrc
)

# (선택) 없는 파일 즉시 잡아내기
message(STATUS "PROJECT_SOURCES = ${PROJECT_SOURCES}")
foreach(f IN LISTS PROJECT_SOURCES)
  if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${f}")
    message(FATAL_ERROR "Missing source: ${f}")
  endif()
endforeach()

if(QT_VERSION_MAJOR GREATER_EQUAL 6)
  qt_add_executable(ClusterUI_0805 MANUAL_FINALIZATION ${PROJECT_SOURCES})
else()
  add_executable(ClusterUI_0805 ${PROJECT_SOURCES})
endif()

target_link_libraries(ClusterUI_0805
  PRIVATE
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Quick
    Qt${QT_VERSION_MAJOR}::DBus
    Qt${QT_VERSION_MAJOR}::QuickControls2
)

if(QT_VERSION_MAJOR EQUAL 6)
  qt_import_qml_plugins(ClusterUI_0805)
  qt_finalize_executable(ClusterUI_0805)
endif()
