from discord.ext import commands, bridge
from utility.cog.command import command_cog
from utility.common import decorators, config, command
from utility.common.errors import McSrvStatusError
from urllib.parse import quote
import discord
from dataclasses import dataclass
import base64
import io

class mcsrvstat(commands.Cog, command_cog):
    """ 
        Gets the info about a minecraft server
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.url = lambda address: 'https://api.mcsrvstat.us/2/' + quote(address)
    
    @dataclass(frozen=True)
    class __mc_server_info:        
        ip: str
        port: int
        title: str
        description: str
        players: list[dict[str]]
        players_online: int
        max_players: int
        version: str
        online: bool
        icon: bytes
    
    @staticmethod
    def __icon_to_bytes(icon: str) -> bytes:
        icon = icon.split(',')[1]
        icon = icon.encode()
        icon = base64.decodebytes(icon)
        return icon
    
    def __parse_data(self, data: dict) -> __mc_server_info:
        online = data['online']
        if not online:
            raise McSrvStatusError()
        if 'uuid' not in data['players']:
            players = None
        else:
            players: dict = data['players']['uuid']
            players = [
                {
                    'name': name,
                    'uuid': uuid
                }
                for name, uuid in players.items()
            ]
        clean: list[str] = data['motd']['clean']
        parsed_data = {
            'ip': data['ip'],
            'port': data['port'],
            'title': clean[0],
            'description': clean[1] if len(clean) > 1 else '',
            'players': players or [],
            'players_online': data['players']['online'],
            'max_players': data['players']['max'],
            'version': data['version'],
            'online': data['online'],
            'icon': self.__icon_to_bytes(data['icon']) if 'icon' in data else None
        }
        return self.__mc_server_info(**parsed_data)
    
    def __create_embed(self, server: __mc_server_info):
        players = '\n'.join(
            [
                f"[{player['name']}](https://minecraftuuid.com/?search={quote(player['uuid'])})"
                for player in server.players[:8]
            ]
        )
        players = players if server.players != [] else f'{server.players_online}/{server.max_players}'
        embed = discord.Embed(
            color=config.embed.color,
            title=server.title,
            description=server.description
        )
        embed.set_thumbnail(url='attachment://icon.png')
        embed.add_field(name='Address', value=f'{server.ip}:{server.port}', inline=False)
        embed.add_field(name='Online', value=str(server.online))
        embed.add_field(name='Version', value=server.version)
        embed.add_field(name='Players', value=players)
        return embed
    
    @bridge.bridge_command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.defer
    async def mc(self, ctx: bridge.BridgeContext, address: str = '147.135.191.71:25582'):
        """
        
        """
        url = self.url(address)
        resp = await self.client.get(url)
        resp.raise_for_status()
        server = self.__parse_data(resp.json())
        embed = self.__create_embed(server)
        file = discord.File(fp=io.BytesIO(server.icon), filename='icon.png')
        await command.respond(ctx, file=file, embed=embed)