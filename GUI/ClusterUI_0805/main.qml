import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

Window {
    width: 1280
    height: 400
    visible: true
    title: qsTr("Cluster UI")

    // Orbitron 폰트 로딩
    FontLoader {
        id: orbitron
        source: "fonts/Orbitron-VariableFont_wght.ttf"
    }

    Rectangle {
        anchors.fill: parent
        color: "#000000"  // 배경: 검정

        // 중앙 디지털 숫자 표시
        Text {
            id: digitalSpeed
            text: "88"
            anchors.centerIn: parent
            font.family: orbitron.name
            font.pixelSize: 120
            color: "#00FF00"  // 녹색 디지털 느낌
            font.bold: true
        }
    }
}
