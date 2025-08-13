import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.12

Window {
    id: root
    visible: true
    visibility: Window.FullScreen
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    title: qsTr("Cluster UI")
    color: "black"

    // Belt & suspenders across platforms:
    Component.onCompleted: root.showFullScreen()

    FontLoader {
        id: orbitronFont
        source: "qrc:/fonts/Orbitron-VariableFont_wght.ttf"
    }

    Image {
        id: background
        source: "qrc:/images/background.png"
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
    }

    Item {
        id: leftGauge
        width: 555
        height: 400
        anchors.left: parent.left
        anchors.leftMargin: 80
        anchors.verticalCenter: parent.verticalCenter

        Text {
            id: speedText
            text: Math.round(bridge.speed).toString() // cm/s → km/h
            anchors.horizontalCenter: parent.horizontalCenter
            y: 240
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            width: 100
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            text: "KM/H"
            anchors.horizontalCenter: speedText.horizontalCenter
            y: 300
            width: 100
            horizontalAlignment: Text.AlignHCenter
            font.family: orbitronFont.name
            font.pixelSize: 30
            color: "white"
        }

        Image {
            id: needle
            source: "qrc:/images/needles.png"
            width: 140
            height: 200
            x: 207
            y: 40
            transform: Rotation {
                origin.x: needle.width / 2
                origin.y: needle.height * 0.92 - 25
                angle: (bridge.speed*1.5)-130
            }
        }
    }

    Item {
        id: rightGauge
        width: 510
        height: 400
        anchors.right: parent.right
        anchors.rightMargin: 80
        anchors.verticalCenter: parent.verticalCenter

        Text {
            text: bridge.battery.toFixed(0) + "%"
            anchors.horizontalCenter: parent.horizontalCenter
            y: 230
            width: 100
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            horizontalAlignment: Text.AlignHCenter
        }
    }

    Item {
        id: batteryIcon
        width: 400
        height: 160
        x: 735
        y: 100

        Image {
            id: iconOutline
            source: "qrc:/images/battery_icon.png"
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
        }

        Rectangle {
            id: batteryFill
            width: batteryIcon.width * bridge.battery / 470
            height: batteryIcon.height / 4
            x: 157
            y: 60
            radius: 3
            z: -1
            color: bridge.battery <= 20 ? "#ff0000" :
                   bridge.battery <= 50 ? "#ffaa00" : "#00ff55"
        }
    }
}

