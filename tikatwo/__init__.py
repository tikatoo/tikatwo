from twitchio.ext import commands


class TikaBot(commands.Bot):
    def __init__(self, options):
        opt_twitch = options['twitch']
        super().__init__(
            irc_token=opt_twitch['token'],
            client_id=opt_twitch['client_id'],
            nick=opt_twitch['nick'],
            prefix='!',
        )

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')
        await self.join_channels(['tikatoo'])

    async def event_message(self, message):
        print(message.content)
        await self.handle_commands(message)

    # Commands use a different decorator
    @commands.command(name='test')
    async def my_command(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')
