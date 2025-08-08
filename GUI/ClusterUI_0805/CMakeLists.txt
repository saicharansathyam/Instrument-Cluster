cmake_minimum_required(VERSION 3.14)

project(ClusterUI_0805 VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---- Qt 찾기: Core, Quick, DBus 추가 ----
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Quick DBus)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Quick DBus)

# ---- 소스 목록 (모든 경우 공통) ----
set(PROJECT_SOURCES
    main.cpp
    PiRacerBridge.cpp
    PiRacerBridge.h
    qml.qrc
)

# ---- 실행파일 생성 ----
if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(ClusterUI_0805
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
    )
else()
    add_executable(ClusterUI_0805
        ${PROJECT_SOURCES}
    )
endif()

# ---- 링크 (DBus 포함) ----
target_link_libraries(ClusterUI_0805
    PRIVATE
        Qt${QT_VERSION_MAJOR}::Core
        Qt${QT_VERSION_MAJOR}::Quick
        Qt${QT_VERSION_MAJOR}::DBus   # ★ 중요
)

# (선택) mac/iOS 번들 세팅 그대로 유지
if(${QT_VERSION} VERSION_LESS 6.1.0)
  set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER com.example.ClusterUI_0805)
endif()
set_target_properties(ClusterUI_0805 PROPERTIES
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

include(GNUInstallDirs)
install(TARGETS ClusterUI_0805
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})

if(QT_VERSION_MAJOR EQUAL 6)
    qt_import_qml_plugins(ClusterUI_0805)
    qt_finalize_executable(ClusterUI_0805)
endif()
