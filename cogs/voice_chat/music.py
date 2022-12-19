from discord.ext import commands, bridge, pages
import asyncio
from utility.discord import voice_chat
from utility.tools.music_tools import music_tools
from utility.tools import lyrics_tools
from utility.common import decorators, config
from utility.ui.views.music import list_view
from utility.ui.views.lyrics import lyrics_view
from utility.cog.command import command_cog
from utility.scraping import Genius
import discord


class music(commands.Cog, command_cog):
    """
        Music bot that joins the voice channel and plays music from playlist
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str]):
        super().__init__(bot=bot, tokens=tokens)
        self.tools = music_tools(bot, bot.loop, tokens['youtube_v3'])
        self.genius = Genius.Genius(access_token=tokens['genius'])

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def play(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        *,
        song: discord.Option(
            str,
            'YouTube url to a song or playlist'
        ) = 'https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau'
    ) -> None:
        """
            Starts the music bot and adds the songs to the playlist
        """
        voice_client = await voice_chat.join(ctx)
        if voice_client:
            self.tools.voice_client.update({ctx.guild.id: voice_client})
        songs = await self.tools.fetch_songs(ctx, song)
        await self.tools.play_song(ctx, songs)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def playnext(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        *,
        song: discord.Option(
            str,
            'YouTube url to a song or playlist'
        )
    ) -> None:
        """
            Same as play, except inserts the songs to the playlist so that they are to be played next
        """
        voice_client = await voice_chat.join(ctx)
        if voice_client != None:
            self.tools.voice_client.update({ctx.guild.id: voice_client})
        songs = await self.tools.fetch_songs(ctx, song)
        await self.tools.play_song(ctx, songs, playnext=True)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    async def list(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Lists the songs in the playlist with controls to control it
        """
        embed = self.tools.create_embed(ctx, page_num=0)
        message = await ctx.respond(embed=embed)
        await message.edit(view=list_view(music_self=self, ctx=await self.bot.get_context(message)))

    @bridge.bridge_command(aliases=['leave'])
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.defer
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def disconnect(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Leaves the voice channel and empties the playlist
        """
        self.tools.playlist[ctx.guild.id] = [[], []]
        await voice_chat.leave(ctx)
        

    @bridge.bridge_command(aliases=['resume', 'stop'])
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.defer
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def pause(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Pauses / resumes the currently playing song
        """
        if ctx.voice_client.is_paused():
            return voice_chat.resume(ctx)
        is_playing = ctx.voice_client.is_playing() and not ctx.guild.me.voice.afk
        if self.tools.playlist[ctx.guild.id][0] != [] and not is_playing:
            return await self.tools.play_song(ctx)
        voice_chat.pause(ctx)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def skip(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        amount: discord.Option(
            int,
            'The amount of songs to skip from the playlist'
        ) = 1
    ) -> None:
        """
            Skips n amount of songs from the playlist. Default is 1
        """
        amount = abs(amount)
        if self.tools.looping[ctx.guild.id]:
            self.tools.playlist[ctx.guild.id][1] += self.tools.playlist[ctx.guild.id][0][1:amount][::-1]
        del self.tools.playlist[ctx.guild.id][0][1:amount]
        self.tools.append_songs(ctx)
        voice_chat.resume(ctx)
        voice_chat.stop(ctx)  # skips one song
        await asyncio.sleep(0.5)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.check(voice_chat.command_check)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def shuffle(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Shuffles the playlist
        """
        if self.tools.playlist[ctx.guild.id] == [[], []]:
            return
        self.tools.shuffle_playlist(ctx.guild.id)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def loop(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Enables / disables looping of the playlist
        """
        self.tools.looping[ctx.guild.id] = not self.tools.looping[ctx.guild.id]
        await self.tools.looping_response(ctx)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    async def song(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        number: discord.Option(
            int,
            'The song number in the playlist'
        ) = 0
    ) -> None:
        """
            Gets the info from the selected song from the playlist. Defaults to currently playing song
        """
        if self.tools.playlist[ctx.guild.id][0] == []:
            return
        embed, view = await self.tools.create_info_embed(ctx, number=number)
        await ctx.respond(embed=embed, view=view, mention_author=False)

    @bridge.bridge_command()
    @bridge.guild_only()
    @commands.check(voice_chat.command_check)
    @decorators.Async.defer
    @decorators.Async.update_playlist
    @decorators.Async.add_reaction
    @decorators.Async.delete_after
    async def replay(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Replays the currently playing song
        """
        if self.tools.playlist[ctx.guild.id][0] == []:
            return
        self.tools.playlist[ctx.guild.id][0].insert(0, self.tools.playlist[ctx.guild.id][0][0])
        voice_chat.stop(ctx)

    @bridge.bridge_command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def lyrics(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        *,
        query: discord.Option(
            str,
            'The search query for the song to get the lyrics from'
        )
    ) -> None:
        """
            Gets the song lyrics from search
        """
        results = await self.genius.Search(query)
        embeds = [lyrics_tools.create_embed(song_result) for song_result in results.song_results]
        paginator = pages.Paginator(
            pages=embeds,
            disable_on_timeout=True,
            loop_pages=True,
        )
        await paginator.respond(ctx, paginator)