import asyncio

###############################################
# Асинхронность на старой версии asyncio
###############################################


@asyncio.coroutine
def gen1():
    # бесконечная генерация чисел
    i = -1
    while True:
        i += 1
        print(i)
        yield from asyncio.sleep(1)


@asyncio.coroutine
def gen2():
    # бесконечная генерация букв "a", "b", "c"
    abc = ["a", "b", "c"]
    i = -1
    while True:
        i += 1
        print(abc[i % 3])
        yield from asyncio.sleep(1)


@asyncio.coroutine
def main():
    task1 = asyncio.ensure_future(gen1())
    task2 = asyncio.ensure_future(gen2())
    yield from asyncio.gather(task1, task2)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
