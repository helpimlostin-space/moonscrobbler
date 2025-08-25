import os
import requests
import discord
from discord.ext import tasks
import urllib.parse

# var (rawr)
LASTFM_USER = os.getenv("LASTFM_USER")
API_KEY = os.getenv("LASTFM_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

last_track = None

def get_last_track():
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={LASTFM_USER}&api_key={API_KEY}&format=json&limit=1"
    r = requests.get(url).json()
    track = r['recenttracks']['track'][0]

    # in case empty or image links say nuh uh
    image_url = None
    if track['image'] and track['image'][-1]['#text']:
        image_url = track['image'][-1]['#text']

    artist = track['artist']['#text']
    name = track['name']
    album = track['album']['#text']

    # epic url moment
    artist_url_enc = urllib.parse.quote(artist, safe='')
    track_url_enc = urllib.parse.quote(name, safe='')
    # track and artist sigma alpha male
    lastfm_track_url = f"https://www.last.fm/music/{artist_url_enc}/_/{track_url_enc}"
    lastfm_artist_url = f"https://www.last.fm/music/{artist_url_enc}"

    return {
        "name": name,
        "artist": artist,
        "album": album,
        "image": image_url,
        "nowplaying": "@attr" in track and "nowplaying" in track["@attr"],
        "url": lastfm_track_url,
        "artist_url": lastfm_artist_url
    }

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # statusstatuststsaydyfjnfjnrek
    activity = discord.Activity(type=discord.ActivityType.listening, name="moon’s lastfm scrobbles")
    await client.change_presence(activity=activity)

    check_scrobbles.start()

@tasks.loop(seconds=30)
async def check_scrobbles():
    global last_track
    try:
        track = get_last_track()
        if track != last_track and track["nowplaying"]:
            channel = client.get_channel(CHANNEL_ID)
            embed = discord.Embed(
                title=track["name"],
                url=track["url"],
                description=f"By: [{track['artist']}]({track['artist_url']})\nFrom: {track['album']}",
                color=121247
            )
            if track['image']:
                embed.set_thumbnail(url=track['image'])
            embed.set_footer(text="From Moon's LastFM scrobbles")
            await channel.send(embed=embed)
            last_track = track
    except Exception as e:
        print("Error:", e)

client.run(DISCORD_TOKEN)