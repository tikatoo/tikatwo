from typing import Any, Awaitable, Callable, Optional
import twitchio


MessageHandler = Callable[[twitchio.Message, Any], Awaitable[None]]


class Module:
    options: dict
    channel: twitchio.Channel

    def __init__(self, channel: twitchio.Channel, options: dict):
        self.options = options
        self.channel = channel

    def handler(self, options: dict) -> MessageHandler:
        raise NotImplementedError()
