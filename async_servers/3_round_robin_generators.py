import socket
from select import select
from collections import deque

###############################################
# David Beazley. Concurrency from the Ground up live. 2015
#
# Асинхронность на генераторах и концепции round robin (карусель)
#
# Концепция состоит в том что у нас есть генератор-сервер который делает генераторы-клиенты (первым начинает выполняться в эвент лупе).
# ГК отправляются в очередб на выполнение в эвент лупе (блок try)
# (ГС тоже отпраляется на обработку еще раз, но уже в конец очереди, после ГК)
# Каждый из ГК при вызове генерирует пару сокет-тип_мониторинга и отправляет эту пару на мониторинг в эвент луп (select)
# Если мы сдетектировали что у этого сокета что-то в буфере (он готов) то этот сокет убирается с мониторинга, и попадает в таски (очередь выполнения)
# Во второй раз попав в try ГК выполняет обработку (например сенд), но теперь она проходит без задержки тк мы мониторили что б было что отправлять
# После выполнения обработки ГК докатывается до yield и отсылает в  эвент луп пару сокет-тип_мониторинга. Пара попадает на мониторинг.
# Круг замкнулся
#
# Главная фишка Round Robin эвент лупа состоит в том что мы берем для обработки таски из начала очереди, а добавляем в конец.
# Соответсвенно сокет сначала "инициалиируется" в конце очереди, доходит до начала, выполняется и встает опять в конец.
# Так шаги выполнения равномерно доставются всем
#
###############################################

tasks = deque([])

# Словари для сохранения сокетов которые надо мониторить
# key - socket : value - генератор-обработчик этого сокета
to_read = {}
to_write = {}


def server():
    # Генератор серверного сокета
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 5003))
    server_socket.listen()

    while True:
        # отправляем серверный сокет на мониторинг с пометкой read
        yield ("read", server_socket)
        # После возвращения серверный сокет встает на ожидание подключения и сразу берет из буфера клиентский сокет
        # тк мы до этого сдетектировали что клиент пришел
        client_socket, addr = server_socket.accept()  # read
        print("Connection from", addr)
        # добавляем в таски на обработку клиентский генератор который управляет поведение клиентского сокета
        tasks.append(client(client_socket))


def client(client_socket: socket.socket):
    # Генератор клиентского сокета
    while True:
        # Отправляем на мониторинг клиентский сокет
        yield ("read", client_socket)
        # После возвращения читаем из буфера (тк с детектировали что в буфере что-то есть)
        request = client_socket.recv(4096)  # read
        print(f"Processing of a request: {request}")

        if request:
            response = "Very importamnt response to client\n".encode()
            yield ("write", client_socket)
            client_socket.send(response)  # write
        else:
            break

    client_socket.close()


# Round Robin
def event_loop():
    # крутим пока есть таски которые надо обработать или словари сокетов которые надо поставить на мониторинг
    while any([tasks, to_read, to_write]):
        # Мониторим сокеты и добавляем таски если предыдущие закончились
        while not tasks:
            # мониторим сокеты, получаем списки готовых для записи и чтения
            ready_to_read, ready_to_write, _ = select(to_read, to_write, [])

            # готовые к чтению или записи генераторы сокетов достаем из словаря и кладем в задачи в конец очереди.
            # Эти сокеты больше не мониторятся по такой причине
            # (пока этот сокет в блоке try не обработается и генератор этого сокета не положит новую пару причина-сокет на мониторинг)
            for sock in ready_to_read:
                tasks.append(to_read.pop(sock))

            for sock in ready_to_write:
                tasks.append(to_write.pop(sock))

        # Обрабатываем таски
        try:
            # достаем нулевую задачу
            task = tasks.popleft()
            # В генераторе выполняется обработка
            # после берем новый сокет и для чего (чтения или записи) его надо мониторить
            reason, sock = next(task)  # ('write', client_socket)

            # складываем сокет в списки которые отправятся на мониторинг
            if reason == "read":
                to_read[sock] = task

            if reason == "write":
                to_write[sock] = task

        # Если генератор task кончится (Например клиент оключился)
        except StopIteration:
            print("Done!")


if __name__ == "__main__":
    # Добавляем к задачам серверный сокет
    tasks.append(server())
    event_loop()