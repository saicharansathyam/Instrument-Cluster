#include "PiRacerBridge.h"
#include <QtDBus/QtDBus>
#include <QtMath>
#include <QDebug>

static const char* IFACE = "com.piracer.dashboard";
static const char* OBJ   = "/com/piracer/dashboard";

PiRacerBridge::PiRacerBridge(QObject *parent)
    : QObject(parent)
{
}

void PiRacerBridge::initDBus() {
    QDBusConnection bus = QDBusConnection::sessionBus();

    bool ok = true;

    // --- 수신 신호 연결 ---
    ok &= bus.connect(IFACE, OBJ, IFACE, "SpeedChanged",
                      this, SLOT(onSpeedChanged(double)));
    ok &= bus.connect(IFACE, OBJ, IFACE, "BatteryChanged",
                      this, SLOT(onBatteryChanged(double)));
    ok &= bus.connect(IFACE, OBJ, IFACE, "GearChanged",
                      this, SLOT(onGearChanged(QString)));

    // 방향지시등: 파이썬이 보내는 문자열 신호 (현재 사용)
    ok &= bus.connect(IFACE, OBJ, IFACE, "TurnSignalChanged",
                      this, SLOT(onTurnSignalChanged(QString)));

    // (겸용) 혹시나 bool 분리 신호도 나올 수 있으니 같이 연결해 둠 (있으면 동작, 없으면 무시)
    bus.connect(IFACE, OBJ, IFACE, "LeftTurnChanged",
                this, SLOT(onLeftTurnChanged(bool)));
    bus.connect(IFACE, OBJ, IFACE, "RightTurnChanged",
                this, SLOT(onRightTurnChanged(bool)));
    // bus.connect(IFACE, OBJ, IFACE, "HazardChanged",
    //             this, SLOT(onHazardChanged(bool)));

    if (!ok) {
        qWarning() << "[DBus] connect() failed for one or more signals";
    }

    // --- 초기값 가져오기 ---
    QDBusInterface iface(IFACE, OBJ, IFACE, bus);
    if (!iface.isValid()) {
        qWarning() << "[DBus] Interface invalid. Start service first.";
        return;
    }

    if (QDBusReply<double> sp = iface.call("GetSpeed"); sp.isValid())
        onSpeedChanged(sp.value());
    if (QDBusReply<double> bt = iface.call("GetBatteryLevel"); bt.isValid())
        onBatteryChanged(bt.value());
    if (QDBusReply<QString> gr = iface.call("GetGear"); gr.isValid())
        onGearChanged(gr.value());

    // 문자열 기반 turn signal 초기값
    if (QDBusReply<QString> ts = iface.call("GetTurnSignal"); ts.isValid())
        onTurnSignalChanged(ts.value());
    // (대안) bool 분리 초기값도 있으면 사용
    // if (QDBusReply<bool> lf = iface.call("GetLeftTurn"); lf.isValid()) onLeftTurnChanged(lf.value());
    // if (QDBusReply<bool> rt = iface.call("GetRightTurn"); rt.isValid()) onRightTurnChanged(rt.value());
}

void PiRacerBridge::onSpeedChanged(double newSpeed) {
    newSpeed = qMax(0.0, newSpeed);
    if (!qFuzzyCompare(m_speed, newSpeed)) {
        m_speed = newSpeed;
        emit speedChanged();
    }
}

void PiRacerBridge::onBatteryChanged(double newBattery) {
    newBattery = qBound(0.0, newBattery, 100.0);
    if (!qFuzzyCompare(m_battery, newBattery)) {
        m_battery = newBattery;
        emit batteryChanged();
    }
}

void PiRacerBridge::onGearChanged(const QString &newGear) {
    if (m_gear != newGear) {
        m_gear = newGear;
        emit gearChanged();
    }
}

// ---- turn signal 처리 ----
void PiRacerBridge::setTurnState(bool left, bool right, bool hazard) {
    bool changed = false;

    if (m_leftTurn != left)   { m_leftTurn = left;   emit leftTurnChanged();   changed = true; }
    if (m_rightTurn != right) { m_rightTurn = right; emit rightTurnChanged();  changed = true; }
    if (m_hazard   != hazard) { m_hazard   = hazard; emit hazardChanged();     changed = true; }

    // changed 여부는 로깅용으로만 사용 가능 (필수 아님)
    if (changed) {
        // qDebug() << "[Bridge] turn state -> L:" << m_leftTurn << " R:" << m_rightTurn << " H:" << m_hazard;
    }
}

// 파이썬이 보내는 문자열 신호 수신: "off" | "left" | "right" | "hazard"
void PiRacerBridge::onTurnSignalChanged(const QString &mode) {
    const QString m = mode.toLower();
    if (m == "left")       setTurnState(true,  false, false);
    else if (m == "right") setTurnState(false, true,  false);
    else if (m == "hazard")setTurnState(true,  true,  true);
    else                   setTurnState(false, false, false); // "off" 또는 알 수 없는 값
}

// (겸용) bool 분리 신호가 들어오는 경우
void PiRacerBridge::onLeftTurnChanged(bool v) {
    setTurnState(v, m_rightTurn, (v && m_rightTurn) ? true : m_hazard);
}

void PiRacerBridge::onRightTurnChanged(bool v) {
    setTurnState(m_leftTurn, v, (m_leftTurn && v) ? true : m_hazard);
}

// 필요 시 구현
// void PiRacerBridge::onHazardChanged(bool v) {
//     if (v) setTurnState(true, true, true);
//     else   setTurnState(m_leftTurn, m_rightTurn, false);
// }
