# asynchronous_python
Репозиторий-справочник по асинхронному подходу и генераторам в python

## Примеры кода:
Папка _async_servers_ - минимальный функционал сервера реализованный разными способами

- _0_synchronous.py_ - синхронный
- _1_simple_el_with_funcs.py_ - постой событийный цикл и две функции. Основан на функции select.select
- _2_callback_async.py_ - асинхронность на колбэках. Основан на классе selectors.DefaultSelector
- _3_round_robin_generators.py_ - асинхронность на каруселе и генераторах
- _4_asyncio.py_ - асинхронный сервер через библиотеку asyncio

</br>
Папка _file_rw_ - скачиваем картинку 10 раз и записываем на диск
</br>
</br>

- _1_sync.py_ - синхронный вариант
- _2_async.py_ - асинхронный вариант 

</br>
Папка _two_endless_gen_ - два бесконечных потока вывода которые принтятся по очереди
</br>
</br>

- _1_round_robin.py_ - асинхронность через карусель
- _2_asyncio_34.py_ - устаревший вариант работы с asyncio
- _3_asyncio.py_ - современный вариант работы с asyncio
