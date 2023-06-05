from dataclasses import dataclass, field
from typing import Any
import time

@dataclass
class Task:
    coro: Any
    time: float

    dependents: list["Task"] = field(default_factory=list)

    def close(self):
        self.coro.close()
        for d in self.dependents:
            d.coro.close()

    def __await__(self):
        yield self

@dataclass
class AsyncSleep:
    time: float

    def __await__(self):
        yield self

# This will eventually evolve into a data structure that encapsulates an
# event loop. This is global so that coroutines can schedule other tasks via
# asynclib.create_task similar to asyncio. Other features will also require
# direct access to the event loop.
jobs = []

def sleep(delay):
    return AsyncSleep(delay)

def create_task(coro):
    task = Task(coro, time=0)
    jobs.append(task)
    return task

def run(coro, *, wait_for_all=False):
    """

    :param coro:
        The main coroutine to run
    :param wait_for_all:
        If true, the event loop will run until every task has completed,
        even if the main coroutine finishes. The return value of the main
        coroutine is stored and returned at the end.
    :return:
        The return value of 'coro'
    """
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
            if job.dependents:
                jobs.extend(job.dependents)

            if job.coro is not orig:
                continue

            ret = e.value
            if not wait_for_all: # cancel all remaining jobs and return
                for j in jobs:
                    j.close()
                return ret
            continue

        if isinstance(command, AsyncSleep):
            job.time = time.time() + command.time
            jobs.append(job)
            jobs.sort(key=lambda c: c.time)
        elif isinstance(command, Task):
            command.dependents.append(job)
        else:
            raise RuntimeError(f"Coroutine yielded unknown type: {type(command)}")

    return ret