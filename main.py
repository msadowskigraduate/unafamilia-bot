from user_welcome import welcome_member_to_the_guild
from on_guild_join import intialize_order_channels
import os
from raidpackage import raidpackage_intro
from item_definitions import populate_items
import discord
from dotenv import load_dotenv


client = discord.Client()
load_dotenv()
CONFIRMED_ORDER_CHANNEL_ID = os.getenv('CONFIRMED_ORDER_CHANNEL_ID')
ORDER_INIT_CHANNEL_ID = os.getenv('ORDER_INIT_CHANNEL_ID')
TOKEN = os.getenv('TOKEN')

storage = {}
initMsgId = 0


@client.event
async def on_ready():
    guild = client.guilds[0]
    confirmed_channel, order_channel = await intialize_order_channels(guild, client, CONFIRMED_ORDER_CHANNEL_ID, ORDER_INIT_CHANNEL_ID)
    populate_items()
    await raidpackage_intro(order_channel, confirmed_channel, client)
   
@client.event
async def on_member_join(member):
    await welcome_member_to_the_guild(member, client)

client.run(TOKEN)
