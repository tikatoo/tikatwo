import json

from . import TikaBot


with open('options.json', 'r') as rf:
    options = json.load(rf)

bot = TikaBot(options)
bot.run()
