/*
 * UDP送信モジュール
 *
 * 指定したIPアドレス・ポートに車速値をUDPで送信する。
 */

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

#include "udp_sender.h"

int udp_sender_init(UdpSender *sender, const char *ip, int port) {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) {
        printf("WSAStartup failed\n");
        return -1;
    }
#endif
    sender->sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sender->sock < 0) {
        perror("socket");
        return -1;
    }
    memset(&sender->addr, 0, sizeof(sender->addr));
    sender->addr.sin_family = AF_INET;
    sender->addr.sin_port = htons(port);
    sender->addr.sin_addr.s_addr = inet_addr(ip);
    return 0;
}

void udp_sender_close(UdpSender *sender) {
#ifdef _WIN32
    closesocket(sender->sock);
    WSACleanup();
#else
    close(sender->sock);
#endif
}

int udp_send_speed(UdpSender *sender, int speed) {
    // 速度を4バイトのバイナリで送信
    unsigned char buf[4];
    buf[0] = (speed >> 24) & 0xFF;
    buf[1] = (speed >> 16) & 0xFF;
    buf[2] = (speed >> 8) & 0xFF;
    buf[3] = speed & 0xFF;
    int ret = sendto(sender->sock, (const char*)buf, 4, 0,
                     (struct sockaddr*)&sender->addr, sizeof(sender->addr));
    if (ret < 0) {
        perror("sendto");
        return -1;
    }
    return 0;
}
