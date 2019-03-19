from os import walk
from pathlib import Path

from . import TikaBot


confpath = Path('tikabot.conf')
if not confpath.is_dir():
    if confpath.exists():
        raise OSError(f"Configuration path {confpath!r} is not a directory")
    else:
        raise OSError(f"Configuration path {confpath!r} does not exist")
connpath = confpath / 'connection.toml'
if not connpath.is_file():
    raise OSError(f"Expected a file at {connpath!r}")

bot = TikaBot(confpath)
bot.run()
