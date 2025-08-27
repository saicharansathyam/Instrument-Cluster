/****************************************************************************
** Meta object code from reading C++ file 'PiRacerBridge.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.13)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../PiRacerBridge.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'PiRacerBridge.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.13. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_PiRacerBridge_t {
    QByteArrayData data[26];
    char stringdata0[294];
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
QT_MOC_LITERAL(5, 55, 15), // "leftTurnChanged"
QT_MOC_LITERAL(6, 71, 16), // "rightTurnChanged"
QT_MOC_LITERAL(7, 88, 13), // "hazardChanged"
QT_MOC_LITERAL(8, 102, 14), // "onSpeedChanged"
QT_MOC_LITERAL(9, 117, 8), // "newSpeed"
QT_MOC_LITERAL(10, 126, 16), // "onBatteryChanged"
QT_MOC_LITERAL(11, 143, 10), // "newBattery"
QT_MOC_LITERAL(12, 154, 13), // "onGearChanged"
QT_MOC_LITERAL(13, 168, 7), // "newGear"
QT_MOC_LITERAL(14, 176, 19), // "onTurnSignalChanged"
QT_MOC_LITERAL(15, 196, 4), // "mode"
QT_MOC_LITERAL(16, 201, 17), // "onLeftTurnChanged"
QT_MOC_LITERAL(17, 219, 1), // "v"
QT_MOC_LITERAL(18, 221, 18), // "onRightTurnChanged"
QT_MOC_LITERAL(19, 240, 8), // "initDBus"
QT_MOC_LITERAL(20, 249, 5), // "speed"
QT_MOC_LITERAL(21, 255, 7), // "battery"
QT_MOC_LITERAL(22, 263, 4), // "gear"
QT_MOC_LITERAL(23, 268, 8), // "leftTurn"
QT_MOC_LITERAL(24, 277, 9), // "rightTurn"
QT_MOC_LITERAL(25, 287, 6) // "hazard"

    },
    "PiRacerBridge\0speedChanged\0\0batteryChanged\0"
    "gearChanged\0leftTurnChanged\0"
    "rightTurnChanged\0hazardChanged\0"
    "onSpeedChanged\0newSpeed\0onBatteryChanged\0"
    "newBattery\0onGearChanged\0newGear\0"
    "onTurnSignalChanged\0mode\0onLeftTurnChanged\0"
    "v\0onRightTurnChanged\0initDBus\0speed\0"
    "battery\0gear\0leftTurn\0rightTurn\0hazard"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_PiRacerBridge[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
      13,   14, // methods
       6,  104, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       6,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   79,    2, 0x06 /* Public */,
       3,    0,   80,    2, 0x06 /* Public */,
       4,    0,   81,    2, 0x06 /* Public */,
       5,    0,   82,    2, 0x06 /* Public */,
       6,    0,   83,    2, 0x06 /* Public */,
       7,    0,   84,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       8,    1,   85,    2, 0x0a /* Public */,
      10,    1,   88,    2, 0x0a /* Public */,
      12,    1,   91,    2, 0x0a /* Public */,
      14,    1,   94,    2, 0x0a /* Public */,
      16,    1,   97,    2, 0x0a /* Public */,
      18,    1,  100,    2, 0x0a /* Public */,

 // methods: name, argc, parameters, tag, flags
      19,    0,  103,    2, 0x02 /* Public */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void, QMetaType::Double,    9,
    QMetaType::Void, QMetaType::Double,   11,
    QMetaType::Void, QMetaType::QString,   13,
    QMetaType::Void, QMetaType::QString,   15,
    QMetaType::Void, QMetaType::Bool,   17,
    QMetaType::Void, QMetaType::Bool,   17,

 // methods: parameters
    QMetaType::Void,

 // properties: name, type, flags
      20, QMetaType::Double, 0x00495001,
      21, QMetaType::Double, 0x00495001,
      22, QMetaType::QString, 0x00495001,
      23, QMetaType::Bool, 0x00495001,
      24, QMetaType::Bool, 0x00495001,
      25, QMetaType::Bool, 0x00495001,

 // properties: notify_signal_id
       0,
       1,
       2,
       3,
       4,
       5,

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
        case 3: _t->leftTurnChanged(); break;
        case 4: _t->rightTurnChanged(); break;
        case 5: _t->hazardChanged(); break;
        case 6: _t->onSpeedChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 7: _t->onBatteryChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 8: _t->onGearChanged((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 9: _t->onTurnSignalChanged((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 10: _t->onLeftTurnChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 11: _t->onRightTurnChanged((*reinterpret_cast< bool(*)>(_a[1]))); break;
        case 12: _t->initDBus(); break;
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
        {
            using _t = void (PiRacerBridge::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&PiRacerBridge::leftTurnChanged)) {
                *result = 3;
                return;
            }
        }
        {
            using _t = void (PiRacerBridge::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&PiRacerBridge::rightTurnChanged)) {
                *result = 4;
                return;
            }
        }
        {
            using _t = void (PiRacerBridge::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&PiRacerBridge::hazardChanged)) {
                *result = 5;
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
        case 3: *reinterpret_cast< bool*>(_v) = _t->leftTurn(); break;
        case 4: *reinterpret_cast< bool*>(_v) = _t->rightTurn(); break;
        case 5: *reinterpret_cast< bool*>(_v) = _t->hazard(); break;
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
        if (_id < 13)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 13;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 13)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 13;
    }
#ifndef QT_NO_PROPERTIES
    else if (_c == QMetaObject::ReadProperty || _c == QMetaObject::WriteProperty
            || _c == QMetaObject::ResetProperty || _c == QMetaObject::RegisterPropertyMetaType) {
        qt_static_metacall(this, _c, _id, _a);
        _id -= 6;
    } else if (_c == QMetaObject::QueryPropertyDesignable) {
        _id -= 6;
    } else if (_c == QMetaObject::QueryPropertyScriptable) {
        _id -= 6;
    } else if (_c == QMetaObject::QueryPropertyStored) {
        _id -= 6;
    } else if (_c == QMetaObject::QueryPropertyEditable) {
        _id -= 6;
    } else if (_c == QMetaObject::QueryPropertyUser) {
        _id -= 6;
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

// SIGNAL 3
void PiRacerBridge::leftTurnChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 3, nullptr);
}

// SIGNAL 4
void PiRacerBridge::rightTurnChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 4, nullptr);
}

// SIGNAL 5
void PiRacerBridge::hazardChanged()
{
    QMetaObject::activate(this, &staticMetaObject, 5, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
