from discord.ext import commands
import asyncio

async def GetTime(time):
    strNum = time[:-1]
    try:
        num = int(strNum)
    except:
        num = 1
    match time[-1]:
        case 's':
            pass
        case 'm':
            num = num * 60
        case 'h':
            num = num * 3600
        case _:
            pass
    if num == 0:
        num = 1
    return num

class spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def spam(self, ctx, victim=f"@everyone", time="1s"):
        num = await GetTime(time)
        server = ctx.message.guild
        spammer = ctx.message.author
        try:
            mention = ctx.message.mentions[0].id
        except:
            mention = 0
        try:
            if server.id in spamming:
                if spammer.id in spamming[server.id]:
                    if spamming[server.id][spammer.id] == True:
                        return
                elif not isinstance(spamming[server.id], {}):
                    spamming[server.id] = {}
            else:
                spamming[server.id] = {}
        except:
            pass
        spamming[server.id][spammer.id] = True
        spamming[server.id]["instance"] = [spammer.id, mention]
        while spamming[server.id][spammer.id]:
            await ctx.send(content=victim, delete_after=num)
            await asyncio.sleep(num)

    @commands.command()
    async def stop(self, ctx):
        author = ctx.message.author
        server = ctx.message.guild
        spammer = spamming[server.id]["instance"][0]
        victim = spamming[server.id]["instance"][1]
        if author.id == victim or author.id == spammer or victim == 0:
            spamming[server.id][spammer] = False
            spamming[server.id]["instance"] = None
            await ctx.reply("Stopping!", delete_after=3)
        return

def setup(client, tokens):
    global spamming
    global victim
    spamming = {}
    victim = {}
    client.add_cog(spam(client))