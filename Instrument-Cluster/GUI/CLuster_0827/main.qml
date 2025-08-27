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

    Component.onCompleted: root.showFullScreen()

    // ==================== Calibration (cm/s → angle) ====================
    property real speedMin: 0
    property real speedMax: 300        // e.g., 300 cm/s ≈ 10.8 km/h
    property real angleMin: -130       // dial angle at 0 cm/s
    property real angleMax:  130       // dial angle at speedMax

    function mapRangeClamped(v, inMin, inMax, outMin, outMax) {
        var vv = Math.max(inMin, Math.min(v, inMax));
        var t  = (vv - inMin) / (inMax - inMin);
        return outMin + t * (outMax - outMin);
    }

    // ==================== Assets ====================
    FontLoader {
        id: orbitronFont
        source: "qrc:/fonts/Orbitron-VariableFont_wght.ttf"
    }

    Image {
        id: background
        source: "qrc:/images/background.png"
        anchors.fill: parent
        fillMode: Image.PreserveAspectCrop
        smooth: true
    }

    // ==================== Top Turn Indicators ====================
    Item {
        id: topIndicators
        width: 400
        height: 100
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 10
        visible: true

        // Left turn
        Image {
            id: leftIndicatorBase
            source: "qrc:/images/left_indicator.png"
            width: 150
            height: 80
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            smooth: true
            visible: false   // 원본은 숨김
        }

        ColorOverlay {
            id: leftIndicator
            anchors.fill: leftIndicatorBase
            source: leftIndicatorBase
            color: "#00FF55"   // 초록색
            opacity: 0.0

            SequentialAnimation on opacity {
                id: leftBlink
                running: bridge && bridge.leftTurn
                loops: Animation.Infinite
                NumberAnimation { to: 1.0; duration: 160 }
                PauseAnimation   { duration: 140 }
                NumberAnimation { to: 0.0; duration: 160 }
                PauseAnimation   { duration: 240 }

                onRunningChanged: if (!running) leftIndicator.opacity = 0.0
            }
        }

        // Right turn
        Image {
            id: rightIndicatorBase
            source: "qrc:/images/right_indicator.png"
            width: 150
            height: 80
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            smooth: true
            visible: false
        }

        ColorOverlay {
            id: rightIndicator
            anchors.fill: rightIndicatorBase
            source: rightIndicatorBase
            color: "#00FF55"   // 초록색
            opacity: 0.0

            SequentialAnimation on opacity {
                id: rightBlink
                running: bridge && bridge.rightTurn
                loops: Animation.Infinite
                NumberAnimation { to: 1.0; duration: 160 }
                PauseAnimation   { duration: 140 }
                NumberAnimation { to: 0.0; duration: 160 }
                PauseAnimation   { duration: 240 }

                onRunningChanged: if (!running) rightIndicator.opacity = 0.0
            }
        }
    }

    // ==================== Left gauge (Speed in cm/s) ====================
    Item {
        id: leftGauge
        width: 555; height: 400
        anchors.left: parent.left; anchors.leftMargin: 80
        anchors.verticalCenter: parent.verticalCenter

        Text {
            id: speedText
            property real displaySpeed: 0.0
            text: Math.round(displaySpeed).toString()
            anchors.horizontalCenter: parent.horizontalCenter
            y: 240
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            width: 100
            horizontalAlignment: Text.AlignHCenter

            Behavior on displaySpeed {
                NumberAnimation {
                    duration: 250
                    easing.type: Easing.OutCubic
                }
            }

            Connections {
                target: bridge
                function onSpeedChanged() {
                    speedText.displaySpeed = Math.max(0, bridge.speed)
                }
            }

            Component.onCompleted: {
                if (bridge) displaySpeed = Math.max(0, bridge.speed)
            }
        }

        Text {
            text: "CM/S"
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
            smooth: true

            property real targetAngle: mapRangeClamped(Math.max(0, bridge ? bridge.speed : 0),
                                                       speedMin, speedMax, angleMin, angleMax)

            transform: Rotation {
                origin.x: needle.width / 2
                origin.y: needle.height * 0.92 - 25
                angle: needle.targetAngle
            }

            Behavior on targetAngle {
                NumberAnimation {
                    duration: 180
                    easing.type: Easing.InOutCubic
                }
            }
        }
    }

    // ==================== Right gauge (Battery %) ====================
    Item {
        id: rightGauge
        width: 510; height: 400
        anchors.right: parent.right; anchors.rightMargin: 80
        anchors.verticalCenter: parent.verticalCenter

        Text {
            id: batteryText
            property real displayBattery: 0.0
            text: Math.round(displayBattery).toString() + "%"
            anchors.horizontalCenter: parent.horizontalCenter
            y: 240
            width: 100
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            horizontalAlignment: Text.AlignHCenter

            Behavior on displayBattery {
                NumberAnimation {
                    duration: 300
                    easing.type: Easing.OutCubic
                }
            }

            Connections {
                target: bridge
                function onBatteryChanged() {
                    batteryText.displayBattery = Math.max(0, Math.min(100, bridge.battery))
                }
            }

            Component.onCompleted: {
                if (bridge) displayBattery = Math.max(0, Math.min(100, bridge.battery))
            }
        }
    }

    // ==================== Battery icon ====================
    Item {
        id: batteryIcon
        width: 350; height: 140
        anchors.horizontalCenter: rightGauge.horizontalCenter
        anchors.verticalCenter: rightGauge.verticalCenter
        anchors.verticalCenterOffset: -15

        Image {
            id: iconOutline
            source: "qrc:/images/battery_icon.png"
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
            smooth: true
        }

        readonly property real cavityX_src: 210
        readonly property real cavityY_src: 395
        readonly property real cavityW_src: 590
        readonly property real cavityH_src: 230

        readonly property real srcW: iconOutline.sourceSize.width  > 0 ? iconOutline.sourceSize.width  : 1024
        readonly property real srcH: iconOutline.sourceSize.height > 0 ? iconOutline.sourceSize.height : 1024

        readonly property real paintedW: iconOutline.paintedWidth
        readonly property real paintedH: iconOutline.paintedHeight
        readonly property real offsetX: (batteryIcon.width  - paintedW) / 2
        readonly property real offsetY: (batteryIcon.height - paintedH) / 2

        readonly property real scaleX: paintedW / srcW
        readonly property real scaleY: paintedH / srcH
        readonly property real cavityX: offsetX + cavityX_src * scaleX
        readonly property real cavityY: offsetY + cavityY_src * scaleY
        readonly property real cavityW:           cavityW_src * scaleX
        readonly property real cavityH:           cavityH_src * scaleY

        property real displayBatteryLevel: 0.0

        Behavior on displayBatteryLevel {
            NumberAnimation {
                duration: 400
                easing.type: Easing.OutCubic
            }
        }

        Connections {
            target: bridge
            function onBatteryChanged() {
                batteryIcon.displayBatteryLevel = Math.max(0, Math.min(bridge.battery, 100))
            }
        }

        Component.onCompleted: {
            if (bridge) displayBatteryLevel = Math.max(0, Math.min(bridge.battery, 100))
        }

        Item {
            id: cavityClip
            x: batteryIcon.cavityX
            y: batteryIcon.cavityY
            width: batteryIcon.cavityW
            height: batteryIcon.cavityH
            clip: true

            readonly property real m: 1.2

            Rectangle {
                id: batteryFill
                x: cavityClip.m
                y: cavityClip.m
                width: (cavityClip.width  - 2*cavityClip.m) * (batteryIcon.displayBatteryLevel / 100.0)
                height: (cavityClip.height - 2*cavityClip.m)
                radius: height / 2
                color: batteryIcon.displayBatteryLevel <= 20 ? "#ff0000"
                     : batteryIcon.displayBatteryLevel <= 50 ? "#ffaa00"
                     : "#00ff55"

                Behavior on width {
                    NumberAnimation { duration: 400; easing.type: Easing.OutCubic }
                }
                Behavior on color { ColorAnimation { duration: 300 } }
            }
        }
    }

    // ==================== Center area (Car + Gear) ====================
    Item {
        id: centerArea
        width: 100
        height: 120
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 60

        Rectangle {
            id: carOutline
            width: 80
            height: 35
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            color: "transparent"
            border.color: "#4A9EFF"
            border.width: 2
            radius: 8
            opacity: 0.6
        }

        Text {
            id: gearText
            text: bridge ? bridge.gear : ""
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: carOutline.bottom
            anchors.topMargin: 20
            font.family: orbitronFont.name
            font.pixelSize: 42
            color: "white"
            horizontalAlignment: Text.AlignHCenter

            SequentialAnimation {
                running: true
                loops: Animation.Infinite
                NumberAnimation { target: gearText; property: "opacity"; to: 0.3; duration: 75 }
                NumberAnimation { target: gearText; property: "opacity"; to: 1.0; duration: 75 }
                PauseAnimation { duration: 1000 }
            }
        }
    }

    // ==================== Key Controls ====================
    Keys.onPressed: {
        if (event.key === Qt.Key_F2) {
            topIndicators.visible = !topIndicators.visible
            event.accepted = true
            return
        }
        if (event.key === Qt.Key_F1) {
            calibOverlay.visible = !calibOverlay.visible
            event.accepted = true
            return
        }
    }

    // ==================== Calibration Overlay (F1) ====================
    Rectangle {
        id: calibOverlay
        visible: false
        anchors.fill: parent
        color: "#00000080"
        z: 999

        Column {
            anchors.centerIn: parent
            spacing: 8

            Text {
                text: "Calibration Overlay (F1 to hide)"
                color: "white"
                font.pixelSize: 20
                font.family: orbitronFont.name
            }
            Text {
                text: "Raw speed: " + (bridge ? Math.max(0, bridge.speed).toFixed(1) : "—") + " cm/s"
                color: "white"
                font.pixelSize: 16
            }
            Text {
                text: "Display speed: " + (typeof speedText.displaySpeed === "number" ? speedText.displaySpeed.toFixed(1) : "—") + " cm/s"
                color: "yellow"
                font.pixelSize: 16
            }
            Text {
                text: "speedMin: " + speedMin + "   speedMax: " + speedMax
                color: "white"
                font.pixelSize: 16
            }
            Text {
                text: "angleMin: " + angleMin + "   angleMax: " + angleMax
                color: "white"
                font.pixelSize: 16
            }

            Canvas {
                width: 360; height: 220
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    ctx.translate(width/2, height-20);

                    ctx.beginPath();
                    ctx.arc(0, 0, 120,
                            (Math.PI/180)*(-angleMax),
                            (Math.PI/180)*(-angleMin),
                            false);
                    ctx.strokeStyle = "#FFFFFF";
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    function drawRay(deg, color) {
                        ctx.save();
                        ctx.rotate(-(Math.PI/180)*deg);
                        ctx.beginPath();
                        ctx.moveTo(0,0); ctx.lineTo(0,-120);
                        ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
                        ctx.restore();
                    }

                    var s = bridge ? Math.max(0, bridge.speed) : 0;
                    drawRay(angleMin, "#00FF55");
                    drawRay(angleMax, "#FF5555");
                    var cur = mapRangeClamped(s, speedMin, speedMax, angleMin, angleMax);
                    drawRay(cur, "#55AAFF");
                }
                Connections {
                    target: bridge
                    function onSpeedChanged() { parent.requestPaint() }
                }
            }
        }
    }
}
