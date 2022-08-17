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
    async def cat(self, ctx):
        random.seed(a=None, version=2)

        resp = None
        async with ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search", headers={'x-api-key': str(self.catAPI)} ) as resp:
                resp = await resp.json()
        url = resp[0]["url"]
        print(url)
        if ".false" in url or random.randrange(32,33) == 32:
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
    random.seed(a=None, version=2)
    i = random.randrange(0,11)
    print(i)
    subreddit = await self.reddit.subreddit("eroonigiri")
    async for submission in subreddit.hot(limit=20): # use random to get a random post # will fix later 
        if not submission.stickied and not submission.is_self:
            if not i: 
                print(submission.id)
                if hasattr(submission, "is_gallery"):
                    gallery = []
                    for i in submission.media_metadata.items():
                        url = i[1]['p'][0]['u'].split("?")[0].replace("preview", "i") #fuck you reddit # 4 dimensional cluster fuck
                        gallery.append(url)
                    return gallery[random.randrange(0,len(gallery))]
                return submission.url
            else:
                i -= 1

def setup(client, tokens):
    client.add_cog(cat(client, tokens))