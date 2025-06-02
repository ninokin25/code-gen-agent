#include "doorlock_childlock_control.h"
#include <stdio.h>
#include <stdbool.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

int main(void) {
    DoorLockState state = {false, false, false};

    // サンプルシナリオ
    int speeds[] = {0, 5, 12, 15, 8, 0};
    bool rear_seat[] = {false, true, true, true, false, false};
    int steps = sizeof(speeds) / sizeof(speeds[0]);

    for (int i = 0; i < steps; ++i) {
        printf("\n[STEP %d] speed=%d km/h, rear_seat_occupied=%s\n", i+1, speeds[i], rear_seat[i] ? "YES" : "NO");
        update_door_lock_state(&state, speeds[i], rear_seat[i]);
        printf("  -> ドアロック状態: %s\n", state.door_locked ? "ON" : "OFF");
        printf("  -> チャイルドロック状態: %s\n", state.child_lock_enabled ? "ON" : "OFF");

        // 500ms周期で制御を実行
#ifdef _WIN32
        Sleep(500); // Windows: 500ms
#else
        usleep(500000); // POSIX: 500,000us = 500ms
#endif
    }
    return 0;
}
