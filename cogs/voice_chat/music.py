from discord.ext import commands
import asyncio
from utility.common.command import respond
from utility.discord import voice_chat
from utility.tools.music_tools import music_tools
from utility.common import decorators
from utility.views.music import music_view
from utility.views.lyrics import lyrics_view
from utility.cog.command import command_cog
from utility.scraping import Genius
import concurrent.futures

class music(commands.Cog, command_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens,  yt_api_key=tokens['youtube_v3'], loop=bot.loop)
        self.description = 'Plays songs from a playlist to a discord voice channel'
        self.tools = music_tools(bot.loop, tokens['youtube_v3'])
        self.genius = Genius.Genius(access_token=tokens['genius'])

    @commands.command(help='url: YouTube url to a song / playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def play(self, ctx, *, arg='https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau'):
        await voice_chat.join(ctx)
        songs = await self.tools.fetch_songs(ctx, arg)
        await self.tools.play_song(ctx, songs)

    @commands.command(help='url: YouTube url to a song / playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def playnext(self, ctx, *, arg):
        await voice_chat.join(ctx)
        songs = await self.tools.fetch_songs(ctx, arg, True)
        await self.tools.play_song(ctx, songs, True)

    @commands.command(help='lists the bot\'s playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    async def list(self, ctx: commands.Context):
        embed = self.tools.create_embed(ctx, page_num=0)
        message = await respond(ctx, embed=embed)
        await message.edit(view=music_view(music_self=self, ctx=await self.bot.get_context(message)))

    @commands.command(help='disconnects from the voice channel')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    @decorators.Async.get_server
    async def disconnect(self, ctx: commands.Context, /, *, server: str = None):
        self.tools.playlist[server] = [[], []]
        await voice_chat.leave(ctx)

    @commands.command(help='resumes the currently playing song')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def resume(self, ctx: commands.Context):
        if ctx.voice_client.is_paused(): # why is it undefined pycord fix it
            return await voice_chat.resume(ctx)
        await voice_chat.pause(ctx)

    @commands.command(help='pauses the currently playing song')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def pause(self, ctx: commands.Context):
        if ctx.voice_client.is_paused():
            return await voice_chat.resume(ctx)
        await voice_chat.pause(ctx)

    @commands.command(help='skips the currently playing song')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    @decorators.Async.get_server
    async def skip(self, ctx, amount=1, /, *, server: str = None):
        amount = abs(amount)
        if self.tools.looping[server]:
            self.tools.playlist[server][1] += self.tools.playlist[server][0][1:amount][::-1]
        del self.tools.playlist[server][0][1:amount]
        self.tools.append_songs(ctx)
        await voice_chat.resume(ctx)
        await voice_chat.stop(ctx)  # skips one song
        await asyncio.sleep(0.5)

    @commands.command(help='shuffles the playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    @decorators.Async.get_server
    async def shuffle(self, ctx: commands.Context, /, *, server: str = None):
        if self.tools.playlist[server] == [[], []]:
            return
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await self.bot.loop.run_in_executor(
                pool,
                self.tools.shuffle_playlist, server
            )

    @commands.command(help='Loops the currently playing song until stopped')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    @decorators.Async.get_server
    async def loop(self, ctx: commands.Context, /, *, server: str = None):
        self.tools.looping[server] = not self.tools.looping[server]
        await self.tools.looping_response(ctx)

    @commands.command(help='number: number of the song in the playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    @decorators.Async.get_server
    async def info(self, ctx, number=0, /, *, server: str = None):
        if self.tools.playlist[server][0] != []:
            embed = self.tools.create_info_embed(ctx, number=number)
            await respond(ctx, embed=embed, mention_author=False)

    @commands.command(help='replays the current song')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    @decorators.Async.get_server
    async def replay(self, ctx: commands.Context, /, *, server: str = None):
        if self.tools.playlist[server][0] != []:
            self.tools.playlist[server][0].insert(0, self.tools.playlist[server][0][0])
            await voice_chat.stop(ctx)

    @commands.command(help='replies with the lyrics from query')
    @commands.cooldown(1, 60, commands.BucketType.user)
    @decorators.Async.typing
    async def lyrics(self, ctx: commands.Context, *, query: str):
        results = await self.genius.Search(query)
        message = await respond(ctx, content='loading...')
        await message.edit(view=lyrics_view(message, results))
