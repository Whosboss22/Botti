
import discord
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from botticommands import *

# create discord client
client = discord.Client()
token = 'OTc2NTY2MTY3MzExMzY4MjMy.GU8ZAI.NSSzrqI09VeEgBgYaW4qybzpxUXkN_6dVEA0UM'

# bot is ready
@client.event
async def on_ready(): 
    try:
        print(client.user.name + " initialized!")
    except Exception as e:
        print(e)
        

#---------------------------------------------COMMAND-FUNCTIONS--------------------------------------------------------

# on new message
@client.event
async def on_message(message):
    if message.author == client.user: return
    if message.author.bot: return
    await process(message)
# start bot
client.run(token)