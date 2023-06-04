import asynclib

async def delayed_hello(delay):
    await asynclib.sleep(delay)
    print(f"Hello! {delay=}")

async def main():
    for i in range(10):
        asynclib.create_task(delayed_hello(i))
    return 9000

val = asynclib.run(main(), wait_for_all=True)
print(f"End of script: return value = {val}")