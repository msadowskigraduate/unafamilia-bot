import asyncio
from error_handler import Error_handler
from emoji_service import Emoji_service
from logging import error
import discord
from item_handler import Item_handler

class RaidPackageClient():

    class Order:
        def __init__(self, id:str, message: discord.Message, author: discord.Member, preorder_embed: discord.Embed):
            self.id = id
            self.message = message
            self.author = author
            self.preorder_embed = preorder_embed
            
           
    __init_message :discord.Message = None

    #Correlation between message and Order
    __responding_players = {}

    def __init__(self, client: discord.Client, order_channel: discord.TextChannel, confirm_channel: discord.TextChannel, error_handler_client: Error_handler, emoji_service_client: Emoji_service, item_handler_client: Item_handler):
        self.client = client
        self.order_channel = order_channel
        self.confirm_channel = confirm_channel
        self.error_handler_client = error_handler_client
        self.emoji_service_client = emoji_service_client
        self.item_handler_client = item_handler_client

    async def initialize_client(self):
        initPost = discord.Embed(title="Una Familia Raid Consumables Ordering Service", url='', color=0x109319, description='Click the 📝 reaction below to begin your order')
        initPost.add_field(name="Intro", value="Welcome to the raid consumable ordering service. You can use this service to order consumables before a raid night at a cheaper price than the auction house.", inline=False)
        initPost.add_field(name="Starting a new order", value="To begin, click the 📝 emoji below, and the bot will send you a DM. Simply click the items you want and type the quantities. Click the green tick to confirm your order.", inline=False)
        initPost.add_field(name="Delivery and payment", value="An officer will mail you the items, and message you the price to deposit into the guild bank before the raid begins.", inline=False)
        self.__init_message = await self.order_channel.send(embed=initPost)
        await self.__init_message.add_reaction(self.emoji_service_client.REACTION_NEW_ORDER)

    async def handle_reaction(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.client.user.id:
            return

        if str(payload.emoji) == self.emoji_service_client.REACTION_NEW_ORDER and payload.event_type == 'REACTION_ADD' and payload.channel_id == self.order_channel.id:
            await self.__listen_for_player_reaction(payload)

        order: self.Order = self.__responding_players.get(payload.message_id)
        if order is not None:
            await self.__listen_for_order_specification(payload, order)

    async def __listen_for_player_reaction(self, payload: discord.RawReactionActionEvent):
        usr = await self.client.fetch_user(payload.user_id)
        sent_message, preorder_embed = await self.__create_dm_preorder(usr, payload)
        await self.__init_message.remove_reaction(self.emoji_service_client.REACTION_NEW_ORDER, usr)
        self.__responding_players[sent_message.id] = self.Order(sent_message.id, sent_message, usr, preorder_embed)

    async def __listen_for_order_specification(self, payload: discord.RawReactionActionEvent, order: Order):
        #Process Order Reactions
        if payload.event_type == 'REACTION_ADD':
            await self.__wait_for_order_reaction_add(payload, order)

        if payload.event_type == 'REACTION_REMOVE':
            await self.__wait_for_order_reaction_remove(payload, order)
        
        if str(payload.emoji) == self.emoji_service_client.REACTION_ACCEPT and payload.channel_id != self.confirm_channel:
            user = await self.client.fetch_user(payload.user_id)
            order.preorder_embed.title = "Confirmed RaidPackage Order"
            order.preorder_embed.description = "Chosen Consumable Package:"
            order.preorder_embed.set_footer(text="")
            order_posting = await self.confirm_channel.send(embed=order.preorder_embed)
            await order_posting.add_reaction('✅')
            await order_posting.add_reaction('💵')
            await user.send(f"Your order is confirmed: {order_posting.jump_url}")
            await order.message.delete()
            await self.__gracefully_complete_order(order)
            return

        if str(payload.emoji) == self.emoji_service_client.REACTION_CANCEL:
            await self.__cancel_order(order)
            await self.__gracefully_complete_order(order)
            return

    async def __create_dm_preorder(self, usr, reaction_payload):
        # Create DMs 
        usr = await self.client.fetch_user(reaction_payload.user_id)
        preorder_embed = discord.Embed(title="Your RaidPackage Order", url='', color=0x109319, description='Choose your options by clicking the emojis below:')
        preorder_embed.set_author(name=usr)

        current_pos = 0
        for item in self.item_handler_client.items:
            if item.position_id == current_pos:
                preorder_embed.add_field(name=item.item_category, value='None', inline=False)
                current_pos += 1

        preorder_embed.set_footer(text=f'To confirm order click ✅\n To cancel order click ❌')

        sent_message = await usr.send(embed=preorder_embed)

        for item in self.item_handler_client.items:
            print(item.item_emoji)
            await sent_message.add_reaction(item.item_emoji)

        await sent_message.add_reaction(self.emoji_service_client.REACTION_ACCEPT)
        await sent_message.add_reaction(self.emoji_service_client.REACTION_CANCEL)
        return sent_message, preorder_embed

    async def __wait_for_order_reaction_add(self, payload, order: Order):  
        for item in self.item_handler_client.items:
            if payload.emoji == item.item_emoji:
                qtyReq = await self.__process_user_quantity_input(self.client, item, order)
                if qtyReq == None:
                    return
                else:
                    await order.message.edit(embed=order.preorder_embed.set_field_at(item.position_id, name=item.item_category, 
                                            value=item.item_name + f" x{qtyReq}", inline=False))
                    break

    async def __wait_for_order_reaction_remove(self, reaction_remove_payload, order: Order):
        for item in self.item_handler_client.items:
            if reaction_remove_payload.emoji.id == item.item_emoji.id:
                await order.message.edit(embed=order.preorder_embed.set_field_at(item.position_id, name=item.item_category, value='None', inline=False))
                break
        
    async def __cancel_order(self, order):
        await order.message.delete()
        cancelMsg = discord.Embed(title="Order Cancelled", url='', color=0x109319)
        usr = await self.client.fetch_user(order.author.id)
        await usr.send(embed=cancelMsg)

    async def __gracefully_complete_order(self, order: Order):
        del self.__responding_players[order.id]
        await self.error_handler_client.delete_usr_error_messages(order.author)
 
    async def __process_user_quantity_input(self, client, item, order: Order):
        msg = None
        qtyEmbed = discord.Embed(title=item.item_name, url='', color=0x109319, description=f"Enter quantity required, for example 20 (Max {item.item_max})")
        botMsg = await order.author.send(embed=qtyEmbed)

        def checkMsg(msg):
            if msg.content != "":
                qty = int(msg.content)
                return True
                        
        try:
            msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
        except asyncio.TimeoutError:
            await botMsg.delete()
            msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
            await self.__cancel_order(order)
        
        # non-numeric string
        except TypeError:
            await botMsg.delete()
            await self.error_handler_client.send_usr_error_message(order.author, "Error Message successful")
            
        except ValueError:
            await botMsg.delete()
            await self.error_handler_client.send_usr_error_message(order.author, f"You must enter a number - please unclick and reclick the {item.item_name} emoji")

        else:
            await botMsg.delete()
                    
        if msg is not None:
            if int(msg.content) > item.item_max:
                await self.error_handler_client.send_usr_error_message(order.author, f"You may only purchase a maximum of {item.item_max} {item.item_name} in a single order - please unclick and reclick the {item.item_name} emoji")
                
            else:
                await self.error_handler_client.delete_usr_error_messages(order.author)
                return int(msg.content)
