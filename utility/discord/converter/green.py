from discord.ext import commands, bridge

class Color(commands.Converter):
    @staticmethod
    async def convert(
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        color: str
    ) -> str:
        color = color.lower()
        color = color.lstrip('#')
        color = color[:6].zfill(6)  # fills with zeros if missing values
        try:
            int(color, 16)
        except ValueError:
            color = '00ff00' # defaults to green if it fails
        return color