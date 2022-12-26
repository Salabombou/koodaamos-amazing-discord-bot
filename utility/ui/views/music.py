import discord
from discord import NotFound, Interaction
from utility.discord import voice_chat
from utility.tools import music_tools
from discord.ext import bridge
import math
import asyncio
from utility.scraping import YouTube


class list_view(discord.ui.View):
    """
        View for the music bot playlist
    """
    def __init__(self, music_self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext):
        super().__init__(timeout=None)
        self.tools: music_tools.music_tools = music_self.tools
        self.bot: bridge.Bot = music_self.bot
        self.embed = None
        self.index = 0
        self.server = ctx.guild.id
        self.ctx = ctx
        self.update_buttons()
    
    async def interaction_check(self, interaction) -> bool:
        """
            Checks if the user can execute these commands
        """
        if await self.bot.is_owner(interaction.user):
            return True
        if interaction.user.bot:
            return False  # if the user is bot
        if interaction.user.voice == None:
            return False  # if the user is not in the same voice chat
        if interaction.message.author.voice == None:
            return False  # if the bot is not currently in a voice channel
        if interaction.user.voice.channel == interaction.message.author.voice.channel:
            return True  # if the bot and the user are in the same voice channel
        return False

    def update_buttons(self):  # holy fuck
        """
            Updates the buttons accordingly
        """
        self.children[0].options = self.tools.create_options(self.ctx)
        playlist_length = math.ceil(len(self.tools.playlist[self.server][0]) / 50)

        for child in self.children:
            child.disabled = False

        if self.index == 0:  # no more to go back
            self.children[1].disabled = True  # super back
            self.children[2].disabled = True  # back
        if self.index >= playlist_length - 1:  # no more to forward
            self.children[4].disabled = True  # for
            self.children[5].disabled = True  # super for
        if self.tools.playlist[self.server][0] == []:  # if the entire list is empty
            for child in self.children:
                child.disabled = True
            self.children[3].disabled = False  # refresh
            self.index = 0

    def update_embed(self):
        """
            Updates the list embed to match the playlist
        """
        for _ in range(0, self.index + 1):
            self.embed = self.tools.create_embed(self.ctx, self.index)
            if self.embed.description != '':
                break
            self.index -= 1

    @discord.ui.select(placeholder='Choose page...', min_values=0, row=0)
    async def select_callback(self, select: discord.ui.Select, interaction: Interaction):
        """
            Select the page
        """
        value = int(select.values[0])
        self.index = value
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='FIRST PAGE', emoji='⏪', style=discord.ButtonStyle.red, row=1, disabled=True)
    async def super_backward_callback(self, button, interaction: Interaction):
        """
            Move back to the first page
        """
        self.index = 0
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='PREVIOUS PAGE', emoji='◀️', style=discord.ButtonStyle.red, row=1, disabled=True)
    async def backward_callback(self, button, interaction: Interaction):
        """
            Go back one page
        """
        self.index -= 1
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='REFRESH', emoji='🔄', style=discord.ButtonStyle.red, row=1)
    async def refresh_callback(self, button, interaction: Interaction):
        """
            Refresh the list
        """
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='NEXT PAGE', emoji='▶️', style=discord.ButtonStyle.red, row=1)
    async def forward_callback(self, button, interaction: Interaction):
        """
            Go forward one page
        """
        self.index += 1
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LAST PAGE', emoji='⏩', style=discord.ButtonStyle.red, row=1)
    async def super_forward_callback(self, button, interaction: Interaction):
        """
            Go to the last page
        """
        self.index = math.ceil(len(self.tools.playlist[self.server][0]) / 50) - 1
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SKIP', emoji='⏭️', style=discord.ButtonStyle.red, row=2)
    async def skip_callback(self, button, interaction: Interaction):
        """
            Skips the currently playing song
        """
        voice_chat.resume(self.ctx)
        voice_chat.stop(self.ctx)
        await asyncio.sleep(0.5)
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SHUFFLE', emoji='🔀', style=discord.ButtonStyle.red, row=2)
    async def shuffle_callback(self, button, interaction: Interaction):
        """
            Shuffles the playlist
        """
        if self.tools.playlist[self.server][0] == []:
            return
        self.tools.shuffle_playlist(self.ctx.guild.id)
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LOOP', emoji='🔁', style=discord.ButtonStyle.red, row=2)
    async def loop_callback(self, button, interaction: Interaction):
        """
            Enable / disable looping
        """
        self.tools.looping[self.server] = not self.tools.looping[self.server]
        await interaction.response.edit_message(view=self)
        await self.tools.looping_response(self.ctx)

    @discord.ui.button(label='PAUSE/RESUME', emoji='⏯️', style=discord.ButtonStyle.red, row=2)
    async def pauseresume_callback(self, button, interaction: Interaction):
        """
            Pause / resume playing
        """
        vc = self.tools.voice_client[self.server]
        if not vc.is_connected():
            return
        
        await interaction.response.edit_message(view=self)
        
        if vc.is_paused():
            return voice_chat.resume(self.ctx)
        elif self.tools.playlist[self.server] != [] and not vc.is_playing():
            return await self.tools.play_song(self.ctx)
        voice_chat.pause(self.ctx)


class song_view(discord.ui.View):
    def __init__(self, song: YouTube.Video):
        super().__init__(timeout=None)
        
        song_link = discord.ui.Button( # link to the video itself
            label='Video',
            style=discord.ButtonStyle.link,
            url=f'https://www.youtube.com/watch?v={song.id}'
        )
        channel_link = discord.ui.Button( # link to the video creator's channel
            label='Channel',
            style=discord.ButtonStyle.link,
            url=f'https://www.youtube.com/channel/{song.channel_id}'
        )
        
        self.add_item(song_link)
        self.add_item(channel_link)
        