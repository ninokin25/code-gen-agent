#ifndef DOORLOCK_CHILDLOCK_CONTROL_H
#define DOORLOCK_CHILDLOCK_CONTROL_H

#include <stdbool.h>

#define SPEED_LOCK_THRESHOLD 10   // km/h
#define SPEED_UNLOCK_THRESHOLD 0  // km/h

typedef struct {
    bool door_locked;
    bool child_lock_enabled;
    bool rear_seat_occupied;
} DoorLockState;

void update_door_lock_state(DoorLockState *state, int speed, bool rear_seat_occupied);

#endif // DOORLOCK_CHILDLOCK_CONTROL_H
