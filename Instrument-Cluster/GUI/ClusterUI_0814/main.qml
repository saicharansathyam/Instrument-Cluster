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
    // Set to match your dial and expected speed range.
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

    // ==================== Left gauge (Speed in cm/s) ====================
    Item {
        id: leftGauge
        width: 555; height: 400
        anchors.left: parent.left; anchors.leftMargin: 80
        anchors.verticalCenter: parent.verticalCenter

        // Numeric speed (cm/s), forced non-negative
        Text {
            id: speedText
            text: Math.round(Math.max(0, bridge.speed)).toString()
            anchors.horizontalCenter: parent.horizontalCenter
            y: 240
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            width: 100
            horizontalAlignment: Text.AlignHCenter
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

            // Map cm/s to dial angle with clamping + smoothing
            property real targetAngle: mapRangeClamped(Math.max(0, bridge.speed), speedMin, speedMax, angleMin, angleMax)

            transform: Rotation {
                id: rot
                origin.x: needle.width / 2
                origin.y: needle.height * 0.92 - 25
                angle: needle.targetAngle
            }
            Behavior on targetAngle { NumberAnimation { duration: 180; easing.type: Easing.InOutCubic } }
        }
    }

    // ==================== Right gauge (Battery % + Gear) ====================
    Item {
        id: rightGauge
        width: 510; height: 400
        anchors.right: parent.right; anchors.rightMargin: 80
        anchors.verticalCenter: parent.verticalCenter

        Text {
            text: Math.round(Math.max(0, Math.min(100, bridge.battery))).toString() + "%"
            anchors.horizontalCenter: parent.horizontalCenter
            y: 230
            width: 100
            font.family: orbitronFont.name
            font.pixelSize: 40
            color: "white"
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            id: gearText
            text: bridge.gear
            anchors.horizontalCenter: parent.horizontalCenter
            y: 300
            width: 100
            font.family: orbitronFont.name
            font.pixelSize: 30
            color: "white"
            horizontalAlignment: Text.AlignHCenter
        }
    }

    // ==================== Battery icon with pixel-perfect clipping ====================
    // Your battery_icon.png is 1024x1024. The inner fillable window measured in source pixels:
    //   X=210, Y=395, W=590, H=230
    Item {
        id: batteryIcon
        width: 400; height: 160
        x: 735; y: 100

        // Outline image (may letterbox due to PreserveAspectFit)
        Image {
            id: iconOutline
            source: "qrc:/images/battery_icon.png"
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
            smooth: true
        }

        // --- Cavity in PNG's original pixel coordinates ---
        readonly property real cavityX_src: 210
        readonly property real cavityY_src: 395
        readonly property real cavityW_src: 590
        readonly property real cavityH_src: 230

        // Intrinsic PNG size (metadata-backed; falls back if unavailable)
        readonly property real srcW: iconOutline.sourceSize.width  > 0 ? iconOutline.sourceSize.width  : 1024
        readonly property real srcH: iconOutline.sourceSize.height > 0 ? iconOutline.sourceSize.height : 1024

        // Painted size/offsets after PreserveAspectFit (actual on-screen rect)
        readonly property real paintedW: iconOutline.paintedWidth
        readonly property real paintedH: iconOutline.paintedHeight
        readonly property real offsetX: (batteryIcon.width  - paintedW) / 2
        readonly property real offsetY: (batteryIcon.height - paintedH) / 2

        // Map source cavity → painted coordinates
        readonly property real scaleX: paintedW / srcW
        readonly property real scaleY: paintedH / srcH
        readonly property real cavityX: offsetX + cavityX_src * scaleX
        readonly property real cavityY: offsetY + cavityY_src * scaleY
        readonly property real cavityW:           cavityW_src * scaleX
        readonly property real cavityH:           cavityH_src * scaleY

        // Clip container: the fill cannot escape the cavity
        Item {
            id: cavityClip
            x: batteryIcon.cavityX
            y: batteryIcon.cavityY
            width: batteryIcon.cavityW
            height: batteryIcon.cavityH
            clip: true

            // Subtle margin to avoid touching antialiased border
            readonly property real m: 1.2

            Rectangle {
                id: batteryFill
                x: cavityClip.m
                y: cavityClip.m
                width: (cavityClip.width  - 2*cavityClip.m) * (Math.max(0, Math.min(bridge.battery, 100)) / 100.0)
                height: (cavityClip.height - 2*cavityClip.m)
                radius: height / 2
                color: bridge.battery <= 20 ? "#ff0000"
                     : bridge.battery <= 50 ? "#ffaa00"
                     : "#00ff55"
                Behavior on width { NumberAnimation { duration: 200 } }
            }
        }
    }

    // ==================== Calibration Overlay (toggle with F1) ====================
    Keys.onPressed: if (event.key === Qt.Key_F1) { calibOverlay.visible = !calibOverlay.visible; event.accepted = true }

    Rectangle {
        id: calibOverlay
        visible: false
        anchors.fill: parent
        color: "#00000080"
        z: 999

        Column {
            anchors.centerIn: parent
            spacing: 8

            Text { text: "Calibration Overlay (F1 to hide)"; color: "white"; font.pixelSize: 20; font.family: orbitronFont.name }
            Text { text: "speed: " + Math.max(0, bridge.speed).toFixed(1) + " cm/s"; color: "white"; font.pixelSize: 16 }
            Text { text: "speedMin: " + speedMin + "   speedMax: " + speedMax; color: "white"; font.pixelSize: 16 }
            Text { text: "angleMin: " + angleMin + "   angleMax: " + angleMax; color: "white"; font.pixelSize: 16 }

            Canvas {
                width: 360; height: 220
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    ctx.translate(width/2, height-20);

                    // Dial arc (between angleMax and angleMin)
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
                    drawRay(angleMin, "#00FF55"); // min angle (green)
                    drawRay(angleMax, "#FF5555"); // max angle (red)

                    // current angle (blue), clamped
                    var cur = mapRangeClamped(Math.max(0, bridge.speed), speedMin, speedMax, angleMin, angleMax);
                    drawRay(cur, "#55AAFF");
                }
            }
        }
    }
}
