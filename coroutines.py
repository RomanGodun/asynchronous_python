from time import time
from typing import Generator
from functools import wraps


def classic_generator():
    for _ in range(3):
        yield time()


def coroutine_generator():
    mess_to_outside = "Ready to work"
    message = yield mess_to_outside
    print(f"Корутина напечатала: {message}")
    return "Done"


def init_coroutine(func):
    # инициализируем корутину
    @wraps(func)
    def inner(*args, **kwargs):
        g: Generator = func(*args, **kwargs)
        g.send(None)
        return g

    return inner


class BlaBlaException(Exception):
    pass


@init_coroutine
def average():
    count = 0
    summ = 0
    av = None

    while True:
        try:
            x = yield av
        except StopIteration:
            print("Done")
            break
        except BlaBlaException:
            # Собственное исключение обрабатывает ошибку
            # При необходимости брикаемся из бесконечного цикла. Сделаем это
            break
        else:
            count += 1
            summ += x
            av = round(summ / count, 2)
    # При достижении ретерна (даже неявного) генератор посылает Stopiteration и вместе с ним значение ретерна
    return "Generator done"


def average_wo_init():
    count = 0
    summ = 0
    av = None

    while True:
        try:
            x = yield av
        except StopIteration:
            print("Done")
            break
        except BlaBlaException:
            # Собственное исключение обрабатывает ошибку
            # При необходимости брикаемся из бесконечного цикла. Сделаем это
            break
        else:
            count += 1
            summ += x
            av = round(summ / count, 2)
    # При достижении ретерна (даже неявного) генератор посылает Stopiteration и вместе с ним значение ретерна
    return "Generator done"


@init_coroutine
def delegator(g: Generator):
    av = None
    while True:
        try:
            data = yield av
            # получаем результат иттерации из подгенератора
            av = g.send(data)
        except BlaBlaException as e:
            # если в делегирующий генератор послали исключение BlaBla то его передаем в подгенератор
            try:
                g.throw(e)
            except StopIteration as e:
                # если обработка этого исключения вернула StopIteration
                # то нам надо выйти из бесконечного цикла и вернуть значение ретерна подгенератора
                # в ретерне делегирующего генератора
                ret = e.value
                break
        except StopIteration as e:
            # если в делегирующий генератор послали исключение StopIteration то его передаем в подгенератор
            try:
                g.throw(e)
            except StopIteration as e:
                # если обработка этого исключения вернула еще один StopIteration
                # то нам надо выйти из бесконечного цикла и вернуть значение ретерна подгенератора
                # в ретерне делегирующего генератора
                ret = e.value
                break

    return ret


@init_coroutine
def delegator_light(g: Generator):
    # У меет получать ретерн, прокидывать эксепшены и сэнды  без дополнительного кода
    # Аналогичен делегирующему генератору выше
    ret = yield from g
    return ret


if __name__ == "__main__":
    #########################################
    # Класический генератор
    #########################################

    # Создаем объект генератора cl_g
    cl_g = classic_generator()

    # Крутим его в цикле for
    # for вызывает метод next() в бесконечном цикле и ловит StopIteration
    for t in cl_g:
        print(t)

    #########################################
    # Корутина
    #########################################

    # Создаем объект генератора с приемом данных cl_g
    cr_g = coroutine_generator()

    # "Инициализируем объект генератора"
    print(f"Приняли сообщение из корутины cr_g: {cr_g.send(None)}")

    try:
        # Посылаем данные
        cr_g.send("123123")
    except StopIteration as e:
        # ловим StopIteration тк корутина дойдет до ретерна
        print(f"Приняли через StopIteration значение из return: {e.value}")

    #########################################
    # Генератор с исключениями, ретерном и инициализацией в декораторе
    #########################################

    # Создаем объект генератора считающего средние значения av_g
    # Инициализация не требуется тк у нас есть декоратор
    av_g = average()

    print(f"\nПосылаем данные в av_g - 1, получаем накопленное среднее: {av_g.send(1)}")
    print(f"Посылаем данные в av_g - 10, получаем накопленное среднее: {av_g.send(10)}")
    print(f"Посылаем данные в av_g - 100, получаем накопленное среднее: {av_g.send(100)}")

    # Посылаем собственное исключение в av_g
    try:
        av_g.throw(BlaBlaException)
    except StopIteration as e:
        print(f"Ловим значение ретерн в эксепт: {e.value}")

    #########################################
    # Делегирующий генератор
    #########################################

    # Теперь этот генератор кончился, нужен новый объект генератора
    # Передадим этот объект в объект делегирующего генератора
    d_g = delegator(average())

    print(f"\nПосылаем данные в d_g - 1, получаем накопленное среднее: {d_g.send(1)}")
    print(f"Посылаем данные в d_g - 10, получаем накопленное среднее: {d_g.send(10)}")
    print(f"Посылаем данные в d_g - 100, получаем накопленное среднее: {d_g.send(100)}")

    # Посылаем собственное исключение в d_g
    try:
        d_g.throw(BlaBlaException)
    except StopIteration as e:
        print(f"Ловим значение ретерн в эксепт: {e.value}")

    #########################################
    # Делегирующий генератор через yield from
    #########################################

    # yield from инициализирует подгенераторы поэтому используем генератор без инициализирующего декортаора
    # Передадим этот объект в объект делегирующего генератора
    dl_g = delegator_light(average_wo_init())

    print(f"\nПосылаем данные в dl_g - 1, получаем накопленное среднее: {dl_g.send(1)}")
    print(f"Посылаем данные в dl_g - 10, получаем накопленное среднее: {dl_g.send(10)}")
    print(f"Посылаем данные в dl_g - 100, получаем накопленное среднее: {dl_g.send(100)}")

    # Посылаем собственное исключение в dl_g
    try:
        dl_g.throw(BlaBlaException)
    except StopIteration as e:
        print(f"Ловим значение ретерн в эксепт: {e.value}")
