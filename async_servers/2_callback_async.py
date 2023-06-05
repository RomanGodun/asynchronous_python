import socket
import selectors

###############################################
# Асинхронный сокет на колбэках
#
# Используется:
#
# - Модуль selectors. Вместо листа со списком для мониторинга используется класс selectors.DefaultSelector.
#   В нем мы регестрирует тройки: сокет - тип_эвента - функция для обработки.
#   В эвент лупе мы собираем эвенты записи в буфер сокета и вызываем привязанную функцию
#
###############################################

selector = selectors.DefaultSelector()


def server() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("localhost", 5002))
    s.listen()

    # fileobj - это сокет. В линуксе сокеты это файлы тк в линуксе все это файлы
    # data - функция которая работает с данными в буфере (читает их)
    selector.register(fileobj=s, events=selectors.EVENT_READ, data=accept_connection)


def accept_connection(server_socket: socket.socket):
    # Добавление сокета. Чтение его и добавление в список на мониторинг
    print("Ready to accept")
    client_socket, addr = server_socket.accept()
    print("Connection from:", addr)

    selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=send_message)


def send_message(client_socket: socket.socket):
    # Общаемся с клиентом
    request = client_socket.recv(4096)
    print(f"Processing of a request: {request}")

    if request:
        response = "Very importamnt response to client\n".encode()
        client_socket.send(response)
    else:
        selector.unregister(client_socket)
        client_socket.close()


def event_loop():
    while True:

        # Отбирает эвенты заполнения буфера. Например в буфер обмена стучиться новый пользователь,
        # значит мы можем этого пользователя зарегистрировать в селекторе
        events = selector.select()

        for key, _ in events:
            # callback - функция которая привязана к выбранному готовому сокету
            callback = key.data
            # Вызов функции с сокетом в качестве параметра
            callback(key.fileobj)


if __name__ == "__main__":
    server()
    event_loop()
