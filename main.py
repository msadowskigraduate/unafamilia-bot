import os
import discord
import asyncio
from discord import user
from discord import embeds
from dotenv import load_dotenv


client = discord.Client()
load_dotenv()
CHANNEL_ID = os.getenv('CONFIRMED_ORDER_CHANNEL_ID')
ORDER_INIT_CHANNEL_ID = os.getenv('ORDER_INIT_CHANNEL_ID')
TOKEN = os.getenv('TOKEN')

storage = {}
initMsgId = 0

@client.event
async def on_ready():
    initPost = discord.Embed(title="Una Familia Raid Consumables Ordering Service", url='', color=0x109319, description='Click the 📝 reaction below to begin your order')
    initPost.add_field(name="Intro", value="Welcome to the raid consumable ordering service. You can use this service to order consumables before a raid night at a cheaper price than the auction house.", inline=False)
    initPost.add_field(name="Starting a new order", value="To begin, click the 📝 emoji below, and the bot will send you a DM. Simply click the items you want and type the quantities. Click the green tick to confirm your order.", inline=False)
    initPost.add_field(name="Delivery and payment", value="An officer will mail you the items, and message you the price to deposit into the guild bank before the raid begins.", inline=False)
    channel = await client.fetch_channel(ORDER_INIT_CHANNEL_ID)
    initMsg = await channel.send(embed=initPost)
    await initMsg.add_reaction('📝')
    initMsgId = initMsg.id
    print(initMsgId)


@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return

    if payload.event_type == 'REACTION_REMOVE':
        return

    usr = await client.fetch_user(payload.user_id)
    

    if str(payload.emoji == '📝' and payload.channel_id == ORDER_INIT_CHANNEL_ID):
        preorder_embed = discord.Embed(title="Your RaidPackage Order", url='', color=0x109319, description='Choose your options by clicking the emojis below:')
        preorder_embed.set_author(name=usr)
        preorder_embed.add_field(name="Weapon Enhancement", value='None', inline=False)
        preorder_embed.add_field(name="Potion", value='None', inline=False)
        preorder_embed.set_footer(text=f'To confirm order click ✅')
        sent_message = await usr.send(embed=preorder_embed)
        storage[usr] = sent_message
        await sent_message.add_reaction('<:ShadedWeight:873183450063069194>')
        await sent_message.add_reaction('<:ShadedSharpen:873183190880235530>')
        await sent_message.add_reaction('<:PotSpectralInt:873187413424484402>')
        await sent_message.add_reaction('<:PotSpectralStr:873183439656996895>')
        await sent_message.add_reaction('✅')
        await sent_message.add_reaction('❌')
        message = payload.message_id
        channel = await client.fetch_channel(ORDER_INIT_CHANNEL_ID)
        reactMsg = await channel.fetch_message(message)
        await reactMsg.remove_reaction('📝', usr)

    msg = storage[usr]
    
    if str(payload.emoji) == '❌':
            await cancelOrder(storage[payload.user_id], payload.user_id)

    if str(payload.emoji) == '<:PotSpectralStr:873183439656996895>':
        order = msg.embeds[0]
        item = "Potion of Spectral Strength"
               
        qtyReq = await ProcessUserQtyInput(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await msg.edit(embed=order.set_field_at(1, name="Potion", value=item + f" x{qtyReq}", inline=False))
            
    if str(payload.emoji) == '<:PotSpectralInt:873187413424484402>':
        order = msg.embeds[0]
        item = "Potion of Spectral Intellect"
               
        qtyReq = await ProcessUserQtyInput(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await msg.edit(embed=order.set_field_at(1, name="Potion", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == '<:ShadedSharpen:873183190880235530>':
        order = msg.embeds[0]
        item = "Shaded Sharpening Stone"
               
        qtyReq = await ProcessUserQtyInput(client, usr, item, 6, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == '<:ShadedWeight:873183450063069194>':
        order = msg.embeds[0]
        item = "Shaded Weightstone"
               
        qtyReq = await ProcessUserQtyInput(client, usr, item, 6, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == '✅' and payload.channel_id != CHANNEL_ID:
        channel = await client.fetch_channel(CHANNEL_ID)
        user = await client.fetch_user(payload.user_id)
        preorder_embed = storage[payload.user_id].embeds[0]
        preorder_embed.title = "Confirmed RaidPackage Order"
        preorder_embed.description = "Chosen Consumable Package:"
        order_posting = await channel.send(embed=preorder_embed)
        await order_posting.add_reaction('✅')
        await order_posting.add_reaction('💵')
        await user.send(f"Your order is confirmed: {order_posting.jump_url}")
        del storage[payload.user_id]
        await msg.delete()


@client.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == client.user.id:
        return

    if payload.channel_id == ORDER_INIT_CHANNEL_ID:
        return

    msg = storage[payload.user_id]

    if str(payload.emoji) == '<:PotSpectralStr:873183439656996895>':
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(1, name="Potion", value='None', inline=False))

    if str(payload.emoji) == '<:PotSpectralInt:873187413424484402>':
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(1, name="Potion", value='None', inline=False))

    if str(payload.emoji) == '<:ShadedSharpen:873183190880235530>':
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value='None', inline=False))

    if str(payload.emoji) == '<:ShadedWeight:873183450063069194>':
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value='None', inline=False))


async def cancelOrder(msg, usr_id):
    await msg.delete()
    del storage[usr_id]
    cancelMsg = discord.Embed(title="Order Cancelled", url='', color=0x109319)
    usr = await client.fetch_user(usr_id)
    await usr.send(embed=cancelMsg)


async def ProcessUserQtyInput(client, usr, item, qtyMax, usr_id):
    qtyEmbed = discord.Embed(title=item, url='', color=0x109319, description=f"Enter quantity required, for example 20 (Max {qtyMax})")
    qtyEmbed.set_footer(text="If the bot doesn't respond, un-click and re-click the reaction")
    botMsg = await usr.send(embed=qtyEmbed)

    def checkMsg(msg):
        try:
            qty = int(msg.content)
            return True
        except Exception:
            raise Exception("mismatch type in ProcessUserQtyInput")

    try:
        msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
    except asyncio.TimeoutError:
        await botMsg.delete()
        await cancelOrder(storage[usr_id], usr_id)
    else:
        await botMsg.delete()
        return int(msg.content)
        
async def MessagePlayer():
    return

client.run(TOKEN)
