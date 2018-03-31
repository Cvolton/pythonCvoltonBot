import discord
import asyncio
import urllib
import datetime
import requests
import youtube_dl
import subprocess
import datetime
from datetime import timezone
import threading
import tweepy
import re

file = open('/home/pi/Desktop/botstuff/twitter/CONSUMER_KEY.txt', 'r')
CONSUMER_KEY = file.read() #note: this twitter integration has nothing to do with the gdps, I just use CvoltonBot for other stuff too
file = open('/home/pi/Desktop/botstuff/twitter/CONSUMER_SECRET.txt', 'r')
CONSUMER_SECRET = file.read()
file = open('/home/pi/Desktop/botstuff/twitter/ACCESS_KEY.txt', 'r')
ACCESS_KEY = file.read()
file = open('/home/pi/Desktop/botstuff/twitter/ACCESS_SECRET.txt', 'r')
ACCESS_SECRET = file.read()
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
client = discord.Client()

file = open('/home/pi/Desktop/botstuff/twitter/twitter_command.txt', 'r')
twitterCommand = file.read()
file = open('/home/pi/Desktop/botstuff/twitter/twitter_channel.txt', 'r')
twitterChannel = file.read()
file = open('/home/pi/Desktop/botstuff/gdpssecret.txt', 'r')
gdpssecret = file.read()

def transferpermsMultithread(members,members2):
    for member in members:
        transferperms(member)
    
def transferperms(person):
    messagething = ""
    for i, val in enumerate(person.roles):
        messagething += val.id + ","
    messagething = messagething[:-1]
    print(messagething)
    print("http://127.0.0.1:9010/a/tools/bot/discordLinkTransferRoles.php?roles="+messagething+"&discordID="+str(person.id)+"&secret="+gdpssecret)
    return urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/discordLinkTransferRoles.php?roles="+messagething+"&discordID="+str(person.id)+"&secret="+gdpssecret).read().decode('UTF-8')

def songUpload(song,message,client):
    msg = client.send_message(message.channel, 'Downloading song, please wait')
    options = {
        'format': 'bestaudio/best', # choice of quality
        'extractaudio' : True,      # only keep the audio
        'audioformat' : "mp3",      # convert to mp3 
        'outtmpl': '/var/www/songcdn/temp/%(id)s',        # name the file the ID of the video
        'noplaylist' : True,        # only download single song, not playlist
        } 
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([song])
        r = ydl.extract_info(song, download=False)
    client.edit_message(msg, 'Reuploading ' + r['id'] + " - " + r['title'] + " by " + r['uploader'])
    subprocess.run(['avconv','-i','/var/www/songcdn/temp/'+r['id'],'-n','-c:a','libmp3lame','-ac','2','-b:a','190k','/var/www/songcdn/'+r['id']+".mp3"])
    link = "http://songcdn.michaelbrabec.cz:9010/"+r['id']
    link = urllib.parse.quote_plus(link)
    title = urllib.parse.quote_plus(r['title'])
    uploader = urllib.parse.quote_plus(r['uploader'])
    songid = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/songAddBot.php?link="+link+".mp3&name="+title+"&author="+uploader).read().decode('UTF-8')
    print('SongID: '+songid+"\r\nReuploaded " + r['id'] + " - " + title + " by " + uploader)
    
