import asyncio
from logging import error
import discord
from discord.client import Client
import item_definitions
import json

_error_messages = []


async def raidpackage_intro(order_channel, confirmed_channel, client):
    initPost = discord.Embed(title="Una Familia Raid Consumables Ordering Service", url='', color=0x109319, description='Click the 📝 reaction below to begin your order')
    initPost.add_field(name="Intro", value="Welcome to the raid consumable ordering service. You can use this service to order consumables before a raid night at a cheaper price than the auction house.", inline=False)
    initPost.add_field(name="Starting a new order", value="To begin, click the 📝 emoji below, and the bot will send you a DM. Simply click the items you want and type the quantities. Click the green tick to confirm your order.", inline=False)
    initPost.add_field(name="Delivery and payment", value="An officer will mail you the items, and message you the price to deposit into the guild bank before the raid begins.", inline=False)
    initMsg = await order_channel.send(embed=initPost)
    await initMsg.add_reaction(item_definitions.REACTION_NEW_ORDER)
    
    def check_channel_and_user_not_client(payload):
        return str(payload.emoji) == item_definitions.REACTION_NEW_ORDER and payload.channel_id == order_channel.id and payload.user_id != client.user.id
    
    reaction_payload = await client.wait_for('raw_reaction_add', check=check_channel_and_user_not_client)
    usr = await client.fetch_user(reaction_payload.user_id)
    sent_message, preorder_embed = await create_dm_preorder(usr, reaction_payload, client)


    #Clean up reaction
    await initMsg.remove_reaction(item_definitions.REACTION_NEW_ORDER, usr)

    async def listen(client, sent_message, preorder_embed, usr, confirmed_channel):
        #Process Order Reactions
        pending_reactions = [client.wait_for('raw_reaction_remove', check=lambda payload: payload.user_id != client.user.id),
                client.wait_for('raw_reaction_add', check=lambda payload: payload.user_id != client.user.id)]
        processed_reactions, pending_reactions = await asyncio.wait(pending_reactions, return_when=asyncio.FIRST_COMPLETED)

        for processed_reaction in processed_reactions:
            payload = await processed_reaction
            if payload.event_type == 'REACTION_ADD':
                await wait_for_order_reaction_add(payload, client, sent_message, preorder_embed, usr, confirmed_channel)

            if payload.event_type == 'REACTION_REMOVE':
                await wait_for_order_reaction_remove(payload, sent_message, preorder_embed)
            
            if str(payload.emoji) == item_definitions.REACTION_ACCEPT and payload.channel_id != confirmed_channel:
                user = await client.fetch_user(payload.user_id)
                preorder_embed.title = "Confirmed RaidPackage Order"
                preorder_embed.description = "Chosen Consumable Package:"
                preorder_embed.set_footer(text="")
                order_posting = await confirmed_channel.send(embed=preorder_embed)
                await order_posting.add_reaction('✅')
                await order_posting.add_reaction('💵')
                await user.send(f"Your order is confirmed: {order_posting.jump_url}")
                await sent_message.delete()
                return

            if str(payload.emoji) == item_definitions.REACTION_CANCEL:
                await cancel_order(sent_message, payload.user_id, client)
                return

        await listen(client, sent_message, preorder_embed, usr, confirmed_channel)
    
    await listen(client, sent_message, preorder_embed, usr, confirmed_channel)

async def create_dm_preorder(usr, reaction_payload, client):
    # Create DMs 
    usr = await client.fetch_user(reaction_payload.user_id)
    preorder_embed = discord.Embed(title="Your RaidPackage Order", url='', color=0x109319, description='Choose your options by clicking the emojis below:')
    preorder_embed.set_author(name=usr)

    current_pos = 0
    for item in item_definitions.items:
        if item.position_id == current_pos:
            preorder_embed.add_field(name=item.item_category, value='None', inline=False)
            current_pos += 1

    preorder_embed.set_footer(text=f'To confirm order click ✅\n To cancel order click ❌')

    sent_message = await usr.send(embed=preorder_embed)

    for item in item_definitions.items:
        await sent_message.add_reaction(item.item_emoji)

    await sent_message.add_reaction(item_definitions.REACTION_ACCEPT)
    await sent_message.add_reaction(item_definitions.REACTION_CANCEL)
    return sent_message, preorder_embed


async def wait_for_order_reaction_add(payload, client, sent_message, preorder_embed, usr, order_channel):  
    for item in item_definitions.items:
        if str(payload.emoji) == item.item_emoji:
            qtyReq = await process_user_quantity_input(client, usr, item.item_name, item.item_max, payload.user_id) 
            if qtyReq == None:
                return
            else:
                await sent_message.edit(embed=preorder_embed.set_field_at(item.position_id, name=item.item_category, 
                                        value=item.item_name + f" x{qtyReq}", inline=False))
                break


async def wait_for_order_reaction_remove(reaction_remove_payload, sent_message, preorder_embed):
    for item in item_definitions.items:
        if str(reaction_remove_payload.emoji) == item.item_emoji:
            await sent_message.edit(embed=preorder_embed.set_field_at(item.position_id, name=item.item_category, value='None', inline=False))
            break
    

async def cancel_order(msg, usr_id, client):
    await msg.delete()
    cancelMsg = discord.Embed(title="Order Cancelled", url='', color=0x109319)
    usr = await client.fetch_user(usr_id)
    await usr.send(embed=cancelMsg)


async def process_user_quantity_input(client, usr, item, qtyMax, usr_id):
    qtyEmbed = discord.Embed(title=item, url='', color=0x109319, description=f"Enter quantity required, for example 20 (Max {qtyMax})")
    qtyEmbed.set_footer(text="If the bot doesn't respond, un-click and re-click the reaction")
    botMsg = await usr.send(embed=qtyEmbed)

    def checkMsg(msg):
        if msg.content != "":
            print(msg.content)
            qty = int(msg.content)
            return True
                    
    try:
        msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
    except asyncio.TimeoutError:
        await botMsg.delete()
        msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
        await cancel_order(msg, usr_id, client)
    
    # non-numeric string
    except TypeError:
        error_msg = await usr.send(f"You must enter a number - please unclick and reclick the {item} emoji")
        _error_messages.append(error_msg)
    except ValueError:
        await botMsg.delete()
        error_msg = await usr.send(f"You must enter a number - please unclick and reclick the {item} emoji")
        _error_messages.append(error_msg)
    else:
        await botMsg.delete()
        
        if len(_error_messages) > 0:
            for error_msg in _error_messages:
                await error_msg.delete()
                _error_messages.remove(error_msg)
        return int(msg.content)