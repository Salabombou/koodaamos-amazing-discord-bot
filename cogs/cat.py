import random
from aiohttp import ClientSession
from discord.ext import commands
import asyncio
import discord
import asyncpraw
import atexit

sessions = []

class cat(commands.Cog):
    def __init__(self, bot, tokens=None):
        self.reddit_id_file = open("./files/id_list", "r+")
        self.reddit_id_file_content = self.reddit_id_file.read().split("\n")
        self.bot = bot
        reddit_api_file = open("./files/reddit_api.api", "r")
        reddit_file_content = reddit_api_file.readlines()

        self.catAPI = tokens[4]
        sessions.append(ClientSession(trust_env=True))

        self.reddit = asyncpraw.Reddit(
            client_id=reddit_file_content[0].strip(),
            client_secret=reddit_file_content[1].strip(),
            requestor_kwargs={"session": sessions[-1]},  # pass Session
            user_agent=reddit_file_content[3].strip()
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
    print(self.reddit_id_file_content)
    
    if hasattr(submission, "is_gallery"):
        gallery = []
        for i in submission.media_metadata.items():
            url = i[1]['p'][0]['u'].split("?")[0].replace("preview", "i") #fuck you reddit # 4 dimensional cluster fuck
            gallery.append(url)
        return gallery[random.randrange(0,len(gallery))]
    return submission.url


def setup(client, tokens):
    client.add_cog(cat(client, tokens))