/*
 * UDP受信モジュール（body_app用）
 *
 * brake_appから送信された車速データ（4バイトint）をUDPで受信し、標準出力に表示する。
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

#define UDP_PORT 50000
#define UDP_BUFSIZE 4


// 受信処理本体を関数化
void udp_receive_speed(void) {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) {
        printf("WSAStartup failed\n");
        return;
    }
#endif
    int sockfd;
    struct sockaddr_in addr, sender_addr;
    unsigned char buf[UDP_BUFSIZE];
#ifdef _WIN32
    int addrlen = sizeof(sender_addr);
#else
    socklen_t addrlen = sizeof(sender_addr);
#endif

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return;
    }
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(UDP_PORT);

    if (bind(sockfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
#ifdef _WIN32
        closesocket(sockfd);
        WSACleanup();
#else
        close(sockfd);
#endif
        return;
    }

    printf("[Receiver] Waiting on UDP port %d...\n", UDP_PORT);
    while (1) {
        int n = recvfrom(sockfd, (char*)buf, UDP_BUFSIZE, 0, (struct sockaddr *)&sender_addr, &addrlen);
        if (n == UDP_BUFSIZE) {
            int speed = (buf[0]<<24) | (buf[1]<<16) | (buf[2]<<8) | buf[3];
            printf("[Receiver] Received: speed=%d km/h\n", speed);
        } else if (n > 0) {
            printf("[Receiver] Invalid data received: %d bytes\n", n);
        } else {
            perror("recvfrom");
            break;
        }
    }
#ifdef _WIN32
    closesocket(sockfd);
    WSACleanup();
#else
    close(sockfd);
#endif
}
