import socket

# domain:5000

###############################################
# Синхронный сокет. Работатет только с одним подключением одновременно.
# Не может принять другие пока не отключился предыдущий.
###############################################

# создаем сокет IPv4
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # задаем настройку переиспользования адреса, иначе при отключении система будет ждать таймаута для порта
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # биндим к сокету конкретный хост и порт
    s.bind(("localhost", 5002))
    # включаем сокет на прием входящих подключений пользовтелей
    s.listen()

    while True:
        # Ждет входящего подключения. Блокирующаяя операция
        print("Ready to accept")
        client_socket, addr = s.accept()
        print("Connection from:", addr)

        with client_socket:
            while True:
                # Ждет пока сокет подключенного клиента что-то отправит. Блокирующаяя операция
                request = client_socket.recv(4096)
                print(f"Processing of a request: {request}")

                if request:
                    # переводим строку в байтс
                    response = "Very importamnt response to client\n".encode()
                    # отсылаем клиенту
                    client_socket.send(response)
                else:
                    break

        # Закрываем клиентский сокет. Контестный менеджер делает это сам
        # client_socket.close()
