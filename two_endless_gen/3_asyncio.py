import asyncio

###############################################
# Асинхронность на современной версии asyncio
###############################################


async def gen1():
    # бесконечная генерация чисел
    i = -1
    while True:
        i += 1
        print(i)
        await asyncio.sleep(1)


async def gen2():
    # бесконечная генерация букв "a", "b", "c"
    abc = ["a", "b", "c"]
    i = -1
    while True:
        i += 1
        print(abc[i % 3])
        await asyncio.sleep(1)


async def main():
    task1 = asyncio.create_task(gen1())
    task2 = asyncio.create_task(gen2())
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    asyncio.run(main())
