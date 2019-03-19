from functools import partial
import twitchio
from .module import MessageHandler, Module


class CallResponse(Module):
    def handler(self, options: dict) -> MessageHandler:
        if 'reply' in options:
            return partial(self.respond, "@{m.author.name} " + options['reply'])
        else:
            return partial(self.respond, options['response'])


    async def respond(self, response: str, message: twitchio.Message, match):
        await self.channel.send(response.format(m=message, a=match))
