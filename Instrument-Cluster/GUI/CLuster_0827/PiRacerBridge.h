#ifndef PIRACERBRIDGE_H
#define PIRACERBRIDGE_H

#include <QObject>
#include <QString>

class PiRacerBridge : public QObject {
    Q_OBJECT
    // ---- QML에서 사용하는 프로퍼티 ----
    Q_PROPERTY(double  speed     READ speed     NOTIFY speedChanged)       // cm/s
    Q_PROPERTY(double  battery   READ battery   NOTIFY batteryChanged)     // 0~100%
    Q_PROPERTY(QString gear      READ gear      NOTIFY gearChanged)        // "P","R","N","D"
    Q_PROPERTY(bool    leftTurn  READ leftTurn  NOTIFY leftTurnChanged)    // 좌 방향지시등
    Q_PROPERTY(bool    rightTurn READ rightTurn NOTIFY rightTurnChanged)   // 우 방향지시등
    Q_PROPERTY(bool    hazard    READ hazard    NOTIFY hazardChanged)      // 비상등

public:
    explicit PiRacerBridge(QObject *parent = nullptr);

    // QML에서 바로 쓰는 getter
    double  speed()    const { return m_speed; }
    double  battery()  const { return m_battery; }
    QString gear()     const { return m_gear; }
    bool    leftTurn() const { return m_leftTurn; }
    bool    rightTurn()const { return m_rightTurn; }
    bool    hazard()   const { return m_hazard; }

    // DBus 연결 (main.cpp에서 호출)
    Q_INVOKABLE void initDBus();

signals:
    void speedChanged();
    void batteryChanged();
    void gearChanged();
    void leftTurnChanged();
    void rightTurnChanged();
    void hazardChanged();

public slots:
    // DBus 신호 슬롯
    void onSpeedChanged(double newSpeed);
    void onBatteryChanged(double newBattery);
    void onGearChanged(const QString &newGear);

    // ① 문자열 기반 (파이썬 현재 구조와 호환)
    void onTurnSignalChanged(const QString &mode);

    // ② (선택) bool 기반도 지원(나중에 파이썬이 분리 신호를 보낼 수도 있으니 겸용)
    void onLeftTurnChanged(bool v);
    void onRightTurnChanged(bool v);
    // void onHazardChanged(bool v); // 필요시 사용

private:
    // 헬퍼: 상태 변경 시 NOTIFY만 필요한 경우 공통 처리
    void setTurnState(bool left, bool right, bool hazard);

private:
    double  m_speed   = 0.0;
    double  m_battery = 0.0;
    QString m_gear    = "P";
    bool    m_leftTurn  = false;
    bool    m_rightTurn = false;
    bool    m_hazard    = false;
};

#endif // PIRACERBRIDGE_H
