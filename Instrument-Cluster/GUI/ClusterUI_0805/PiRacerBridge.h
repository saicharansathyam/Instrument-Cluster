#ifndef PIRACERBRIDGE_H
#define PIRACERBRIDGE_H

#include <QObject>
#include <QString>

class PiRacerBridge : public QObject {
    Q_OBJECT
    Q_PROPERTY(double speed READ speed NOTIFY speedChanged)     // cm/s
    Q_PROPERTY(double battery READ battery NOTIFY batteryChanged)
    Q_PROPERTY(QString gear READ gear NOTIFY gearChanged)

public:
    explicit PiRacerBridge(QObject *parent = nullptr);

    double speed() const;
    double battery() const;
    QString gear() const;

    Q_INVOKABLE void initDBus();  // D-Bus 연결 초기화

public slots:
    void onSpeedChanged(double newSpeed);
    void onBatteryChanged(double newBattery);
    void onGearChanged(const QString &newGear);

signals:
    void speedChanged();
    void batteryChanged();
    void gearChanged();

private:
    double m_speed;
    double m_battery;
    QString m_gear;
};

#endif // PIRACERBRIDGE_H
