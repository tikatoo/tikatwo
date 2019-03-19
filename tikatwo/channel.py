import functools
import re
from typing import \
    Any, Awaitable, Callable, List, MutableMapping, Match, NamedTuple, Optional
import twitchio
from .matcher import Pattern
from .modules import MessageHandler, Module, mapping as modules


class _PatternsEntry(NamedTuple):
    matcher: Callable[[twitchio.Message], Any]
    handlers: List[MessageHandler]


class _RegexMatcher:
    class _UserFetch:
        def __init__(self, me: str):
            self.me = self[me]

        def __getitem__(self, key: str) -> str:
            return f"(?:@?{key})"

    def __init__(self, nick: str, re_src: str, flags=re.RegexFlag.IGNORECASE):
        self._re = re.compile(self._preprocess(re_src, nick), flags=flags)

    def _preprocess(self, re_src, nick: str):
        return re_src.format(
            u=self._UserFetch(nick)
        )

    def __call__(self, msg: twitchio.Message) -> Optional[Match]:
        return self._re.search(msg.content)


class Channel:
    _channel: twitchio.Channel
    _patterns: List[_PatternsEntry]
    modules: MutableMapping[str, Module]

    def __init__(self, config: MutableMapping[str, Any],
                 _nick: str, _channel: twitchio.Channel):
        self._channel = _channel
        self._patterns = []

        self.modules = {}

        for pattern in config['patterns']:
            if 'regex' in pattern:
                matcher = _RegexMatcher(_nick, pattern['regex'])

            handlers: List[MessageHandler] = []
            if 'modules' in pattern:
                for modname in pattern['modules']:
                    if modname in self.modules:
                        module = self.modules[modname]
                    else:
                        if 'modules' in config and modname in config['modules']:
                            modconf = config['modules'][modname]
                        else:
                            modconf = {}
                        module = modules[modname](_channel, modconf)
                        self.modules[modname] = module

                    handlers.append(module.handler(pattern))
            
            response = (
                ('@{m.author.name}, ' + pattern['reply'])
                if 'reply' in pattern
                else pattern['response']
                if 'response' in pattern
                else None
            )

            if response is not None:
                handlers.append(functools.partial(
                    self.handle_respond, response
                ))
            
            if handlers:
                self._patterns.append(_PatternsEntry(
                    matcher, handlers
                ))

    async def handle_message(self, message: twitchio.Message):
        for pattern in self._patterns:
            match = pattern.matcher(message)
            if match:
                for handler in pattern.handlers:
                    await handler(message, match)

    async def handle_respond(self, response: str,
                             message: twitchio.Message, match):
        await self._channel.send(response.format(
            m=message, a=match,
            **self.modules
        ))
