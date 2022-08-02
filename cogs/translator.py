from discord.ext import commands
from aiohttp import ClientSession
from discord import Webhook
import asyncio
import discord
import deepl
import tweepy

class translator(commands.Cog):
    def __init__(self, bot, tokens=None):
        self.bearertoken = tokens[4]
        self.bot = bot
        self.client = tweepy.Client(self.bearertoken)
        self.translator  = deepl.Translator(tokens[6])

    @commands.command()
    async def usage(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        usage = self.translator.get_usage()
        if usage.character.limit_exceeded:
            sent_message = await ctx.send("Character limit exceeded.")
        else:
            sent_message = await ctx.send(f"Character usage: {usage.character}")
        await sent_message.delete(delay=30)


    @commands.command()
    async def tr(self, ctx, content = None, delete = True):
        self.client
        if (delete):
            try:
                await ctx.message.delete()
            except Exception:
                pass
        reference = None
        user = None
        usage = self.translator.get_usage()
        if (usage.character.limit_exceeded):
            await ctx.send("Character limit exceeded.", delete_after=30)
            return
        if ctx.message.reference != None:
            msg_id = ctx.message.reference.message_id
            message = await ctx.fetch_message(msg_id)
            content = message.content
            reference = message
        if "https://twitter.com" in content:
            #content = content.split("/status/",1)[1].split("?",1)[0]
            #test = client.get_tweet(content)
            #content = str(test[0])[:-24]
            content = content.split("/status/",1)
            tweet_id = content[1].split("?",1)[0]
            #user = client.get_user(id=tweet_id,expansions="author_id")

            tweet = self.client.get_tweet(id=tweet_id,expansions=["author_id","attachments.media_keys"],media_fields=["preview_image_url","url"],user_fields=["profile_image_url"]) # why is this not working? where is the tweet url? 
            headers = {"Authorization": "Bearer " + self.bearertoken}
            tweet_url = None
            async with ClientSession() as session:
                async with session.get("https://api.twitter.com/2/tweets/"+ str(tweet_id) +"?expansions=author_id%2Cattachments.media_keys&media.fields=media_key%2Curl&user.fields=profile_image_url%2Curl",headers=headers) as resp:
                    tweet_url = await resp.json()
            #print(tweet_url) #prepare for wall of text
            url = []
            if "media" in tweet_url["includes"]:
                for image in tweet_url["includes"]["media"]:
                    if image["type"] == "photo":
                        url.append(image["url"])

            user_icon_url = tweet_url["includes"]["users"][0]["profile_image_url"]
            user_url = tweet_url["includes"]["users"][0]["url"]
            user = tweet[1]["users"][0] # optimize this later

            content = str(tweet[0]).split("https://t.co/")[0]
            if content != None and len(content) < 2000 and content != "":
                await translate(self, ctx, content, user, reference, url, tweet_id, user_icon_url, user_url) #it is a mess but it works
                return
        try:
            if content != None and len(content) < 2000 and content != "":
                await translate(self, ctx, content, user, reference)
        except deepl.DeepLException:
            print("shit")


async def translate(self, ctx, content, user, reference, url = None, id = None, user_icon_url = None, user_url = None,):
    result = self.translator.translate_text(content, target_lang="EN-US")
    result = str(result).replace("@", "@​") # lets not be annoying # warning: there is a zero width space
    if user != None:
        if url != None:
            embed = discord.Embed(description=result, color=0x006eff,url=str("https://twitter.com/i/web/status/" + str(id)))
            embed.set_author(name=str(str(user["name"]) + "(@" + str(user["username"]) + ")"), icon_url=str(user_icon_url),url=user_url)
            embed.set_footer(text="Translated by DeepL")
            embeds = [embed]
            i = 0
            for url in url: # making multiple embeds with same url so that we can have multiple images # dont ask how this works
                if i > 3: # max 4 images because discord doesn't like more 
                    break
                embed = discord.Embed(url=str("https://twitter.com/i/web/status/" + str(id))) 
                embed.set_image(url=url)
                embeds.append(embed) 
                i += 1

            async with ClientSession() as session:
                if (ctx.message.channel.id == 773148428275941386):  
                    pass 
                    webhook = Webhook.from_url('https://discord.com/api/webhooks/965641540275937300/t5gOZeFGv5YEFgQVl4_XQoMjnWgHs_KCKOZLH8Z50BAoDhQlf7t6KjpTXBaRJgSGImVV', session=session)
                elif (ctx.message.channel.id == 798462155585224737):
                    pass
                    webhook = Webhook.from_url('https://discord.com/api/webhooks/965631589239365632/WOPJyugAKLI-OhCL_XTCKow9Gxb553eDgN_-0gSy9lfYsCu4H8oqaMrtgWEecJRrLR_4', session=session)
                else:
                    print("well shit") 
                    return 
                
                #koodaamo
                #test server
                await webhook.send(embeds=embeds)
            return
        else:
            embed=discord.Embed(description=result, color=0x006eff, url=str("https://twitter.com/i/web/status/" + str(id)))
            embed.set_author(name=str(str(user["name"]) + "(@" + str(user["username"]) + ")"), icon_url=user_icon_url, url=user_url)
            embed.set_footer(text="Translated by DeepL")
    else:
        print("user is none")
        embed=discord.Embed(description=result, color=0x006eff)
    if reference == None:    
        await ctx.send(embed=embed)
    else:
        await reference.reply(embed=embed)

def setup(client, tokens):
    client.add_cog(translator(client, tokens))