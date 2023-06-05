from dataclasses import dataclass, field
from typing import Any
from queue import PriorityQueue
import time

@dataclass
class Loop:
    """
    Holds all the global state for the running event loop. In the future,
    support multiple event loops.
    """
    jobs: PriorityQueue = field(default_factory=PriorityQueue)

loop = Loop()

def get_running_loop():
    global loop
    return loop

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

@dataclass
class Event:
    flag: bool = False
    waiters: list[Task] = field(default_factory=list)

    def __await__(self):
        if not self.flag:
            yield self
        return True

    async def wait(self):
        await self

    def set(self):
        self.flag = True
        for waiter in self.waiters:
            loop.jobs.put(waiter)
        self.waiters = []

    def clear(self):
        self.flag = False

    def is_set(self):
        return self.flag

def create_task(coro):
    task = Task(coro, time=0)
    loop.jobs.put(task)
    return task

@dataclass
class Sleep:
    time: float

    def __await__(self):
        yield self

def sleep(delay):
    return Sleep(delay)

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
    loop.jobs.put(Task(coro, time=0))

    while not loop.jobs.empty():
        job = loop.jobs.get()
        time.sleep(max(0.0, job.time - time.time()))

        try:
            command = job.coro.send(None)
        except StopIteration as e:
            job.return_val = e.value
            for dep in job.dependents:
                loop.jobs.put(dep)

            # If this is the main job, cancel all remaining jobs and return
            if job.coro is coro:
                while not loop.jobs.empty():
                    loop.jobs.get().close()
                return job.return_val

            continue

        if isinstance(command, Sleep):
            job.time = time.time() + command.time
            loop.jobs.put(job)
        elif isinstance(command, Task):
            command.dependents.append(job)
        elif isinstance(command, Event):
            command.waiters.append(job)
        else:
            raise RuntimeError(f"Coroutine yielded unknown type: {type(command)}")