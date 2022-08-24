
from discord.ext import commands
import discord
import openai
import asyncio
import httpx
import json
import io

    
class tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=30)

    async def CreateSpeech(self, text):
        payload = {
            'character': 'GLaDOS',
            'emotion': 'Contextual',
            'text': text
        }
        resp = await self.client.post(data=json.dumps(payload), headers={'Content-Type': 'application/json;charset=utf-8'}, url='https://api.15.ai/app/getAudioFile5')
        resp.raise_for_status()
        wav_name = resp.json()['wavNames'][0]
        speech = await self.client.get(f'https://cdn.15.ai/audio/{wav_name}')
        resp.raise_for_status()
        buf = io.BytesIO(speech.content)
        buf.seek(0)
        return buf
    @commands.command(aliases=['15'])
    @commands.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tts(self, ctx, *, arg="Hi there!"):
        if ctx.message.author.bot:
            return 
        async with ctx.typing():
            wav = await CreateSpeech(text=arg)
        file = discord.File(fp=wav, filename="unknown.wav")
        await ctx.reply(file=file, mention_author=False)

def setup(client, tokens):
    client.add_cog(tts(client))