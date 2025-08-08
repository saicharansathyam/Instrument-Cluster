#include "PiRacerBridge.h"
#include <QtMath>
#include <QtDBus/QtDBus>
#include <QDebug>

static const char* IFACE = "com.piracer.dashboard";
static const char* OBJ   = "/com/piracer/dashboard";

PiRacerBridge::PiRacerBridge(QObject *parent)
    : QObject(parent), m_speed(0.0), m_battery(0.0), m_gear("P") {}

void PiRacerBridge::initDBus() {
    QDBusConnection bus = QDBusConnection::sessionBus();

    bus.connect(IFACE, OBJ, IFACE, "SpeedChanged",
                this, SLOT(onSpeedChanged(double)));
    bus.connect(IFACE, OBJ, IFACE, "BatteryChanged",
                this, SLOT(onBatteryChanged(double)));
    bus.connect(IFACE, OBJ, IFACE, "GearChanged",
                this, SLOT(onGearChanged(QString)));

    // 초기값 가져오기
    QDBusInterface iface(IFACE, OBJ, IFACE, bus);
    if (iface.isValid()) {
        QDBusReply<double> sp = iface.call("GetSpeed");
        if (sp.isValid()) onSpeedChanged(sp.value());

        QDBusReply<double> bt = iface.call("GetBatteryLevel");
        if (bt.isValid()) onBatteryChanged(bt.value());

        QDBusReply<QString> gr = iface.call("GetGear");
        if (gr.isValid()) onGearChanged(gr.value());
    } else {
        qWarning() << "[DBus] Interface invalid. Start service first.";
    }
}

double PiRacerBridge::speed() const {
    return m_speed;
}

double PiRacerBridge::battery() const {
    return m_battery;
}

QString PiRacerBridge::gear() const {
    return m_gear;
}

void PiRacerBridge::onSpeedChanged(double newSpeed) {
    if (qFabs(m_speed - newSpeed) > 0.1) {
        m_speed = newSpeed;
        emit speedChanged();
    }
}

void PiRacerBridge::onBatteryChanged(double newBattery) {
    if (qFabs(m_battery - newBattery) > 0.1) {
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

