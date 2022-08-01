
from discord.ext import commands
import discord
import openai
import asyncio
import httpx
import json
import io

async def CreateSpeech(text):
    payload = {
        'character': 'GLaDOS',
        'emotion': 'Contextual',
        'text': text
    }
    async with httpx.AsyncClient(timeout=30) as requests:
        r = await requests.post(data=json.dumps(payload), headers={'Content-Type': 'application/json;charset=utf-8'}, url='https://api.15.ai/app/getAudioFile5')
        r.raise_for_status()
        wav_name = r.json()['wavNames'][0]
        speech = await requests.get(f'https://cdn.15.ai/audio/{wav_name}')
    r.raise_for_status()
    buf = io.BytesIO(speech.content)
    buf.seek(0)
    return buf
    
class tts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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