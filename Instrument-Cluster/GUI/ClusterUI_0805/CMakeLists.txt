cmake_minimum_required(VERSION 3.14)

project(ClusterUI_0805 VERSION 0.1 LANGUAGES CXX)

# ---- Qt 자동 처리 ----
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---- Qt 찾기 (Qt5/Qt6 모두 지원, DBus/QuickControls2 포함) ----
find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Quick DBus QuickControls2)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Quick DBus QuickControls2)

# ---- 소스 경로 (현재 폴더 구조 유지) ----
set(PROJECT_SOURCES
    main.cpp
    PiRacerBridge.cpp
    PiRacerBridge.h
    qml.qrc
)

# ---- 실행 파일 ----
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

# ---- 링크 (DBus/QuickControls2) ----
target_link_libraries(ClusterUI_0805
    PRIVATE
        Qt${QT_VERSION_MAJOR}::Core
        Qt${QT_VERSION_MAJOR}::Quick
        Qt${QT_VERSION_MAJOR}::DBus
        Qt${QT_VERSION_MAJOR}::QuickControls2
)

# ---- 번들/설치(선택) ----
if(${QT_VERSION} VERSION_LESS 6.1.0)
  set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER com.example.ClusterUI_0805)
endif()

set_target_properties(ClusterUI_0805 PROPERTIES
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

include(GNUInstallDirs)
install(TARGETS ClusterUI_0805
    BUNDLE DESTINATION .
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

# ---- Qt6용 마무리(선택) ----
if(QT_VERSION_MAJOR EQUAL 6)
    qt_import_qml_plugins(ClusterUI_0805)
    qt_finalize_executable(ClusterUI_0805)
endif()
