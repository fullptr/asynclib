import asynclib

async def waiter(event):
    print('waiting for it ...')
    await event.wait()
    print('... got it!')

async def main():
    # Create an Event object.
    event = asynclib.Event()

    # Spawn a Task to wait until 'event' is set.
    waiter_task = asynclib.create_task(waiter(event))

    # Sleep for 1 second and set the event.
    await asynclib.sleep(1)
    event.set()

    # Wait until the waiter task is finished.
    await waiter_task

asynclib.run(main())