
from discord.ext import commands
import discord
import openai
import asyncio
import httpx
import json
import io
    
class moist(commands.Cog):
    def __init__(self, bot, tokens):
        self.bot = bot
        self.token = tokens[2]
        self.client = httpx.AsyncClient(timeout=30)

    async def CreateSpeech(self, text, token):
        payload = {
            "speech": text + '.~',
            "voice": "cr1tikal",
            "pace": 1
            }
        r = await self.client.post(data=json.dumps(payload), headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}" }, url='https://api.uberduck.ai/speak')
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
    async def moist(self, ctx, *, arg="Hi there!"):
        arg = arg.replace('\n', ' ')
        if ctx.message.author.bot:
            return
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
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

def setup(client, tokens):
    client.add_cog(moist(client, tokens))