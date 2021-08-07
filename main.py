import os
import discord
import asyncio
from discord import user
from discord import embeds
from dotenv import load_dotenv


client = discord.Client()
load_dotenv()
CHANNEL_ID = os.getenv('CHANNEL_ID')
TOKEN = os.getenv('TOKEN')

storage = {}


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!raidpackage'):
        preorder_embed = discord.Embed(title="Your RaidPackage Order", url='', color=0x109319, description='Choose your options by clicking the emojis below:')
        preorder_embed.set_author(name=message.author)
        preorder_embed.add_field(name="Weapon Enhancement", value='None', inline=False)
        preorder_embed.add_field(name="Potion", value='None', inline=False)
        preorder_embed.set_footer(text=f'To confirm order click ✅')
        sent_message = await message.author.send(embed=preorder_embed)
        storage[message.author.id] = sent_message
        await sent_message.add_reaction('<:ShadedWeight:873183450063069194>')
        await sent_message.add_reaction('<:ShadedSharpen:873183190880235530>')
        await sent_message.add_reaction('<:PotSpectralInt:873187413424484402>')
        await sent_message.add_reaction('<:PotSpectralStr:873183439656996895>')
        await sent_message.add_reaction('✅')
        await sent_message.add_reaction('❌')
        await message.delete()

@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return

    if payload.event_type == 'REACTION_REMOVE':
        return

    usr = await client.fetch_user(payload.user_id)
    
    if str(payload.emoji) == '❌':
            await cancelOrder(storage[payload.user_id], payload.user_id)

    if str(payload.emoji) == '<:PotSpectralStr:873183439656996895>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        item = "Potion of Greater Strength"
               
        qtyReq = await ProcessUserQtyInput(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await msg.edit(embed=order.set_field_at(1, name="Potion", value=item + f" x{qtyReq}", inline=False))
            
    if str(payload.emoji) == '<:PotSpectralInt:873187413424484402>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(1, name="Potion", value="Potion of Greater Intellect", inline=False))

    if str(payload.emoji) == '<:ShadedSharpen:873183190880235530>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value="Greater Sharpening Stone", inline=False))

    if str(payload.emoji) == '<:ShadedWeight:873183450063069194>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value="Greater Weight Stone", inline=False))

    if str(payload.emoji) == '✅' and payload.CHANNEL_ID != CHANNEL_ID:
        channel = client.get_channel(CHANNEL_ID)
        user = await client.fetch_user(payload.user_id)
        preorder_embed = storage[payload.user_id].embeds[0]
        preorder_embed.title = "Confirmed RaidPackage Order"
        preorder_embed.description = "Chosen Consumable Package:"
        order_posting = await channel.send(embed=preorder_embed)
        await order_posting.add_reaction('✅')
        await order_posting.add_reaction('💵')
        await user.send(f"Your order is confirmed: {order_posting.jump_url}")
        del storage[payload.user_id]


async def cancelOrder(msg, usr_id):
    await msg.delete()
    del storage[usr_id]
    cancelMsg = discord.Embed(title="Order Cancelled", url='', color=0x109319)
    usr = await client.fetch_user(usr_id)
    await usr.send(embed=cancelMsg)


async def ProcessUserQtyInput(client, usr, item, qtyMax, usr_id):
    qtyEmbed = discord.Embed(title=item, url='', color=0x109319, description=f"Enter quantity required, for example 20 (Max {qtyMax})")
    botMsg = await usr.send(embed=qtyEmbed)

    def checkMsg(msg):
        try:
            qty = int(msg.content)
            return True
        except Exception:
            raise Exception("mismatch type in ProcessUserQtyInput")

    try:
        msg = await client.wait_for("message", timeout=5.0, check=checkMsg)
    except asyncio.TimeoutError:
        await botMsg.delete()
        await cancelOrder(storage[usr_id], usr_id)
    else:
        await botMsg.delete()
        return int(msg.content)
        



    
    

client.run(TOKEN)
