import discord
from discord.ext import commands
from utility.common import config


class help_command(commands.HelpCommand):

    def get_command_signature(self, command: commands.Command):
        signature = command.signature
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=0xC9EDBE)
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if command_signatures := [
                self.get_command_signature(c) for c in filtered
            ]:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(
                    command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        embed = discord.Embed(
            title=self.get_command_signature(command), color=0xC9EDBE)
        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            embed.add_field(
                name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    # a helper function to add commands to an embed
    async def send_help_embed(self, title, description, commands: list[commands.Command]):
        embed = discord.Embed(
            title=title, description=description or "No help found...")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                signature = self.get_command_signature(command)
                embed.add_field(
                    name=signature, value=command.help or config.string.zero_width_space)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog: commands.Cog):
        title = cog.qualified_name or "No"
        await self.send_help_embed(f'{title.capitalize()}', cog.description, cog.get_commands())
