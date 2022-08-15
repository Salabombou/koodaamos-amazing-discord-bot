import discord

# THE ORDER FOR THE FILES
# 1.   Attachments
# 2.   Embeds
#   a. Video
#   b. Thumbnail
#   c. Image

# THE ORDER WHERE TO LOOK FOR FILES
# 1. From the replied message
# 2. From the command message itself
# 3. From the channel history

async def GetFile(embeds, attachments, no_aud, no_vid, no_img): # gets the file for the img if there is one
    for attachment in attachments:
        if attachment.content_type != None:
            not_allowed = ("audio" in attachment.content_type and no_aud) or ("video" in attachment.content_type and no_vid) or ("image" in attachment.content_type and no_img)
            if not_allowed:
                continue
            return attachment
    for embed in embeds:
        if isinstance(embed,discord.embeds.Embed):
            if isinstance(embed.video.proxy_url, str) and not no_vid:
                return embed.video
            if isinstance(embed.image.proxy_url, str) and not no_img:
                return embed.image
            if isinstance(embed.thumbnail.proxy_url, str) and not no_img:
                return embed.thumbnail
    return None

# Overlay a greenscreen video on top of the target.
async def get_target(ctx, no_aud=False, no_vid=False, no_img=False):
    history =  await ctx.channel.history(limit=50).flatten()
    file = None

    if ctx.message.reference != None: # if its a reply 
        reply = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        embeds = reply.embeds
        attachments = reply.attachments
        file = await GetFile(embeds, attachments, no_aud, no_vid, no_img=False)
        if file == None:
            raise Exception("No images/videos in the reply or video or audio is not accepted")
        return file
    else: # if there are embeds or attachments in the command itself
        embeds = ctx.message.embeds
        attachments = ctx.message.attachments
        file = await GetFile([], attachments, no_aud, no_vid, no_img=False)
    if file == None:
        for message in history[1:]:
            embeds = message.embeds
            attachments = message.attachments
            file = await GetFile(embeds, attachments, no_aud, no_vid, no_img=False)
            if file != None:
                break
    return file
