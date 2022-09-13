import discord
from utility.common.errors import TargetNotFound
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

async def get_file(embeds, attachments, no_aud, no_vid, no_img): # gets the file for the img if there is one
    for attachment in attachments:
        if attachment.content_type != None:
            content_type = attachment.content_type[0:5]
            not_allowed = (content_type == 'audio' and no_aud) or (content_type == 'video' and no_vid) or (content_type == 'image' and no_img)
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
        file = await get_file(embeds, attachments, no_aud, no_vid, no_img)
        if file == None:
            raise TargetNotFound()
        return file
    else: # if there are embeds or attachments in the command itself
        embeds = ctx.message.embeds
        attachments = ctx.message.attachments
        file = await get_file([], attachments, no_aud, no_vid, no_img)
    if file == None:
        for message in history[1:]:
            embeds = message.embeds
            attachments = message.attachments
            file = await get_file(embeds, attachments, no_aud, no_vid, no_img)
            if file != None:
                break
    return file