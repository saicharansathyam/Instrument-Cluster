import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Window {
    id: root
    width: 1280
    height: 400
    visible: true
    title: qsTr("Cluster UI")

    // ▶ 속도와 배터리 변수
    property real speed: 0
    property int batteryLevel: 100

    // ▶ 속도 애니메이션
    NumberAnimation on speed {
        id: speedAnim
        from: 0
        to: 100
        duration: 5000
        loops: Animation.Infinite
        running: true
        easing.type: Easing.InOutQuad
    }

    // ▶ 배터리 애니메이션
    NumberAnimation on batteryLevel {
        id: batteryAnim
        from: 100
        to: 0
        duration: 5000
        loops: Animation.Infinite
        running: true
        easing.type: Easing.InOutQuad
    }

    // ▶ Orbitron 폰트 로드
    FontLoader {
        id: orbitronFont
        source: "qrc:/fonts/Orbitron-VariableFont_wght.ttf"
    }

    // ▶ 배경 이미지
    Image {
        id: background
        source: "qrc:/images/background.png"
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
    }

    // ▶ 왼쪽 원형 게이지 영역
    Item {
        id: leftGauge
        width: 555
        height: 400
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 80

        // ▶ 속도 숫자
        Text {
            id: speedText
            text: Math.round(root.speed).toString()
            anchors.horizontalCenter: parent.horizontalCenter
            y: 240  // 수직 위치는 유지
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            horizontalAlignment: Text.AlignHCenter
            width: 100  // 충분한 고정 너비를 줘야 함!
        }

        // ▶ "KM/H" 표시
        Text {
            id: kmhText
            text: "KM/H"
            anchors.horizontalCenter: speedText.horizontalCenter
            y: 300
            width: 100
            horizontalAlignment: Text.AlignHCenter
            font.family: orbitronFont.name
            font.pixelSize: 30
            color: "white"
        }


        // ▶ 바늘 이미지
        Image {
            id: needle
            source: "qrc:/images/needles.png"
            width: 140
            height: 200
            x: 207
            y: 40

            transform: Rotation {
                id: needleRotation
                origin.x: needle.width / 2
                origin.y: needle.height * 0.92 - 25
                angle: root.speed * 2.6 - 130  // 회전 범위: -120° ~ +120°
            }
        }
    }

    // ▶ 오른쪽 배터리 게이지 영역
    Item {
        id: rightGauge
        width: 510
        height: 400
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 80

        // ▶ 배터리 텍스트
        Text {
            id: batteryText
            text: root.batteryLevel + "%"
            anchors.horizontalCenter: parent.horizontalCenter
            y: 230
            width: 100
            horizontalAlignment: Text.AlignHCenter
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
        }

    }
    Item {
        id: batteryIcon
        width: 400
        height: 160
        x: 735      // 위치 조절 가능
        y: 100

        // 배경 아이콘
        Image {
            id: iconOutline
            source: "qrc:/images/battery_icon.png"
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
        }

        // 내부 충전 바
        Rectangle {
            id: batteryFill
            width: batteryIcon.width * root.batteryLevel / 470
            height: batteryIcon.height / 4
            x: 157
            y: 60
            radius: 3
            z: -1

            color: root.batteryLevel <= 20 ? "#ff0000" :    // 빨간색
                   root.batteryLevel <= 50 ? "#ffaa00" :    // 주황색
                   "#00ff55"                                // 초록색
        }

    }
}
