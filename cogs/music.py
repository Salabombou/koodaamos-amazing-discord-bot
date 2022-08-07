from discord.ext import commands
import asyncio
from utility import VoiceChat, music_tools, common
from utility.views.music import music_view
import googleapiclient.discovery
import numpy as np

class music(commands.Cog):
    def __init__(self, bot=None, tokens=None):
        self.bot = bot
        self.youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=tokens[3])
        self.playlist = {}
        self.looping = {}

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    async def play(self, ctx, url='https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau', *args):
        await VoiceChat.join(ctx)
        songs = await music_tools.fetch_songs(self, ctx, url, args)
        music_tools.play_song(self, ctx, songs)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def list(self, ctx):
        embed = music_tools.create_embed(ctx, self.playlist, 0)
        message = await ctx.send(embed=embed)
        ctx = await self.bot.get_context(message)
        await message.edit(view=music_view(music_self=self, ctx=ctx))
        
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def disconnect(self, ctx):
        server = common.get_server(ctx)
        self.playlist[server] = [[],[]]
        await VoiceChat.leave(ctx)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            await VoiceChat.resume(ctx)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            await VoiceChat.pause(ctx)
    
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def skip(self, ctx, amount='1'):
        server = common.get_server(ctx)
        temp = self.looping[server]
        self.looping[server] = False
        amount = abs(int(amount))
        del self.playlist[server][0][1:amount]
        music_tools.append_songs(ctx, self.playlist)
        await VoiceChat.stop(ctx) # skips one song
        await asyncio.sleep(0.5) #why? # just incase
        self.looping[server] = temp
    
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def shuffle(self, ctx):
        server = common.get_server(ctx)
        if self.playlist[server] == [[],[]]: return
        temp = self.playlist[server][0][0]
        self.playlist[server][0].pop(0)
        np.random.shuffle(self.playlist[server][0])
        np.random.shuffle(self.playlist[server][1])
        self.playlist[server][0].insert(0, temp)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def loop(self, ctx):
        server = common.get_server(ctx)
        self.looping[server] = not self.looping[server]
    
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @music_tools.decorators.update_playlist
    async def info(self, ctx, number='0'):
        embed, file = music_tools.create_info_embed(self, ctx, number=number)
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    @common.decorators.delete_after
    async def replay(self, ctx):
        server = common.get_server(ctx)
        self.playlist[server][0].insert(0, self.playlist[server][0][0])
        await VoiceChat.stop(ctx)
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after): # this is safe trust me
        if not member.id == self.bot.user.id:
            return
        elif before.channel == None: # if this is the event, which the bot joins the voice channel
            server = str(after.channel.guild.id)
            voice = after.channel.guild.voice_client
            time = 0
            await asyncio.sleep(5)
            while voice.is_connected():
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 600: # keeps on checking if the bot has been inactive for long periods of time, then leaving
                    self.playlist[server] = [[],[]]
                    await voice.disconnect()
def setup(client, tokens):
    client.add_cog(music(client, tokens))