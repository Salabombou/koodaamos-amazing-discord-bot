
# Koodaamo's Amazing Discord Bot
  

## What is it?

A discord bot written python using [Pycord](https://github.com/Pycord-Development/pycord).

Commands range from web scraping to ffmpeg video editing

## Supported Python versions

- 3.10

  

## Running the bot

- Clone the repository to your local machine

- Create a virtual enviroment named (optionally) .venv in python with `py -m venv .venv`

- Activate the virtual enviroment with `.venv\Scripts\activate`

- Install the needed packages with `py -m pip install -r requirements.txt`

- Before starting the bot, add the needed api tokens to the [tokens.json](./tokens.json)

- Start the bot with `py bot.py`

  

# Documentation

## Cogs
Cogs are a way to manage command in Pycord api. Each cog is a class object with the command(s) inside.

## [Ffmpeg](./cogs/ffmpeg/)
Commands utilizing ffmpeg

##### [Green](./cogs/ffmpeg/video/green.py)
Puts a greenscreen YouTube video on top of an image or a video
##### [Audio](./cogs/ffmpeg/audio/audio.py)
Adds audio from YouTube video on top of an image or video
##### [Flanger](./cogs/ffmpeg/audio/flanger.py)
Adds to video's audio or to an audio file a vibrato effect
##### [Nightcore](./cogs/ffmpeg/audio/nightcore.py)
Makes the video and its audio faster and more high pitched
##### [Bait](./cogs/ffmpeg/video/bait.py)
Makes an prank video from YouTube to play after the image or the first frame of the video
##### [Reverse](./cogs/ffmpeg/video/reverse.py)
Reverses the video and the audio
##### [Ruin](./cogs/ffmpeg/video/ruin.py)
Ruins the video and the audio completely by making its bitrate very small
##### [Mute](./cogs/ffmpeg/audio/mute.py)
Silences the video
##### [Earrape](./cogs/ffmpeg/audio/reverse.py)
Ruins the audio in the video by making it very loud

### [Fun](./cogs/fun/)
Fun commands to play around with

##### [Gpt3](./cogs/fun/gpt3.py)
An AI chatbot that responds to different questions and tasks
##### [Dalle](./cogs/fun/eduko.py)
Creates a 3x3 collage from AI generated images from a prompt

## [Tools](./cogs/tools/)

##### [Eduko](./cogs/tools/eduko.py)
Scrapes the Eduko's menu from Eduko's website

##### [Sauce](./cogs/tools/sauce.py)
Finds the sauce (origin) from an image

#### [Download](./cogs/tools/download.py)
Downloads a video, image or audio from multiple sources

Supported sites:
- Youtube
- Reddit
- TikTok
- Spotify

TBA:
- Twitter
- Twitch (clips)

#### [Owner](./cogs/tools/owner.py)
Bot owner only commands

## [Music](./cogs/voice_chat/music.py)
Music bot that joins the voice channel and plays music from playlist

There are multiple different commands to manage the music bot

#### [Play](./cogs/voice_chat/music.py)
Starts the music bot and adds the song(s) to the playlist

#### [Playnext](./cogs/voice_chat/music.py)
Same as play, except inserts the songs to the playlist so that they are to be played next

#### [list](./cogs/voice_chat/music.py)
Lists the songs in the playlist with controls to control it

#### [disconnect](./cogs/voice_chat/music.py)
Leaves the voice channel and empties the playlist

#### [Pause/Resume](./cogs/voice_chat/music.py)
Pauses / resumes the currently playing song

#### [Skip](./cogs/voice_chat/music.py)
Skips n amount of songs in the playlist. default is 1

#### [Shuffle](./cogs/voice_chat/music.py)
Shuffles the playlist

#### [Loop](./cogs/voice_chat/music.py)
Enables / disables looping of the playlist

#### [Info](./cogs/voice_chat/music.py)
Gets the info from the selected song from the playlist. Defaults to currently playing song

#### [Replay](./cogs/voice_chat/music.py)
Replays the currently playing song

#### [Lyrics](./cogs/voice_chat/music.py)
Gets the song lyrics from search

## [Utility](./utility/)
Utility contains different scripts used by different commands

### [Ffmpeg](./utility/ffmpeg.py)
Contains tools to create videos with ffmpeg

### [Ffprobe](./utility/ffprobe.py)
Contains tools to get info about different files with ffprobe

### [Logging](./utility/logging.py)
Logging related config


## [Common](./utility/common/)

### [Command](./utility/common/command.py)

### [Convert](./utility/common/convert.py)

### [Decorators](./utility/common/decorators.py)

### [Config](./utility/common/config.py)

### [Errors](./utility/common/errors.py)

### [File Management](./utility/common/file_management.py)

### [Requests](./utility/common/requests.py)

## [Discord](./utility/discord/)

### [Check](./utility/discord/check.py)

### [Help](./utility/discord/help.py)

### [Listeners](./utility/discord/listeners.py)

### [Target](./utility/discord/target.py)

### [Voice Chat](./utility/discord/voice_chat.py)

### [Webhook](./utility/discord/webhook.py)

## [Scraping](./utility/scraping/)

### [Compress](./utility/scraping/compress.py)

### [Download](./utility/scraping/download.py)

### [Genius](./utility/scraping/Genius.py)

### [Pomf](./utility/scraping/pomf.py)

### [Reddit](./utility/scraping/Reddit.py)

### [Spotify](./utility/scraping/Spotify.py)

### [TikTok](./utility/scraping/TikTok.py)

### [YouTube](./utility/scraping/YouTube.py)

## [Tools](./utility/tools/)

### [Music Tools](./utility/tools/music_tools.py)

### [Sauce Tools](./utility/tools/sauce_tools.py)

## [Views](./utility/views/)

### [Music](./utility/views/music.py)

### [Sauce](./utility/views/sauce.py)
