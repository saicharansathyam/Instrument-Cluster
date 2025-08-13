/****************************************************************************
** Meta object code from reading C++ file 'PiRacerBridge.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.8)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../../PiRacerBridge.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'PiRacerBridge.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.8. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_PiRacerBridge_t {
    QByteArrayData data[15];
    char stringdata0[157];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_PiRacerBridge_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_PiRacerBridge_t qt_meta_stringdata_PiRacerBridge = {
    {
QT_MOC_LITERAL(0, 0, 13), // "PiRacerBridge"
QT_MOC_LITERAL(1, 14, 12), // "speedChanged"
QT_MOC_LITERAL(2, 27, 0), // ""
QT_MOC_LITERAL(3, 28, 14), // "batteryChanged"
QT_MOC_LITERAL(4, 43, 11), // "gearChanged"
QT_MOC_LITERAL(5, 55, 14), // "onSpeedChanged"
QT_MOC_LITERAL(6, 70, 8), // "newSpeed"
QT_MOC_LITERAL(7, 79, 16), // "onBatteryChanged"
QT_MOC_LITERAL(8, 96, 10), // "newBattery"
QT_MOC_LITERAL(9, 107, 13), // "onGearChanged"
QT_MOC_LITERAL(10, 121, 7), // "newGear"
QT_MOC_LITERAL(11, 129, 8), // "initDBus"
QT_MOC_LITERAL(12, 138, 5), // "speed"
QT_MOC_LITERAL(13, 144, 7), // "battery"
QT_MOC_LITERAL(14, 152, 4) // "gear"

    },
    "PiRacerBridge\0speedChanged\0\0batteryChanged\0"
    "gearChanged\0onSpeedChanged\0newSpeed\0"
    "onBatteryChanged\0newBattery\0onGearChanged\0"
    "newGear\0initDBus\0speed\0battery\0gear"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_PiRacerBridge[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       7,   14, // methods
       3,   62, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   49,    2, 0x06 /* Public */,
       3,    0,   50,    2, 0x06 /* Public */,
       4,    0,   51,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       5,    1,   52,    2, 0x0a /* Public */,
       7,    1,   55,    2, 0x0a /* Public */,
       9,    1,   58,    2, 0x0a /* Public */,

 // methods: name, argc, parameters, tag, flags
      11,    0,   61,    2, 0x02 /* Public */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void, QMetaType::Double,    6,
    QMetaType::Void, QMetaType::Double,    8,
    QMetaType::Void, QMetaType::QString,   10,

 // methods: parameters
    QMetaType::Void,

 // properties: name, type, flags
      12, QMetaType::Double, 0x00495001,
      13, QMetaType::Double, 0x00495001,
      14, QMetaType::QString, 0x00495001,

 // properties: notify_signal_id
       0,
       1,
       2,

       0        // eod
};

void PiRacerBridge::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<PiRacerBridge *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->speedChanged(); break;
        case 1: _t->batteryChanged(); break;
        case 2: _t->gearChanged(); break;
        case 3: _t->onSpeedChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 4: _t->onBatteryChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 5: _t->onGearChanged((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 6: _t->initDBus(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (PiRacerBridge::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&PiRacerBridge::speedChanged)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (PiRacerBridge::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&PiRacerBridge::batteryChanged)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (PiRacerBridge::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&PiRacerBridge::gearChanged)) {
                *result = 2;
                return;
            }
        }
    }
#ifndef QT_NO_PROPERTIES
    else if (_c == QMetaObject::ReadProperty) {
        auto *_t = static_cast<PiRacerBridge *>(_o);
        (void)_t;
        void *_v = _a[0];
        switch (_id) {
        case 0: *reinterpret_cast< double*>(_v) = _t->speed(); break;
        case 1: *reinterpret_cast< double*>(_v) = _t->battery(); break;
        case 2: *reinterpret_cast< QString*>(_v) = _t->gear(); break;
        default: break;
        }
    } else if (_c == QMetaObject::WriteProperty) {
    } else if (_c == QMetaObject::ResetProperty) {
    }
#endif // QT_NO_PROPERTIES
}

QT_INIT_METAOBJECT const QMetaObject PiRacerBridge::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_PiRacerBridge.data,
    qt_meta_data_PiRacerBridge,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *PiRacerBridge::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *PiRacerBridge::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_PiRacerBridge.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int PiRacerBridge::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 7)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 7;
    }
#ifndef QT_NO_PROPERTIES
    else if (_c == QMetaObject::ReadProperty || _c == QMetaObject::WriteProperty
            || _c == QMetaObject::ResetProperty || _c == QMetaObject::RegisterPropertyMetaType) {
        qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    } else if (_c == QMetaObject::QueryPropertyDesignable) {
        _id -= 3;
    } else if (_c == QMetaObject::QueryPropertyScriptable) {
        _id -= 3;
    } else if (_c == QMetaObject::QueryPropertyStored) {
        _id -= 3;
    } else if (_c == QMetaObject::QueryPropertyEditable) {
        _id -= 3;
    } else if (_c == QMetaObject::QueryPropertyUser) {
        _id -= 3;
    }
#endif // QT_NO_PROPERTIES
    return _id;
}

// SIGNAL 0
void PiRacerBridge::speedChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void PiRacerBridge::batteryChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}

// SIGNAL 2
void PiRacerBridge::gearChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 2, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
