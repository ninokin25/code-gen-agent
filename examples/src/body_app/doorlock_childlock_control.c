/*
 * ドアロック自動制御＋チャイルドロック連動
 *
 * 概要:
 *   車速連動ドアロックに加え、後席乗員検知時はチャイルドロックも自動制御する。
 *
 * 主な機能:
 *   - 車速によるロック/アンロック
 *   - 後席センサで乗員検知時のみチャイルドロックON
 *   - 降車時は自動でチャイルドロック解除
 */

// ドアロック自動制御＋チャイルドロック連動
#include "doorlock_childlock_control.h"
#include <stdio.h>

// 車速・後席センサ入力を受けて状態を更新
void update_door_lock_state(DoorLockState *state, int speed, bool rear_seat_occupied) {
    // ドアロック制御
    if (speed >= SPEED_LOCK_THRESHOLD && !state->door_locked) {
        state->door_locked = true;
        printf("[INFO] ドアロック: ON\n");
    } else if (speed <= SPEED_UNLOCK_THRESHOLD && state->door_locked) {
        state->door_locked = false;
        printf("[INFO] ドアロック: OFF\n");
    }

    // チャイルドロック制御
    if (rear_seat_occupied && state->door_locked && !state->child_lock_enabled) {
        state->child_lock_enabled = true;
        printf("[INFO] チャイルドロック: ON\n");
    } else if ((!rear_seat_occupied || !state->door_locked) && state->child_lock_enabled) {
        state->child_lock_enabled = false;
        printf("[INFO] チャイルドロック: OFF\n");
    }

    // 後席乗員状態の記録
    state->rear_seat_occupied = rear_seat_occupied;
}
