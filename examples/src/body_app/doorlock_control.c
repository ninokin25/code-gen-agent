#include "doorlock_control.h"
#include <stdint.h>
#include <stdbool.h>

#define MANUAL_OVERRIDE_PERIOD_MS 30000
#define LOCK_SPEED_THRESHOLD 20

static int manual_override_timer = 0;
static DoorLockState door_lock_state = UNLOCKED;
static DoorLockHistory history = {UNLOCK, 0, false};

// タイマ更新用関数（100msごとに呼び出し）
static void update_manual_override_timer(int elapsed_ms) {
    if (manual_override_timer > 0) {
        manual_override_timer -= elapsed_ms;
        if (manual_override_timer < 0) manual_override_timer = 0;
    }
}

// 手動操作検出（スイッチの前回値と比較）
static DoorLockCommand prev_driver = UNLOCK;
static DoorLockCommand prev_passenger = UNLOCK;
static DoorLockCommand prev_rear = UNLOCK;
static bool is_manual_operation(DoorLockCommand driver, DoorLockCommand passenger, DoorLockCommand rear) {
    bool manual = false;
    if (driver != prev_driver || passenger != prev_passenger || rear != prev_rear) {
        manual = true;
    }
    prev_driver = driver;
    prev_passenger = passenger;
    prev_rear = rear;
    return manual;
}

DoorLockCommand update_door_lock_state(
    int vehicle_speed_kph,
    ShiftPosition shift_position,
    DoorLockCommand driver_lock_switch,
    DoorLockCommand passenger_lock_switch,
    DoorLockCommand rear_lock_switch,
    uint32_t current_time_ms
) {
    // 入力信号異常チェック
    if (vehicle_speed_kph < 0 || shift_position < SHIFT_P || shift_position > SHIFT_R) {
        return door_lock_state == LOCKED ? LOCK : UNLOCK;
    }

    // 手動操作優先
    if (is_manual_operation(driver_lock_switch, passenger_lock_switch, rear_lock_switch)) {
        manual_override_timer = MANUAL_OVERRIDE_PERIOD_MS;
        history.last_command = driver_lock_switch; // 代表値
        history.last_command_time = current_time_ms;
        history.is_manual = true;
        door_lock_state = (driver_lock_switch == LOCK) ? LOCKED : UNLOCKED;
        return driver_lock_switch;
    }

    // タイマ更新
    update_manual_override_timer(100);
    if (manual_override_timer > 0) {
        // 手動操作後は自動制御無効
        return door_lock_state == LOCKED ? LOCK : UNLOCK;
    }

    // 自動制御
    if (vehicle_speed_kph >= LOCK_SPEED_THRESHOLD && door_lock_state == UNLOCKED) {
        door_lock_state = LOCKED;
        history.last_command = LOCK;
        history.last_command_time = current_time_ms;
        history.is_manual = false;
        return LOCK;
    }
    if (vehicle_speed_kph == 0 && shift_position == SHIFT_P && door_lock_state == LOCKED) {
        door_lock_state = UNLOCKED;
        history.last_command = UNLOCK;
        history.last_command_time = current_time_ms;
        history.is_manual = false;
        return UNLOCK;
    }
    // 状態維持
    return door_lock_state == LOCKED ? LOCK : UNLOCK;
}
