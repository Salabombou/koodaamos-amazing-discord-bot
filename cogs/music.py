from discord.ext import commands
import asyncio
from utility import VoiceChat, music_tools
from utility.common import decorators
from utility.views.music import music_view
import googleapiclient.discovery
import numpy as np

class music(commands.Cog):
    def __init__(self, bot=None, tokens=None):
        self.description = 'Plays songs from a playlist to a discord voice channel'
        self.bot = bot
        self.youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=tokens[3])
        self.playlist = {}
        self.looping = {}

    @commands.command(help='url: YouTube url to a song / playlist')
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @music_tools.decorators.update_playlist
    @decorators.add_reaction
    async def play(self, ctx, url='https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau', *args):
        if args != ():
            url = url + ' ' + ' '.join(args)
        await VoiceChat.join(ctx)
        songs = await music_tools.fetch_songs(self, ctx, url)
        music_tools.play_song(self, ctx, songs)

    @commands.command(help='lists the bot\'s playlist')
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @music_tools.decorators.update_playlist
    async def list(self, ctx):
        embed = music_tools.create_embed(ctx, self.playlist, 0)
        message = await ctx.send(embed=embed)
        ctx = await self.bot.get_context(message)
        await message.edit(view=music_view(music_self=self, ctx=ctx))
        
    @commands.command(help='disconnects from the voice channel')
    @commands.check(VoiceChat.command_check)
    @decorators.add_reaction
    @decorators.delete_after
    async def disconnect(self, ctx):
        server = music_tools.get_server(ctx)
        self.playlist[server] = [[],[]]
        await VoiceChat.leave(ctx)

    @commands.command(help='resumes the currently playing song')
    @commands.check(VoiceChat.command_check)
    @decorators.add_reaction
    @decorators.delete_after
    async def resume(self, ctx):
        await VoiceChat.resume(ctx)

    @commands.command(help='pauses the currently playing song')
    @commands.check(VoiceChat.command_check)
    @decorators.add_reaction
    @decorators.delete_after
    async def pause(self, ctx):
        await VoiceChat.pause(ctx)
    
    @commands.command(help='skips the currently playing song')
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @decorators.add_reaction
    @decorators.delete_after
    async def skip(self, ctx, amount='1'):
        server = music_tools.get_server(ctx)
        temp = self.looping[server]
        self.looping[server] = False
        amount = abs(int(amount))
        del self.playlist[server][0][1:amount]
        music_tools.append_songs(ctx, self.playlist)
        await VoiceChat.resume(ctx)
        await VoiceChat.stop(ctx) # skips one song
        await asyncio.sleep(0.5) #why? # just incase
        self.looping[server] = temp
    
    @commands.command(help='shuffles the playlist')
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @decorators.add_reaction
    @decorators.delete_after
    async def shuffle(self, ctx):
        server = music_tools.get_server(ctx)
        if self.playlist[server] == [[],[]]: return
        temp = self.playlist[server][0][0]
        self.playlist[server][0].pop(0)
        np.random.shuffle(self.playlist[server][0])
        np.random.shuffle(self.playlist[server][1])
        self.playlist[server][0].insert(0, temp)

    @commands.command(help='Loops the currently playing song until stopped')
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @decorators.add_reaction
    @decorators.delete_after
    async def loop(self, ctx):
        server = music_tools.get_server(ctx)
        self.looping[server] = not self.looping[server]
    
    @commands.command(help='number: number of the song in the playlist')
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @music_tools.decorators.update_playlist
    async def info(self, ctx, number='0'):
        server = music_tools.get_server(ctx)
        if self.playlist[server][0] == []: return
        embed = music_tools.create_info_embed(self, ctx, number=number)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help='replays the current song')
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @decorators.add_reaction
    @decorators.delete_after
    async def replay(self, ctx):
        server = music_tools.get_server(ctx)
        if self.playlist[server][0] != []:
            self.playlist[server][0].insert(0, self.playlist[server][0][0])
            await VoiceChat.stop(ctx)

def setup(client, tokens):
    client.add_cog(music(client, tokens))