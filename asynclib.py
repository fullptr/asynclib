from dataclasses import dataclass, field
from typing import Any
from queue import PriorityQueue
import time

# This will eventually evolve into a data structure that encapsulates an
# event loop. This is global so that coroutines can schedule other tasks via
# asynclib.create_task similar to asyncio. Other features will also require
# direct access to the event loop.
jobs = PriorityQueue()

@dataclass
class Task:
    coro: Any
    time: float

    dependents: list["Task"] = field(default_factory=list)
    return_val: Any = None

    def close(self):
        self.coro.close()
        for d in self.dependents:
            d.coro.close()

    def __lt__(self, other):
        return self.time < other.time

    def __await__(self):
        yield self
        return self.return_val

def create_task(coro):
    task = Task(coro, time=0)
    jobs.put(task)
    return task

@dataclass
class EventSleep:
    time: float

    def __await__(self):
        yield self

def sleep(delay):
    return EventSleep(delay)

async def gather(*coros):
    gather_jobs = [create_task(c) for c in coros]
    return [await j for j in gather_jobs]

def run(coro):
    """
    :param coro:
        The main coroutine to run
    :return:
        The return value of 'coro'
    """
    jobs.put(Task(coro, time=0))

    while not jobs.empty():
        job = jobs.get()
        time.sleep(max(0.0, job.time - time.time()))

        try:
            command = job.coro.send(None)
        except StopIteration as e:
            job.return_val = e.value
            for dep in job.dependents:
                jobs.put(dep)

            # If this is the main job, cancel all remaining jobs and return
            if job.coro is coro:
                while not jobs.empty():
                    jobs.get().close()
                return job.return_val

            continue

        if isinstance(command, EventSleep):
            job.time = time.time() + command.time
            jobs.put(job)
        elif isinstance(command, Task):
            command.dependents.append(job)
        else:
            raise RuntimeError(f"Coroutine yielded unknown type: {type(command)}")