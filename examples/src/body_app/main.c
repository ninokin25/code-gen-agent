#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif


#include "doorlock_control.h"

#define UDP_PORT 50000
#define UDP_BUFSIZE 4
#define CONTROL_PERIOD_MS 500

#include "udp_receiver.h"



// シフトレンジ・スイッチ入力はダミー（常にD/UNLOCK）
static ShiftPosition get_shift_position(void) { return SHIFT_D; }
static DoorLockCommand get_driver_lock_switch(void) { return UNLOCK; }
static DoorLockCommand get_passenger_lock_switch(void) { return UNLOCK; }
static DoorLockCommand get_rear_lock_switch(void) { return UNLOCK; }

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif


int main(void) {
    ShiftPosition shift_position = SHIFT_D;
    DoorLockCommand driver_lock_switch = UNLOCK;
    DoorLockCommand passenger_lock_switch = UNLOCK;
    DoorLockCommand rear_lock_switch = UNLOCK;
    uint32_t current_time_ms = 0;

    printf("[App] Speed-linked door lock control application started.\n");
    printf("[App] Receiving vehicle speed via UDP and controlling door lock. (Press Ctrl+C to exit)\n");

    // UDP受信スレッド起動
    start_udp_speed_receiver();

    while (1) {
        int vehicle_speed_kph = get_latest_vehicle_speed();

        // シフト・スイッチは模擬関数で取得
        shift_position = get_shift_position();
        driver_lock_switch = get_driver_lock_switch();
        passenger_lock_switch = get_passenger_lock_switch();
        rear_lock_switch = get_rear_lock_switch();

        DoorLockCommand cmd = update_door_lock_state(
            vehicle_speed_kph,
            shift_position,
            driver_lock_switch,
            passenger_lock_switch,
            rear_lock_switch,
            current_time_ms
        );

        printf("[App] Received speed: %d km/h\n", vehicle_speed_kph);
        if (cmd == LOCK) {
            printf("[App] Door lock command: LOCK\n");
        } else {
            printf("[App] Door lock command: UNLOCK\n");
        }

#ifdef _WIN32
        Sleep(CONTROL_PERIOD_MS);
#else
        usleep(CONTROL_PERIOD_MS * 1000);
#endif
        current_time_ms += CONTROL_PERIOD_MS;
    }
    return 0;
}