def getStatus(stra, name):
    try:
        r = requests.head(stra)
        status = "Offline"
        if r.status_code == 200:
            status = "Online "
        return name + " | " + status + " | " + str(r.status_code)
        # prints the int of the status code. Find more at httpstatusrappers.com :)
    except requests.ConnectionError:
        return name + " | Offline | Error"

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    await client.change_presence(game=discord.Game(name='Online - ' + str(datetime.datetime.now())))
    if message.content.startswith('!'):
        print(message.content)
    if message.author.id == "259732376303697920":
        pass
    elif message.content.startswith('!isuo'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!isup'):
        await client.send_message(message.channel, 'I am online!')
    elif message.content.startswith('!level'):
        level = message.content.replace("!level ","")
        level = urllib.parse.quote_plus(level)
        levelinfo = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/levelSearchBot.php?str="+level).read().decode('UTF-8')
        await client.send_message(message.channel, levelinfo)
    elif message.content.startswith('!userlevels'):
        userlevels = message.content.replace("!userlevels ","")
        levelinfo = requests.post("http://127.0.0.1:9010/a/tools/bot/userLevelSearchBot.php", data={'str': userlevels}, headers={'User-Agent': "CvoltonGDPS"})
        await client.send_message(message.channel, levelinfo.text)
    elif message.content.startswith('!links'):
        file = open('/home/pi/Desktop/botstuff/links.txt', 'r')
        await client.send_message(message.channel, file.read())
    elif message.content.startswith('!help'):
        file = open('/home/pi/Desktop/botstuff/help.txt', 'r')
        await client.send_message(message.channel, file.read())
    elif message.content.startswith('!download'):
        file = open('/home/pi/Desktop/botstuff/latest.txt', 'r')
        await client.send_message(message.channel, file.read())
    elif message.content.startswith('!songlist'):
        pg = message.content.replace("!songlist ","")
        songinfo = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/songListBot.php?page="+pg).read().decode('UTF-8')
        await client.send_message(message.channel, songinfo)
    elif message.content.startswith('!searchsong'):
        query = message.content.replace("!searchsong ","")
        query = urllib.parse.quote_plus(query)
        songinfo = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/songSearchBot.php?str="+query).read().decode('UTF-8')
        await client.send_message(message.channel, songinfo)
    elif message.content.startswith('!whorated'):
        query = message.content.replace("!whorated ","")
        rate = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/whoRatedBot.php?level="+query).read().decode('UTF-8')
        await client.send_message(message.channel, rate)
    elif message.content.startswith('!player'):
        query = message.content.replace("!player ","")
        query = urllib.parse.quote_plus(query)
        player = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/playerStatsBot.php?player="+query).read().decode('UTF-8')
        await client.send_message(message.channel, player)
    elif message.content.startswith('!top'):
        query = message.content.replace("!top ","")
        split = query.split(' ')
        try:
            type = split[0]
        except:
            type = "none"
        try:
            page = split[1]
        except:
            page = "0"
        
        leaderboards = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/leaderboardsBot.php?type="+type+"&page="+page).read().decode('UTF-8')
        await client.send_message(message.channel, leaderboards)
    elif message.content.startswith('!mods'):
        mods = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/modActionsBot.php").read().decode('UTF-8')
        await client.send_message(message.channel, mods)
    elif message.content.startswith('!daily'):
        daily = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/dailyLevelBot.php").read().decode('UTF-8')
        await client.send_message(message.channel, daily)
    elif message.content.startswith('!time'):
        time = datetime.datetime.now()
        await client.send_message(message.channel, time)
    elif message.content.startswith('!server'):
        tmp = await client.send_message(message.channel, 'Attempting to connect to servers...')
        answer = "CvoltonGDPS\r\n```"
        answer = answer + getStatus("http://pi.michaelbrabec.cz:9010/a/downloadGJLevel22.php","\r\nmichaelbrabec.cz (web)")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://127.0.0.1:9010/a/downloadGJLevel22.php","\r\n     CvoltonGDPS (PHP)")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://192.168.2.144:8000/downloadGJLevel","\r\n  CvoltonGDPS (Python)")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://192.168.2.113:26205/mineshack/load.swf","\r\n             Mineshack")
        await client.edit_message(tmp, answer + "```")
        answer = answer + "```\r\nOther\r\n```"
        answer = answer + getStatus("http://www.boomlings.com/database/downloadGJLevel22.php","      Main GD Server")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://www.boomlings.com/database2/downloadGJLevel22.php","\r\n      Test GD Server")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://www.robtopgames.com/database/downloadGJLevel.php","\r\n      Beta GD Server")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://52.33.77.121/database/gdps/downloadGJLevel22.php","\r\n         TeamHaxGDPS")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://yoanndp.tk/server21/downloadGJLevel22.php","\r\n             Yoanndp")
        await client.edit_message(tmp, answer + "```")
        answer = answer + getStatus("http://kadegdlps.altervista.org/database/downloadGJLevel.php","\r\n            KadeGDPS")
        await client.edit_message(tmp, answer + "```")
    elif message.content.startswith('!songreup'):
        song = message.content.replace("!songreup ","")
        ReupThread = threading.Thread(target=songUpload,args=(song,message,client))
        ReupThread.start()
        leaderboards = urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/latestSongBot.php").read().decode('UTF-8')
        await client.send_message(message.channel, "Check SongID "+leaderboards+" in a few minutes")
    elif message.content.startswith('!'+twitterCommand):
        messagecontent = message.content.replace("!"+twitterCommand+" ","")
        api.update_status(messagecontent)
        await client.send_message(message.channel, "100 priznal")
        print(message.channel.id)
    elif message.channel.id == twitterChannel:
        if message.content != "xxl exkluzivne 100 priznal":
            api.update_status(message.content)
            await client.send_message(message.channel, "xxl exkluzivne 100 priznal")
    elif message.content.startswith('!linkacc'):
        account = message.content.replace("!linkacc ","")
        await client.send_message(message.channel, urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/discordLinkReq.php?account="+account+"&discordID="+str(message.author.id)+"&secret="+gdpssecret).read().decode('UTF-8'))
    elif message.content.startswith('!unlinkacc'):
        account = message.content.replace("!unlinkacc ","")
        await client.send_message(message.channel, urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/discordLinkUnlink.php?discordID="+str(message.author.id)+"&secret="+gdpssecret).read().decode('UTF-8'))
    elif message.content.startswith('!resetpassword'):
        await client.send_message(message.channel, urllib.request.urlopen("http://127.0.0.1:9010/a/tools/bot/discordLinkResetPass.php?discordID="+str(message.author.id)+"&secret="+gdpssecret).read().decode('UTF-8'))
    elif message.content.startswith('!listroles'):
        for i, val in enumerate(message.author.roles):
            await client.send_message(message.channel, str(val.id) + " : " + val.name)
    elif message.server.id == "267761099951046656":
        if message.content.startswith('!transferperms'):
            person = message.author
            if '<@' in message.content:
                personid = message.content.split('<@')[1]
                personid = personid.split('>')[0]
                non_decimal = re.compile(r'[^\d.]+')
                personid = non_decimal.sub('', personid)
                print(personid)
                person = message.server.get_member(personid)
            await client.send_message(message.channel, "Transferring roles")
            await client.send_message(message.channel, transferperms(person))
        elif message.content.startswith('!listmembers'):
            await client.send_message(message.channel, "bot gonna lag now lol prenk")
            timebeforelag = datetime.datetime.now(tz=timezone.utc).timestamp()
            TransferThread = threading.Thread(target=transferpermsMultithread,args=(message.server.members,message.server.members))
            TransferThread.start()
            timeafterlag = datetime.datetime.now(tz=timezone.utc).timestamp()
            finaltime = str(timeafterlag - timebeforelag)
            await client.send_message(message.channel, "done, " + finaltime + "s")

file = open('/home/pi/Desktop/botstuff/token.txt', 'r')
client.run(file.read())
