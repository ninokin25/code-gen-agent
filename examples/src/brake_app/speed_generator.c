/*
 * 簡易車速生成モジュール
 *
 * 一定周期で車速値を生成し、コールバック関数で通知する。
 */

#include <stdio.h>
#include <stdbool.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

#define SPEED_GEN_CYCLE_MS 500

// 車速生成コールバック型
typedef void (*SpeedCallback)(int speed);

// サンプル車速パターン
static int speed_pattern[] = {0, 5, 12, 20, 35, 40, 50, 60, 35, 20, 18, 7, 0, 0, 0};
static int speed_pattern_len = sizeof(speed_pattern) / sizeof(speed_pattern[0]);

// 車速生成メインループ
void run_speed_generator(SpeedCallback cb) {
    int idx = 0;
    while (1) {
        int speed = speed_pattern[idx];
        if (cb) cb(speed);
        idx = (idx + 1) % speed_pattern_len;
#ifdef _WIN32
        Sleep(SPEED_GEN_CYCLE_MS);
#else
        usleep(SPEED_GEN_CYCLE_MS * 1000);
#endif
    }
}

// デモ用コールバック
void print_speed(int speed) {
    printf("[SpeedGen] Speed: %d km/h\n", speed);
}

#ifdef SPEED_GEN_DEMO_MAIN
int main(void) {
    run_speed_generator(print_speed);
    return 0;
}
#endif
