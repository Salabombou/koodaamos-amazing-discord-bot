import discord
from discord.ext import commands, bridge
from utility.cog.command import command_cog
from utility.common import decorators
from utility.discord import target
from utility.tools import osu_tools
from utility.common import command

class osr2mp4(commands.Cog, command_cog):
    def __init__(self, bot: bridge.Bot, tokens: dict[str, str]) -> None:
        super().__init__(bot=bot, tokens=tokens)
    
    @bridge.bridge_command()
    @commands.cooldown(300, 10, commands.BucketType.user)
    @decorators.Async.defer
    async def osr2mp4(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext):
        replay = await target.get_target(ctx, ext='osr')

        resp = await self.client.get(replay.url)
        resp.raise_for_status()

        video_url = await osu_tools.get_replay(resp.content, ctx.author.name)
        await command.respond(ctx, video_url)