import asynclib

async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asynclib.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f

async def main():
    # Schedule three calls *concurrently*:
    L = await asynclib.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
    )

    return L

async def inner():
    return 42
async def outer():
    x = await inner()
    print(x)
    return x

ret = asynclib.run(main())
print(ret)