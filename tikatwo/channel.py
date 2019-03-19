import re
from typing import \
    Any, Awaitable, Callable, List, MutableMapping, Match, NamedTuple, Optional
import twitchio
from .matcher import Pattern
from .modules import MessageHandler, Module, mapping as modules


class _PatternsEntry(NamedTuple):
    matcher: Callable[[twitchio.Message], Any]
    handler: MessageHandler


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
    _patterns: List[_PatternsEntry]

    def __init__(self, config: MutableMapping[str, Any],
                 _nick: str, _channel: twitchio.Channel):
        self._patterns = []

        module_inst: MutableMapping[str, Module] = {}

        for pattern in config['patterns']:
            if 'regex' in pattern:
                matcher = _RegexMatcher(_nick, pattern['regex'])

            modname = pattern['module']
            if modname in module_inst:
                module = module_inst[modname]
            else:
                if 'modules' in pattern and modname in pattern['modules']:
                    modconf = pattern['modules'][modname]
                else:
                    modconf = {}
                module = modules[modname](_channel, modconf)
                module_inst[modname] = module

            self._patterns.append(
                _PatternsEntry(matcher, module.handler(pattern))
            )

    async def handle_message(self, message: twitchio.Message):
        for pattern in self._patterns:
            match = pattern.matcher(message)
            if match:
                await pattern.handler(message, match)
