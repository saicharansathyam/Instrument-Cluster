#include <QApplication>
#include <QWidget>
#include <QLabel>
#include <QVBoxLayout>
#include <QTimer>
#include <QDBusConnection>
#include <QDBusInterface>
#include <QDBusReply>
#include <QFont>

class SpeedDisplay : public QWidget
{
    Q_OBJECT

public:
    SpeedDisplay(QWidget *parent = nullptr) : QWidget(parent)
    {
        // Create UI
        setWindowTitle("PiRacer Speed Display");
        resize(300, 200);
        
        speedLabel = new QLabel("0.0 km/h", this);
        speedLabel->setAlignment(Qt::AlignCenter);
        
        // Make text big and green
        QFont font = speedLabel->font();
        font.setPointSize(24);
        font.setBold(true);
        speedLabel->setFont(font);
        speedLabel->setStyleSheet("color: #00ff00; background-color: #1a1a1a;");
        
        statusLabel = new QLabel("Connecting...", this);
        statusLabel->setAlignment(Qt::AlignCenter);
        statusLabel->setStyleSheet("color: #888888;");
        
        QVBoxLayout *layout = new QVBoxLayout(this);
        layout->addWidget(speedLabel);
        layout->addWidget(statusLabel);
        
        // Connect to D-Bus
        connectToDBus();
        
        // Update speed every 500ms
        timer = new QTimer(this);
        connect(timer, &QTimer::timeout, this, &SpeedDisplay::updateSpeed);
        timer->start(500);
    }

private slots:
    void updateSpeed()
    {
        if (!dbusInterface) {
            statusLabel->setText("D-Bus connection failed");
            return;
        }
        
        // Call GetSpeed method
        QDBusReply<double> reply = dbusInterface->call("GetSpeed");
        
        if (reply.isValid()) {
            double speed = reply.value();
            speedLabel->setText(QString::number(speed, 'f', 1) + " km/h");
            statusLabel->setText("Connected - Real CAN data");
        } else {
            statusLabel->setText("Failed to get speed");
        }
    }

private:
    void connectToDBus()
    {
        QDBusConnection bus = QDBusConnection::sessionBus();
        
        if (!bus.isConnected()) {
            statusLabel->setText("Cannot connect to D-Bus");
            return;
        }
        
        dbusInterface = new QDBusInterface("com.piracer.speed",
                                           "/com/piracer/speed", 
                                           "com.piracer.speed",
                                           bus, this);
        
        if (!dbusInterface->isValid()) {
            statusLabel->setText("D-Bus interface invalid");
            delete dbusInterface;
            dbusInterface = nullptr;
        }
    }
    
    QLabel *speedLabel;
    QLabel *statusLabel;
    QTimer *timer;
    QDBusInterface *dbusInterface = nullptr;
};

#include "simple_speed_display.moc"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    SpeedDisplay display;
    display.show();
    
    return app.exec();
}
