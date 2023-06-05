import socket
from select import select

###############################################
# Простейший асинхронный сокет
#
# Используется:
#
# - Разделение разных действий на разные функции. server, accept_connection, send_message
#
# - Эвент луп который в бесконечном цикле определяет состояния сокетов. Есть ли что-то в их буфере обмена и готовс ли скоет это читать.
#       - Если готов читать серверный сокет то запускается функция добавления клиента
#       - Если готов читать клинтский сокет то запускается функция получения сообщения от клиента и отправки клиенту респонса
#
# - Функция select. Смотрит на список сокетов и создает подсписки по их состоянию. Список готовых читать, список готовых писать, список ошибок
#       - В линуксе сокеты это файлы тк в линуксе все это файлы
#
# - Глобальный список to_monitor, что бы функция select знала что мониторить
#
###############################################

to_monitor: list[socket.socket] = []


def server() -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("localhost", 5002))
    s.listen()

    return s


def accept_connection(server_socket: socket.socket) -> None:
    # Добавление сокета. Чтение его и добавление в список на мониторинг
    print("Ready to accept")
    client_socket, addr = server_socket.accept()
    print("Connection from:", addr)

    to_monitor.append(client_socket)


def send_message(client_socket: socket.socket) -> None:
    # Общаемся с клиентом
    request = client_socket.recv(4096)
    print(f"Processing of a request: {request}")

    if request:
        response = "Very importamnt response to client\n".encode()
        client_socket.send(response)
    else:
        client_socket.close()


def event_loop(server_socket):

    while True:
        ready_to_read, _, _ = select(to_monitor, [], [])  # read, write, errors

        for sock in ready_to_read:

            if sock is server_socket:
                accept_connection(sock)
            else:
                send_message(sock)


if __name__ == "__main__":

    server_socket = server()
    to_monitor.append(server_socket)
    event_loop(server_socket)
