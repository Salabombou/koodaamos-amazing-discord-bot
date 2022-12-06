from discord.ext import commands
import asyncio
from utility.common.command import respond
from utility.discord import voice_chat
from utility.tools.music_tools import music_tools
from utility.common import decorators
from utility.views.music import list_view
from utility.views.lyrics import lyrics_view
from utility.cog.command import command_cog
from utility.scraping import Genius
from utility.views.music import song_view

class music(commands.Cog, command_cog):
    """
        Music bot that joins the voice channel and plays music from playlist
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str]):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Plays songs from a playlist to a discord voice channel'
        self.tools = music_tools(bot, bot.loop, tokens['youtube_v3'])
        self.genius = Genius.Genius(access_token=tokens['genius'])

    @commands.command(help='url: YouTube url to a song / playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def play(self, ctx: commands.Context, *, arg='https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau'):
        """
            Starts the music bot and adds the songs to the playlist
        """
        voice_client = await voice_chat.join(ctx)
        if voice_client != None:
            self.tools.voice_client.update({ctx.guild.id: voice_client})
        songs = await self.tools.fetch_songs(ctx, arg)
        await self.tools.play_song(ctx, songs)

    @commands.command(help='url: YouTube url to a song / playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def playnext(self, ctx: commands.Context, *, arg):
        """
            Same as play, except inserts the songs to the playlist so that they are to be played next
        """
        voice_client = await voice_chat.join(ctx)
        if voice_client != None:
            self.tools.voice_client.update({ctx.guild.id: voice_client})
        songs = await self.tools.fetch_songs(ctx, arg)
        await self.tools.play_song(ctx, songs, playnext=True)

    @commands.command(help='lists the bot\'s playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    async def list(self, ctx: commands.Context):
        """
            Lists the songs in the playlist with controls to control it
        """
        embed = self.tools.create_embed(ctx, page_num=0)
        message = await respond(ctx, embed=embed)
        await message.edit(view=list_view(music_self=self, ctx=await self.bot.get_context(message)))

    @commands.command(help='disconnects from the voice channel', aliases=['leave'])
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def disconnect(self, ctx: commands.Context):
        """
            Leaves the voice channel and empties the playlist
        """
        self.tools.playlist[ctx.guild.id] = [[], []]
        await voice_chat.leave(ctx)
        

    @commands.command(help='pauses / resumes the currently playing song', aliases=['resume', 'stop'])
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def pause(self, ctx: commands.Context):
        """
            Pauses / resumes the currently playing song
        """
        if ctx.voice_client.is_paused():
            return voice_chat.resume(ctx)
        is_playing = ctx.voice_client.is_playing() and not ctx.guild.me.voice.afk
        if self.tools.playlist[ctx.guild.id][0] != [] and not is_playing:
            return await self.tools.play_song(ctx)
        voice_chat.pause(ctx)

    @commands.command(help='skips the currently playing song')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def skip(self, ctx, amount=1):
        """
            Skips n amount of songs in the playlist. default is 1
        """
        amount = abs(amount)
        if self.tools.looping[ctx.guild.id]:
            self.tools.playlist[ctx.guild.id][1] += self.tools.playlist[ctx.guild.id][0][1:amount][::-1]
        del self.tools.playlist[ctx.guild.id][0][1:amount]
        self.tools.append_songs(ctx)
        voice_chat.resume(ctx)
        voice_chat.stop(ctx)  # skips one song
        await asyncio.sleep(0.5)

    @commands.command(help='shuffles the playlist')
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def shuffle(self, ctx: commands.Context):
        """
            Shuffles the playlist
        """
        if self.tools.playlist[ctx.guild.id] == [[], []]:
            return
        self.tools.shuffle_playlist(ctx.guild.id)

    @commands.command(help='Loops the currently playing song until stopped')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def loop(self, ctx: commands.Context):
        """
            Enables / disables looping of the playlist
        """
        self.tools.looping[ctx.guild.id] = not self.tools.looping[ctx.guild.id]
        await self.tools.looping_response(ctx)

    @commands.command(help='number: number of the song in the playlist')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.update_playlist
    async def song(self, ctx: commands.Context, number=0):
        """
            Gets the info from the selected song from the playlist. Defaults to currently playing song
        """
        if self.tools.playlist[ctx.guild.id][0] == []:
            return
        embed, view = await self.tools.create_info_embed(ctx, number=number)
        await respond(ctx, embed=embed, view=view, mention_author=False)

    @commands.command(help='replays the current song')
    @commands.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def replay(self, ctx: commands.Context):
        """
            Replays the currently playing song
        """
        if self.tools.playlist[ctx.guild.id][0] == []:
            return
        self.tools.playlist[ctx.guild.id][0].insert(0, self.tools.playlist[ctx.guild.id][0][0])
        voice_chat.stop(ctx)

    @commands.command(help='replies with the lyrics from query')
    @commands.cooldown(1, 60, commands.BucketType.user)
    @decorators.Async.typing
    async def lyrics(self, ctx: commands.Context, *, query: str):
        """
            Gets the song lyrics from search
        """
        results = await self.genius.Search(query)
        message = await respond(ctx, content='loading...')
        await message.edit(view=lyrics_view(message, results))
