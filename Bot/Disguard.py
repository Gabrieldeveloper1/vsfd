'''This file contains the main runtime operations of Disguard. Cogs, the main features, are split into a trio of files'''

import discord
from discord.ext import commands, tasks
import dns
import secure
import database
import Antispam
import Cyberlog
import os
import datetime
import collections
import asyncio
import traceback
import random


booted = False
cogs = ['Cyberlog', 'Antispam', 'Moderation', 'Birthdays']
print("Booting...")

def prefix(bot, message):
    return '.' if type(message.channel) is not discord.TextChannel else database.GetPrefix(message.guild)

bot = commands.Bot(command_prefix=prefix)
bot.remove_command('help')

indexes = 'Indexes'

@tasks.loop(hours=1)
async def valentinesDaySend():
    if datetime.datetime.now().strftime('%H:%M') > '22:45':
        await bot.get_user(596381991151337482).send(secure.endVD())
        valentinesDaySend.cancel()
    try:
        path = 'G:/My Drive/Other/ur mom'
        image = False
        while not image:
            resultingPic = random.randint(0, len(os.listdir(path)))
            if not '.ini' in os.listdir(path)[resultingPic]: image = True
        await bot.get_user(596381991151337482).send(file=discord.File('{}/{}'.format(path,os.listdir(path)[resultingPic]), os.listdir(path)[resultingPic]))
        def cancelCheck(r, u): return str(r) == '❌' and u.id == 596381991151337482 and type(r.message.channel) is discord.DMChannel
        await bot.wait_for('reaction_add', check=cancelCheck)
        await bot.get_user(596381991151337482).send('Cancelled picture sending. `.lexy` to restart.')
        valentinesDaySend.cancel()
    except: traceback.print_exc()

@tasks.loop(minutes=1)
async def valentinesDayKickoff():
    if datetime.datetime.now().strftime('%H:%M') >= '07:45' and datetime.datetime.now().strftime('%m %d') == '02 14':
        await bot.get_user(596381991151337482).send(secure.vd())
        valentinesDaySend.start()
        valentinesDayKickoff.cancel()

@bot.command()
async def lexy(ctx):
    if ctx.author.id == 596381991151337482: valentinesDaySend.start()

@bot.listen()
async def on_ready(): #Method is called whenever bot is ready after connection/reconnection. Mostly deals with database verification and creation
    '''Method called when bot connects and all the internals are ready'''
    global booted
    global loading
    if not booted:
        booted=True
        loading = bot.get_emoji(573298271775227914)
        valentinesDayKickoff.start()
        await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name="my boss (Verifying database...)", type=discord.ActivityType.listening))
        for cog in cogs:
            try:
                bot.load_extension(cog)
            except:
                pass
        await database.Verification(bot)
        await Antispam.PrepareFilters(bot)
        Cyberlog.ConfigureSummaries(bot)
        await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name="my boss (Indexing messages...)", type=discord.ActivityType.listening))
        for server in bot.guilds:
            print('Indexing '+server.name)
            for channel in server.text_channels:
                path = "{}/{}/{}".format(indexes,server.id, channel.id)
                try: os.makedirs(path)
                except FileExistsError: pass
                try: 
                    async for message in channel.history(limit=None, after=datetime.datetime.now() - datetime.timedelta(days=30)):
                        if not message.author.bot:
                            if '{}_{}.txt'.format(message.id, message.author.id) in os.listdir(path): break
                            try: f = open('{}/{}_{}.txt'.format(path, message.id, message.author.id), "w+")
                            except FileNotFoundError: pass
                            try: f.write('{}\n{}\n{}'.format(message.created_at.strftime('%b %d, %Y - %I:%M %p'), message.author.name, message.content))
                            except UnicodeEncodeError: pass
                            try: f.close()
                            except: pass
                            if (datetime.datetime.utcnow() - message.created_at).days < 7 and await database.GetImageLogPerms(server):
                                attach = 'Attachments/{}/{}/{}'.format(message.guild.id, message.channel.id, message.id)
                                try: os.makedirs(attach)
                                except FileExistsError: pass
                                for attachment in message.attachments:
                                    if attachment.size / 1000000 < 8:
                                        try: await attachment.save('{}/{}'.format(attach, attachment.filename))
                                        except discord.HTTPException: pass
                except discord.Forbidden: pass
            Cyberlog.indexed[server.id] = True
        print("Indexed")
    print("Booted")
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name="your servers", type=discord.ActivityType.watching))    

@bot.command()
async def verify(ctx):
    if ctx.author.id == 247412852925661185:
        status = await ctx.send("Verifying...")
        await database.Verification(bot)
        await status.delete()

@bot.command()
async def help(ctx):
    await ctx.send(embed=discord.Embed(description="[View help here](https://disguard.netlify.com/commands)"))

@bot.command()
async def ping(ctx):
    m = await ctx.send('Pong!')
    await m.edit(content='Pong! {}ms'.format(round((datetime.datetime.utcnow() - ctx.message.created_at).microseconds / 1000)))


database.Initialize(secure.token())
bot.run(secure.token()) #Bot token stored in another file, otherwise anyone reading this could start the bot
#database.Initialize(secure.beta())
#bot.run(secure.beta())
