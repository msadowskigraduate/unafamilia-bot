from emoji_service import Emoji_service
from user_welcome import welcome_member_to_the_guild
from on_guild_join import intialize_order_channels
import os
from raidpackage import RaidPackageClient
from error_handler import Error_handler
from item_handler import Item_handler
import discord
from dotenv import load_dotenv


client = discord.Client()
load_dotenv()
CONFIRMED_ORDER_CHANNEL_ID = os.getenv('CONFIRMED_ORDER_CHANNEL_ID')
ORDER_INIT_CHANNEL_ID = os.getenv('ORDER_INIT_CHANNEL_ID')
TOKEN = os.getenv('TOKEN')

initMsgId = 0
raidpackage_client: RaidPackageClient = None
error_handler_client: Error_handler = None
item_handler_client: Item_handler = None
emoji_service_client: Emoji_service = None

@client.event
async def on_ready():
    global raidpackage_client
    global error_handler_client
    global emoji_service_client
    global item_handler_client
    guild = client.guilds[0]
    confirmed_channel, order_channel = await intialize_order_channels(guild, client, CONFIRMED_ORDER_CHANNEL_ID, ORDER_INIT_CHANNEL_ID)

    if error_handler_client is None:
        error_handler_client = Error_handler()

    if emoji_service_client is None:
        emoji_service_client = Emoji_service(guild)

    if item_handler_client is None:
        item_handler_client = Item_handler(emoji_service_client)
        await item_handler_client.populate_items()

    if raidpackage_client is None:
        raidpackage_client = RaidPackageClient(client, order_channel, confirmed_channel, error_handler_client, emoji_service_client, item_handler_client)

    await raidpackage_client.initialize_client()

@client.event
async def on_raw_reaction_add(payload):
    await raidpackage_client.handle_reaction(payload)

@client.event
async def on_raw_reaction_remove(payload):
    await raidpackage_client.handle_reaction(payload)

@client.event
async def on_member_join(member):
    await welcome_member_to_the_guild(member, client)

client.run(TOKEN)
