import asyncio
from logging import error
import discord
from discord.client import Client
import icon_definitions

_error_messages = []

async def raidpackage_intro(order_channel, confirmed_channel, client):
    initPost = discord.Embed(title="Una Familia Raid Consumables Ordering Service", url='', color=0x109319, description='Click the 📝 reaction below to begin your order')
    initPost.add_field(name="Intro", value="Welcome to the raid consumable ordering service. You can use this service to order consumables before a raid night at a cheaper price than the auction house.", inline=False)
    initPost.add_field(name="Starting a new order", value="To begin, click the 📝 emoji below, and the bot will send you a DM. Simply click the items you want and type the quantities. Click the green tick to confirm your order.", inline=False)
    initPost.add_field(name="Delivery and payment", value="An officer will mail you the items, and message you the price to deposit into the guild bank before the raid begins.", inline=False)
    initMsg = await order_channel.send(embed=initPost)
    await initMsg.add_reaction(icon_definitions.REACTION_NEW_ORDER)
    
    def check_channel_and_user_not_client(payload):
        return str(payload.emoji) == icon_definitions.REACTION_NEW_ORDER and payload.channel_id == order_channel.id and payload.user_id != client.user.id
    
    reaction_payload = await client.wait_for('raw_reaction_add', check=check_channel_and_user_not_client)
    usr = await client.fetch_user(reaction_payload.user_id)
    sent_message, preorder_embed = await create_dm_preorder(usr, reaction_payload, client)


    #Clean up reaction
    await initMsg.remove_reaction(icon_definitions.REACTION_NEW_ORDER, usr)

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
            
            if str(payload.emoji) == icon_definitions.REACTION_ACCEPT and payload.channel_id != confirmed_channel:
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

            if str(payload.emoji) == icon_definitions.REACTION_CANCEL:
                await cancel_order(sent_message, payload.user_id, client)
                return

        await listen(client, sent_message, preorder_embed, usr, confirmed_channel)
    
    
    await listen(client, sent_message, preorder_embed, usr, confirmed_channel)

async def create_dm_preorder(usr, reaction_payload, client):
    # Create DMs 
    usr = await client.fetch_user(reaction_payload.user_id)
    preorder_embed = discord.Embed(title="Your RaidPackage Order", url='', color=0x109319, description='Choose your options by clicking the emojis below:')
    preorder_embed.set_author(name=usr)
    preorder_embed.add_field(name="Weapon Enhancement", value='None', inline=False)        
    preorder_embed.add_field(name="Combat Potions", value='None', inline=False)
    preorder_embed.add_field(name="Augment Runes", value='None', inline=False)
    preorder_embed.add_field(name="Armor Kits", value='None', inline=False)
    preorder_embed.add_field(name="Utility Potions", value='None', inline=False)
    preorder_embed.add_field(name="Extras", value='None', inline=False)
    preorder_embed.set_footer(text=f'To confirm order click ✅\n To cancel order click ❌')

    sent_message = await usr.send(embed=preorder_embed)
    await sent_message.add_reaction(icon_definitions.emoji_augment_rune)
    await sent_message.add_reaction(icon_definitions.emoji_spectral_int)
    await sent_message.add_reaction(icon_definitions.emoji_spectral_str)
    await sent_message.add_reaction(icon_definitions.emoji_spectral_agi)
    await sent_message.add_reaction(icon_definitions.emoji_phamtom_fire)
    await sent_message.add_reaction(icon_definitions.emoji_armor_kit)
    await sent_message.add_reaction(icon_definitions.emoji_shadowcore_oil)
    await sent_message.add_reaction(icon_definitions.emoji_embalmers_oil)
    await sent_message.add_reaction(icon_definitions.emoji_shaded_weightstone)
    await sent_message.add_reaction(icon_definitions.emoji_shaded_sharpen)
    await sent_message.add_reaction(icon_definitions.emoji_healing_pot)
    await sent_message.add_reaction(icon_definitions.emoji_mana_pot)
    await sent_message.add_reaction(icon_definitions.emoji_rejuve_pot)
    await sent_message.add_reaction(icon_definitions.emoji_tome)
    
    await sent_message.add_reaction(icon_definitions.REACTION_ACCEPT)
    await sent_message.add_reaction(icon_definitions.REACTION_CANCEL)
    return sent_message, preorder_embed

