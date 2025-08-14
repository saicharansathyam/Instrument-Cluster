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

    bool ok = true;
    ok &= bus.connect(IFACE, OBJ, IFACE, "SpeedChanged",
                      this, SLOT(onSpeedChanged(double)));
    ok &= bus.connect(IFACE, OBJ, IFACE, "BatteryChanged",
                      this, SLOT(onBatteryChanged(double)));
    ok &= bus.connect(IFACE, OBJ, IFACE, "GearChanged",
                      this, SLOT(onGearChanged(QString)));
    if (!ok) qWarning() << "[DBus] connect() failed for one or more signals";

    // Fetch initial values
    QDBusInterface iface(IFACE, OBJ, IFACE, bus);
    if (iface.isValid()) {
        if (QDBusReply<double> sp = iface.call("GetSpeed"); sp.isValid())
            onSpeedChanged(sp.value());
        if (QDBusReply<double> bt = iface.call("GetBatteryLevel"); bt.isValid())
            onBatteryChanged(bt.value());
        if (QDBusReply<QString> gr = iface.call("GetGear"); gr.isValid())
            onGearChanged(gr.value());
    } else {
        qWarning() << "[DBus] Interface invalid. Start service first.";
    }
}

double PiRacerBridge::speed() const   { return m_speed;   }
double PiRacerBridge::battery() const { return m_battery; }
QString PiRacerBridge::gear() const   { return m_gear;    }

void PiRacerBridge::onSpeedChanged(double newSpeed) {
    // Clamp to non-negative to avoid showing minus values
    newSpeed = qMax(0.0, newSpeed);
    if (qFabs(m_speed - newSpeed) > 0.1) {
        m_speed = newSpeed;
        emit speedChanged();
    }
}

void PiRacerBridge::onBatteryChanged(double newBattery) {
    // Clamp to [0, 100] just in case
    newBattery = qBound(0.0, newBattery, 100.0);
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
