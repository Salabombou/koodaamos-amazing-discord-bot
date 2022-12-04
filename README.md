
  

  

# Koodaamo's Amazing Discord Bot

  

  

## What is it?

  

  

A discord bot written python using [Pycord](https://github.com/Pycord-Development/pycord).

  

  

Commands range from web scraping to ffmpeg video editing

  

  

## Supported Python versions

  

  

- 3.10
- 3.11
  

  

  

## Running the bot

  

  

- Clone the repository to your local machine

  

  

- Create a virtual enviroment named (optionally) .venv in python with `py -m venv .venv`

  

  

- Activate the virtual enviroment with `.venv\Scripts\activate`

  

  

- Install the needed packages with `py -m pip install -r requirements.txt`


- Insatll ffmpeg for the ffmpeg commands


  

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

Common tools to be used by multiple different apps

  

### [Command](./utility/common/command.py)

`async def respond(ctx, /, *, mention_author=False, **kwargs)`

Responds safely to the command

  

### [Convert](./utility/common/convert.py)

Contains functions to be used for conversion

  

`class timedelta`

static class to be used to organize the functions

  

functions:

`def to_seconds(delta_time)`

Converts timedelta to seconds.

Returns a float.

  

### [Decorators](./utility/common/decorators.py)

Contains the decorators to be used by the application

  

### [Config](./utility/common/config.py)

Contains global values for the bot such as the default embed color, max message length and unicode characters

  

File contains static classes with variables in them

  

`class embed`

Contains the default embed variables to be used by the bot

  

variables:

* `color` The color the embeds should be in
  

### [Errors](./utility/common/errors.py)

Contains the bot's custom exceptions.

Exception classes:
* `class CommandTimeout(Exception)` External command timed out
* `class SauceNotFound(Exception)` No sauce were found for the image
* `class SongNotFound(Exception)` No songs found in the play
* `class UrlInvalid(Exception)` Given url is malformed
* `class VideoUnavailable(Exception)` Video is not available for download
* `class VideoTooLong(Exception)` Video's duration exceeds the maximum allowed duration
* `class UnsupportedUrl(Exception)` Url is not supported by the application
* `class DownloadFailure(Exception)` File download failed
* `class TargetNotFound(Exception)` Target file could not be found
* `class FfmpegError(Exception)` Ffmpeg command did not complete successfully
* `class FfprobeError(Exception)` Ffprobe command did not complete successfully
* `class VideoSearchNotFound(Exception)` Could not find any videos with the said query
* `class PomfUploadFail(Exception)` Uploading the file to pomf failed
* `class TargetError(Exception)` Target is invalid in some way
* `class UrlRedirectError(Exception)` Url redirected too many times
* `class NaughtyError(Exception)` User is listed in the naughty list
* `class GeniusSongsNotFound(Exception)` No songs were found from Genius with a query
* `class PlaylistEmpty(Exception)` Playlist does not have any songs
* `class LyricsTooLong(Exception)` Lyrics are over the allowed message length
* `class YoutubeApiError(Exception)` YouTube api did not respond correctly
* `class GeniusApiError(Exception)` Genius api did not respond correctly


### [File Management](./utility/common/file_management.py)

`async def get_bytes(file)`

Converts the file either from url or path to bytes

returns the bytearray of the file

  

`async def prepare_file(ctx, file, ext)`

Prepares the file to be sent by the bot.

returns the sendable file class object and a string that might contain a direct download link to the file it was uploaded, if needed

  

### [Requests](./utility/common/requests.py)

`async def get_redirect_url(url):`

Gets the redirect url from url.

Returns the final url

  

## [Discord](./utility/discord/)

  

  

### [Check](./utility/discord/check.py)

Contains the discord command checking functions

  

`class command_checker`

Contains the default command checker for the bot

  

`async def check(ctx)`

The default command checker for bot.

  

### [Help](./utility/discord/help.py)

Contains the default help command class used by the bot

  

`class help_command`

The default help command class

  

### [Listeners](./utility/discord/listeners.py)

Listeners used by the bot

  

`class Listeners`

The class that contains the listeners

  

`async def on_command_error(ctx, error)`

When a normal command raises an exception

  

`async def on_application_command_error(ctx, error)`

When an application command raises an exception

  

`async def on_ready()`

Once the bot is ready to receive commands

### [Target](./utility/discord/target.py)

Contains the function to get the target file from discord chat

  

`class Target(FfprobeFormat)`

Class used to store the relevant info about the target file

  

`async def Target.probe()`

Probes the selected target with ffprobe to get additional information about the file

  

`async def get_target(ctx, no_aud=False, no_vid=False, no_img=False`

Gets the target with the approved types

On exception, raises either TargetError or TargetNotFound

  

### [Voice Chat](./utility/discord/voice_chat.py)

Contains the functions to be used by the bot for voice chat management

  

`def command_check(ctx)`

Command checker for voice chat commands

  

Returs boolean True if success, else False

  

`async def join(ctx)`

Joins the same voice chat the user is in

  

`async def leave(ctx)`

Leaves the voice channel

  

`def stop(ctx)`

Stops the bot from playing sound in the voice chat

  

`def resume(ctx)`

Resumes the bot to playing sound

  

`def pause(ctx)`

Pauses the bot of playing sound

  

### [Webhook](./utility/discord/webhook.py)

Webhook handler for the bot's webhooks

  

`async def send_message(ctx, /, *, embeds, files=None)`

Send a message using the bot's webhook

If webhook doesnt exist, creates one.

  

## [Scraping](./utility/scraping/)

Contains the webscraping related tools

  

### [Compress](./utility/scraping/compress.py)

Used to compress files using [8mb.video](https://8mb.video/)

  

`async def video(file, server_level, ext)`

Compresses the video.

  

Returns the bytearray of the compressed video

  

### [Download](./utility/scraping/download.py)

Contains the centered way to download files from the scrapers the bot uses just from the url itself.

  

`async def from_url(url)`

Gets the raw url to the file to be downloaded

  

Raises UnsupportedUrl if the url is not supported by the application

  

### [Genius](./utility/scraping/Genius.py)

Genius scraper for song lyrics

`class GeniusSearchResults`

Class object to store the Genius search results

  

variables:

* `json` The json response of the search
* `song_results` All the parsed results as a list of new SongResult classes
* `best_song_result` The first index of `song_results`


`class GeniusSearchResult.SongResult`

The class to stores invidual song results

  

variables:

* `api_path`
* `artist_names`
* `title`
* `full_title`
* `id`
* `language`
* `lyrics_owner_id`
* `lyrics_state`
* `path`
* `release_date`
* `url`
* `thumbnail`
* `artist_icon`
* `other`
* `lyrics`

  

### [Pomf](./utility/scraping/pomf.py)

Pomf scraper for remote file hosting

  

`async def upload(file, ext)`

Uploads the file to pomf.cat to be hosted from

  

Returns the url to the uploaded file

  

### [Reddit](./utility/scraping/Reddit.py)

Reddit download website scraper

  

`async def get_raw_url(url)`

Gets the direct download url for the Reddit file

  

### [Spotify](./utility/scraping/Spotify.py)

Spotify music download website scraper

  

`async def get_raw_url(url)`

Gets the direct download url for the Spotify song

  

### [TikTok](./utility/scraping/TikTok.py)

Tiktok video download website scraper

  

`async def get_raw_url(url)`

Gets the direct download url for the TikTok

  

### [YouTube](./utility/scraping/YouTube.py)

Youtube scraper using the YouTube's api and third parties

  

`class VideoDummie`

A dummie versio of the Video class used as a placeholder

  

`Video`

A class containing the info about the YouTube video

  

variables:

* `title` Video's title
* `description` Video's description
* `channelId` Video's Uploader's channel's ID
* `channelTitle` Video's Uploader's channel's Title
* `videoId` ID of the video
* `thumbnail` Url to the video's thumbnail
 

`def _parse_data(data, videoId, from_playlist)`

Parses the data from the api's response json

Returns new Video class
  

`class YT_Extractor`

Extractor for extracting data from YouTube

  

variables:

 * `loop` Event loop
* `youtube` YouTube api libary's instance
* `channel_icons` Contains the already fetched channel icons for memoization
* `client` Httpx AsyncClient for requests


`async def get_raw_url(url, video, max_duration)`

Gets the raw url to a YouTube video

  

`async def get_info(url, id, video, max_duration)`

Gets the info from the YouTube video

  

`def __get_resuls(ytInitialData)`

Internal private method used to parse the javascript variable

  

`def __get_initial_data(content)`

Internal private method.

Gets the javascript variable from the YouTube search results document and parses it using json.loads module

  

`async def fetch_from_search(query)`

Gets the Youtube video from search.

  

Using websraping instead of YouTube's official api because it is very costly, about few hundered times more than normal video fetch

  

returns new Video class

  

`async def fetch_from_video(videoId)`

Fetches the data from YouTube video

  

returns new Video class

  

`async def fetch_from_playlist(playlistId)`

Fetches the data from YouTube playlist

  

returns a list of new Video classes

  

`async def fetch_channel_icon(channelId)`

Fetches the channel's icon

  

return the url for the channel's icon

  
  
  

`async def get_raw_url(url)`

Gets the best possible quality direct download url of the YouTube video's url

  

returns the direct download url

  

## [Tools](./utility/tools/)

Tools some cogs need

  

### [Music Tools](./utility/tools/music_tools.py)

Contains the music bot's management used tools

  

`class music_tools`

The class that the music bot uses containing all the functions to manage the music bot

  

`def append_song(ctx, /, playnext=False, songs=[])`

Appends the songs to the playlist and moves the playlist from right to left

  

`def serialize_songs(ID)`

creates the embed decription text used to list playlist's contents

  

`def create_embed(ctx, page_num)`

Creates the embed for the selected page

  

`def create_options(ctx)`

Creates the Select options used by the bot in the dropdown menu in the music bot's view class

  

`async def create_info_embed(ctx, number=0, song=None)`

Creates the info embed for currently playing song or a specific song using a number

  

`async def fetch_songs(ctx, url, no_playlists=False)`

Fetches the song(s) from either video, playlist or a search query

  

Raises UrlInvalid if the url is malformed

  

`def shuffle_playlist(ID)`

Shuffles the playlist using numpy

  

`async def send_song_unavailable(ctx, next_song)`

Sends a message about the song being unavailable, and runs the play_song once again with the next song

  

`async def play_song(ctx, songs=[], playnext=False, next_song=False)`

Song player handler

  

`def next_song(ctx, message)`

Function to be called after the bot stops playing music.

Runs the play_song again for the next song in the playlist

  

`async def looping_response(ctx)`

Responds if the music bot is currently looping or not

  

### [Sauce Tools](./utility/tools/sauce_tools.py)

Contains the sauce cog's used tools

  

`class parsed_result`

Class used to parse the html document of the sauce

  

class variables:

* `content` Info about the image
* `similarity` How similar the result image is to the actual image
* `title` Title of the result image
* `image` Url to the image
 

`def create_embed(res, url, hidden)`

Creates the embed for the result from the document

  

## [Views](./utility/views/)

Contains the files and in them the discord view classes used for buttons and dropdown menus in discord's chat

### [Lyrics](./utility/views/lyrics.py)

Contains the view class used for the lyrics command's lyrics selector

`class lyrics_view(discord.ui.View)`

  

variables:

* `index` list index
* `embeds` all the embeds for the results
* `results` all the results
* `loop` Running event loop
* `message Response message

The command response message

  

`async def on_timeout()`

Run after certain amount of inactivity for the view

  

Removes the view from the message

  

`async def create_embeds(song_results)`

Creates the embeds for the lyrics

  

returns a list of embeds

  

`def update index()`

Updates the index of the embeds

  

`async def backward_callback(button, interaction)`

Go backwards in the embeds

  

`async def forward_callback(button, interaction)`

Go forward in the embeds

  

`async def select_lyrics_callback(select, interaction)`

Select the song to fetch the lyrics from.

  

Deletes itself from the message after it has responded

  

### [Music](./utility/views/music.py)

Contains the view class used for the music bot's management

  

`class music_view(discord.ui.View)`

View for the music bot playlist

  

`async def interaction_check(interaction)`

Checks if the user can execute these commands

  

returns boolean True if successful, else False

  

`def update_buttons()`

Updates the buttons accordingly

  

`def update_embed()`

Updates the list embed to match the playlist

  

`async def select_callback(select, interaction)`

Select the page from the list

  

`async def super_backward_callback(button, interaction)`

Moves to the first page

  

`async def backward_callback(button, interaction)`

  

`async def refresh_callback(button, interaction)`

Refershes the list

  

`async def forward_callback(button, interaction)`

Go forward one page

  

`async def super_forward_callback(button, interaction)`

Go to the last page

  

`async def skip_callback(button, interaction)`

Skips the currently playing song

  

`async def shuffle_callback(button, interaction)`

Shuffles the playlist

  

`async def loop_callback(button, interaction)`

Enable / disable looping

  

`async def pauseresume_callback(button, interaction)`

Pause / resume playing

  

### [Sauce](./utility/views/sauce.py)

Contains the view class used to scroll through sauce command's results

  

`class sauce_view(discord.ui.View)`

The sauce view

  

variables:

* `embeds` Embeds for every result
* `index` The embed index
* `message` The command response message
* `loop` Running event loop


`async def on_timeout()`

Run after certain amount of inactivity for the view

  

Removes the view from the message

  

`def update_index()`

Updates the index of the playlist

  

`async def backward_callback(button, interaction)`

Go backwards in the embeds

  

`async def forward_callback(button, interaction)`

Go forwards in the embeds
