#ifndef DOORLOCK_CONTROL_H
#define DOORLOCK_CONTROL_H
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    SHIFT_P,
    SHIFT_N,
    SHIFT_D,
    SHIFT_R
} ShiftPosition;

typedef enum {
    LOCK,
    UNLOCK
} DoorLockCommand;

typedef enum {
    LOCKED,
    UNLOCKED
} DoorLockState;

typedef struct {
    DoorLockCommand last_command;
    uint32_t last_command_time;
    bool is_manual;
} DoorLockHistory;

DoorLockCommand update_door_lock_state(
    int vehicle_speed_kph,
    ShiftPosition shift_position,
    DoorLockCommand driver_lock_switch,
    DoorLockCommand passenger_lock_switch,
    DoorLockCommand rear_lock_switch,
    uint32_t current_time_ms
);

#endif // DOORLOCK_CONTROL_H