async def wait_for_order_reaction_add(payload, client, sent_message, preorder_embed, usr, order_channel):  

    if str(payload.emoji) == icon_definitions.emoji_embalmers_oil:
        item = "Embalmer's Oil"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 6, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(0, name="Weapon Enhancement", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_shadowcore_oil:
        item = "Embalmer's Oil"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 6, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(0, name="Weapon Enhancement", value=item + f" x{qtyReq}", inline=False))
    
    if str(payload.emoji) == icon_definitions.emoji_shaded_sharpen:
        item = "Shaded Sharpening Stone"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 6, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(0, name="Weapon Enhancement", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_shaded_weightstone:
        item = "Shaded Weightstone"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 6, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(0, name="Weapon Enhancement", value=item + f" x{qtyReq}", inline=False))
    
    if str(payload.emoji) == icon_definitions.emoji_spectral_str:
        item = "Potion of Spectral Strength"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value=item + f" x{qtyReq}", inline=False))
            
    if str(payload.emoji) == icon_definitions.emoji_spectral_int:
        item = "Potion of Spectral Intellect"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_spectral_agi:
        item = "Potion of Spectral Agility"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_phamtom_fire:
        item = "Potion of Phantom Fire"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 40, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_augment_rune:
        item = "Augment Runes"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 20, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(2, name="Augment Runes", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_armor_kit:
        item = "Heavy Desolate Armor Kit"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 2, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(3, name="Armor Kits", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_healing_pot:
        item = "Spiritual Healing Potion"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 20, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value=item + f" x{qtyReq}", inline=False))

    if str(payload.emoji) == icon_definitions.emoji_mana_pot:
        item = "Spiritual Mana Potion"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 20, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value=item + f" x{qtyReq}", inline=False))
    
    if str(payload.emoji) == icon_definitions.emoji_rejuve_pot:
        item = "Spiritual Rejuvenation Potion"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 20, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value=item + f" x{qtyReq}", inline=False))


    if str(payload.emoji) == icon_definitions.emoji_tome:
        item = "Tome of the Still Mind"
               
        qtyReq = await process_user_quantity_input(client, usr, item, 20, payload.user_id) 
        if qtyReq == None:
            return
        else:
            await sent_message.edit(embed=preorder_embed.set_field_at(5, name="Extras", value=item + f" x{qtyReq}", inline=False))

    
async def wait_for_order_reaction_remove(reaction_remove_payload, sent_message, preorder_embed):
    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_shaded_sharpen:
        await sent_message.edit(embed=preorder_embed.set_field_at(0, name="Weapon Enhancement", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_shaded_weightstone:
        await sent_message.edit(embed=preorder_embed.set_field_at(0, name="Weapon Enhancement", value='None', inline=False))  
    
    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_spectral_str:
        await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_spectral_int:
        await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_spectral_agi:
        await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value='None', inline=False))
    
    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_phamtom_fire:
        await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_phamtom_fire:
        await sent_message.edit(embed=preorder_embed.set_field_at(1, name="Combat Potions", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_augment_rune:
        await sent_message.edit(embed=preorder_embed.set_field_at(2, name="Augment Runes", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_armor_kit:
        await sent_message.edit(embed=preorder_embed.set_field_at(3, name="Armor Kits", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_healing_pot:
        await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_rejuve_pot:
        await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value='None', inline=False)) 

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_mana_pot:
        await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value='None', inline=False))

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_mana_pot:
        await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Utility Potions", value='None', inline=False))        

    if str(reaction_remove_payload.emoji) == icon_definitions.emoji_tome:
        await sent_message.edit(embed=preorder_embed.set_field_at(4, name="Extras", value='None', inline=False))



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
        try:
            print(msg.content)
            qty = int(msg.content)
            return True
        except TypeError:
            print("Type error mismatch in raidpackage line 142") #need to implement proper handling here without crashing out program
            
    try:
        msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
    except asyncio.TimeoutError:
        await botMsg.delete()
        msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
        await cancel_order(msg, usr_id, client)
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