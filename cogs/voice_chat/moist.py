
from discord.ext import commands
import discord
import asyncio
import json
from utility.cog.command import command_cog


class eduko(commands.Cog, command_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)

    async def CreateSpeech(self, text, token):
        payload = {
            "speech": text + '.~',
            "voice": "cr1tikal",
            "pace": 1
        }
        r = await self.client.post(data=json.dumps(payload), headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, url='https://api.uberduck.ai/speak')
        r.raise_for_status()
        uuid = r.json()['uuid']
        url = f'https://uberduck-audio-outputs.s3-us-west-2.amazonaws.com/{uuid}/audio.wav'
        speech = await self.client.head(url)
        while speech.status_code == 403:
            await asyncio.sleep(1)
            speech = await self.client.head(url)
        speech.raise_for_status()
        return url

    @commands.command()
    @commands.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def moist(self, ctx: commands.Context, *, arg="Hi there!"):
        arg = arg.replace('\n', ' ')
        if ctx.message.author.voice == None:
            return
        channel = ctx.message.author.voice.channel
        if ctx.voice_client == None:
            await channel.connect()
        player = ctx.voice_client
        async with ctx.typing():
            wav = await self.CreateSpeech(text=arg, token=self.token)
            wav = discord.FFmpegPCMAudio(wav)
            while player.is_playing():
                await asyncio.sleep(1)
        try:
            await player.play(wav)
        except:
            pass

    @commands.command()
    async def leave(self, ctx: commands.Context):
        await ctx.voice_client.disconnect()
