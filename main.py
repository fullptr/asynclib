import asynclib

async def delayed_hello(delay):
    await asynclib.sleep(delay)
    print(f"Hello! {delay=}")

async def main():
    t1 = asynclib.create_task(delayed_hello(1))
    t2 = asynclib.create_task(delayed_hello(2))
    await t1
    await t2
    return 9000

import time
start = time.time()
val = asynclib.run(main())
print(f"Ended with {val=}: took {time.time() -start:.1f} seconds")