#include "speed_generator.h"
#include "udp_sender.h"
#include <stdio.h>
#include <stdbool.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

#define DEST_IP "127.0.0.1"  // 受信側body_appのIPアドレス
#define DEST_PORT 50000       // 受信側body_appのポート

// コールバックでUDP送信
void send_speed_callback(int speed) {
    static UdpSender sender;
    static bool initialized = false;
    if (!initialized) {
        if (udp_sender_init(&sender, DEST_IP, DEST_PORT) != 0) {
            printf("[Sender] UDP初期化失敗\n");
            return;
        }
        initialized = true;
    }
    printf("[Sender] 送信: 車速=%d km/h\n", speed);
    udp_send_speed(&sender, speed);
}

int main(void) {
    // 車速生成→UDP送信
    run_speed_generator(send_speed_callback);
    return 0;
}
