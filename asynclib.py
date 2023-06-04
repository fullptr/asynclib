from dataclasses import dataclass
from typing import Any
import time

@dataclass
class Task:
    coro: Any
    time: float

@dataclass
class AsyncSleep:
    time: float

    def __await__(self):
        yield self

jobs = []

def sleep(delay):
    return AsyncSleep(delay)

def create_task(coro):
    jobs.append(Task(coro, time=0))

def run(coro, *, wait_for_all=False):
    global jobs

    if jobs:
        raise RuntimeError("Already running an event loop")

    ret = None
    orig = coro

    jobs = [Task(coro, time=0)]
    jobs.sort(key=lambda co: co.time)

    while jobs:
        job = jobs.pop(0)
        time.sleep(max(0.0, job.time - time.time()))

        try:
            command = job.coro.send(None)
        except StopIteration as e:
            if job.coro is not orig:
                continue

            ret = e.value
            if not wait_for_all: # cancel all remaining jobs and return
                for j in jobs:
                    j.coro.close()
                return ret

        if isinstance(command, AsyncSleep):
            job.time = time.time() + command.time
            jobs.append(job)
            jobs.sort(key=lambda c: c.time)
        else:
            raise RuntimeError(f"Coroutine yielded unknown type: {type(command)}")

    return ret