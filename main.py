import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
from random import choice
from image_cog import image_cog
from aiohttp import request
import praw
import random

# s3t a reddir settings
reddit = praw.Reddit(client_id = '-Ml7Dqld2x4DjPSZ6khiJg',
                    client_secret = 'HGzUCyS_8FD9p-Ns4W2XS409c5rdtw',
                    username = 'cartiroman',
                    password = 'Dadefo95',
                    user_agent = 'carti')

youtube_dl.utils.bug_reports_message = lambda: ''


# set a youtube settings
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

# set a ffmpeg settings
ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# Create a class for Youtbe 
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# set a commands which need to start a message
client = commands.Bot(command_prefix='/')

client.add_cog(image_cog(client))

status = ['Listening Playboi Carti', 'Eating!', 'watching you!']


# kick function(kick users from server)
@client.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)


# ban function(ban user from server)
@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)


# finction(which meen that bot ready to use)
@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

# function which print Welcome text when the user join tp the server
@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `?help` command for details!')

# when user type <?hello> send a random text from responses
@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['Why did you wake me up? 🧛', 'Wasup homie', 'Hello 👋, how are you?', 'Hi', '**Wasssuup!**']
    await ctx.send(choice(responses))

# meme fucntion (send a ransom mem to the server)
@client.command()
async def meme(ctx):
    subreddit = reddit.subreddit("memes")
    all_subs = []

    top = subreddit.top(limit = 50)

    for submission in top:
        all_subs.append(submission)

    random_sub = random.choice(all_subs)

    name = random_sub.title
    url = random_sub.url

    em = discord.Embed(title = name)
    em.set_image(url = url)

    await ctx.send(embed = em)


@client.command(name='wasup')
async def wasup(ctx):
    response = ["I am good 👌", "i'm off the grid", "man leave me alone ✔️"]
    await ctx.send(choice(response))

# play function (play music in the server from youtube)
@client.command(name='play', help='This command plays music')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel 🎤")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client
    
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

# stop function(which stop the music)
@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


client.run('TOKEN')
