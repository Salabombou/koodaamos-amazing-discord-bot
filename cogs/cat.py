import random
from utility.cog.command import command_cog
from aiohttp import ClientSession
from discord.ext import commands
import asyncio
import discord
import asyncpraw
import atexit

sessions = []

class cat(commands.Cog,command_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.reddit_id_file = open("./files/id_list", "r+")
        self.reddit_id_file_content = self.reddit_id_file.read().split("\n")
        self.bot = bot

        self.catAPI =  tokens['cat']
        sessions.append(ClientSession(trust_env=True))

        self.reddit = asyncpraw.Reddit(
            client_id=tokens['reddit_id'],
            client_secret=tokens['reddit_secret'],
            requestor_kwargs={"session": sessions[-1]},  # pass Session
            user_agent=tokens['reddit_agent']
        )
    
    @commands.command()
    @commands.is_nsfw()
    async def cat(self, ctx, *args):
        random.seed(a=None, version=2)

        resp = None
        async with ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search", headers={'x-api-key': str(self.catAPI)}) as resp:
                resp = await resp.json()
        url = resp[0]["url"]
        if ".false" in url or random.randrange(0,101) == 32 or "-f" in args:
            url = await getSecretCatUrl(self) #add easter egg here
        await ctx.send(url)
    
    def exit_handler():
        loop = asyncio.new_event_loop()
        loop.run_until_complete(async_exit_handler())
        loop.close()
    atexit.register(exit_handler)

async def async_exit_handler():
    for session in sessions:
        await session.close()
    print("\nClient closed")

async def getSecretCatUrl(self):
    subreddit = await self.reddit.subreddit("eroonigiri")
    submission = await subreddit.random()
    while submission.stickied or submission.is_self or submission.id in self.reddit_id_file_content:
        submission = await subreddit.random()
        print("fuck")
    self.reddit_id_file_content.append(submission.id)
    open("./files/id_list", "a").write(str(submission.id) + "\n")
    
    if hasattr(submission, "is_gallery"):
        gallery = []
        for i in submission.media_metadata.items():
            url = i[1]['p'][0]['u'].split("?")[0].replace("preview", "i") #fuck you reddit # 4 dimensional cluster fuck
            gallery.append(url)
        return gallery[random.randrange(0,len(gallery))]
    return submission.url


def setup(client, tokens):
    client.add_cog(cat(client, tokens))