import itertools
import functools
from typing import List, MutableMapping
import twitchio
from .module import MessageHandler, Module


class Counter(Module):
    counters: MutableMapping[str, int]

    def __init__(self, channel: twitchio.Channel, options: dict):
        super().__init__(channel, options)
        self.counters = {}

    def __getitem__(self, name):
        return self.counters[name]

    def handler(self, options: dict) -> MessageHandler:
        incrs: List[str] = []
        decrs: List[str] = []
        if 'incr' in options:
            incrs = options['incr']
            if isinstance(incrs, str):
                incrs = [incrs]
        if 'decr' in options:
            decrs = options['decr']
            if isinstance(decrs, str):
                decrs = [decrs]

        for counter in itertools.chain(incrs, decrs):
            if counter not in self.counters:
                self.counters[counter] = 0

        return functools.partial(self.count, incrs, decrs)

    async def count(self, incrs: List[str], decrs: List[str],
                    message: twitchio.Message, match):
        for counter in incrs:
            self.counters[counter] += 1
        for counter in decrs:
            self.counters[counter] -= 1
