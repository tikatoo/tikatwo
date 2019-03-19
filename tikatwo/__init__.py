from pathlib import Path
from typing import Any, List, MutableMapping, NamedTuple, Optional
import aiosqlite
import toml
import twitchio
from twitchio.ext import commands

from .channel import Channel


class _ChannelInfo(NamedTuple):
    name: str
    config: MutableMapping[str, Any]


class TikaBot(commands.Bot):
    _channelinfo: Optional[List[_ChannelInfo]]
    _channels: MutableMapping[str, Channel]

    def __init__(self, confpath: Path):
        with (confpath / 'connection.toml').open() as rf:
            connection = toml.load(rf)

        con_twitch = connection['twitch']
        super().__init__(
            irc_token=con_twitch['token'],
            client_id=con_twitch['client_id'],
            nick=con_twitch['nick'],
            prefix='!',
        )

        channels = confpath / 'channels'
        if not channels.is_dir():
            raise OSError(f"Expected directory at {channels!r}")

        self._channelinfo = []
        self._channels = {}
        for chanpath in channels.iterdir():
            channame = chanpath.stem
            if chanpath.is_file() and chanpath.suffix == '.toml':
                with chanpath.open() as rf:
                    chanconf = toml.load(rf)
            else:
                raise OSError(f"Expected TOML file at {chanpath!r}")

            self._channelinfo.append(
                _ChannelInfo(channame, chanconf)
            )
            self._channels[channame] = Channel(
                chanconf, self.nick,
                self.get_channel(channame)
            )

    async def event_ready(self):
        for info in self._channelinfo:
            await self.join_channels((info.name,))
            self._channels[info.name] = Channel(
                info.config, self.nick, self.get_channel(info.name)
            )
        print(f'Ready | {self.nick}')

    async def event_message(self, message: twitchio.Message):
        print('[MSG]', message.author.name + ':', message.content)
        if message.author.name != self.nick:
            await self._channels[message.channel.name].handle_message(message)
        await self.handle_commands(message)
