import cv2
import numpy as np
import socket
from PIL import Image
from zlib import decompress
from win32api import GetSystemMetrics


WIDTH, HEIGHT = GetSystemMetrics(0), GetSystemMetrics(1)
print(WIDTH, HEIGHT)

PORT = 1234
SERVER_IP = "192.168.1.18"
ADDR = (SERVER_IP, PORT)


def create_socket_connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(ADDR)

    return sock


def recv_img_data(sock):
    size_len = int.from_bytes(sock.recv(1), "big")
    size = int.from_bytes(sock.recv(size_len), "big")

    buf = b""
    while len(buf) < size:
        data = sock.recv(size - len(buf))

        if not data:
            print("not data")
            return data

        buf += data

    data = decompress(buf)

    return data


def main():
    # region Creating a socket and connecting to the server
    print(f"Connecting to {SERVER_IP} on port {PORT}...")

    sock = create_socket_connect()

    print(f"Connected {ADDR}")
    # endregion

    server_width = int.from_bytes(sock.recv(1024), "big")
    server_height = int.from_bytes(sock.recv(1024), "big")

    num = 0

    while True:
        data = recv_img_data(sock)

        if data == -1:
            print("yes")
            continue

        img = Image.frombytes("RGB", (server_width, server_height), data)
        img = np.array(img)[:, :, ::-1]
        img = cv2.resize(img, (WIDTH, HEIGHT))
        cv2.imshow("Screen", img)
        cv2.waitKey(1)

        num += 1


if __name__ == '__main__':
    main()
