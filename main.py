import asynclib

async def delayed_print(msg, delay):
    await asynclib.sleep(delay)
    print(msg)


async def main():
    t1 = asynclib.create_task(delayed_print("world", 2))
    t2 = asynclib.create_task(delayed_print("Hello", 1))
    await t1
    await t2
    print("Done")


asynclib.run(main())