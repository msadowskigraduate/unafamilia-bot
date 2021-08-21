import asyncio
import discord
import item_definitions

class RaidPackageClient():

    class Order:
        def __init__(self, id:str, message: discord.Message, author: discord.Member, preorder_embed: discord.Embed):
            self.id = id
            self.message = message
            self.author = author
            self.preorder_embed = preorder_embed
            self.__error_messages = []


        async def delete_order_error_messages(self):
            if len(self.__error_messages) > 0:
                for msg in self.__error_messages:
                    await msg.delete()
                    self.__error_messages.remove(msg)
            
        async def send_error_message(self, msg: str):
            error_msg = await self.author.send(msg)
            self.__error_messages.append(error_msg)
            
    __init_message :discord.Message = None

    #Correlation between message and Order
    __responding_players = {}

    def __init__(self, client: discord.Client, order_channel: discord.TextChannel, confirm_channel: discord.TextChannel):
        self.client = client
        self.order_channel = order_channel
        self.confirm_channel = confirm_channel

    async def initialize_client(self):
        initPost = discord.Embed(title="Una Familia Raid Consumables Ordering Service", url='', color=0x109319, description='Click the 📝 reaction below to begin your order')
        initPost.add_field(name="Intro", value="Welcome to the raid consumable ordering service. You can use this service to order consumables before a raid night at a cheaper price than the auction house.", inline=False)
        initPost.add_field(name="Starting a new order", value="To begin, click the 📝 emoji below, and the bot will send you a DM. Simply click the items you want and type the quantities. Click the green tick to confirm your order.", inline=False)
        initPost.add_field(name="Delivery and payment", value="An officer will mail you the items, and message you the price to deposit into the guild bank before the raid begins.", inline=False)
        self.__init_message = await self.order_channel.send(embed=initPost)
        await self.__init_message.add_reaction(item_definitions.REACTION_NEW_ORDER)

    async def handle_reaction(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.client.user.id:
            return

        if str(payload.emoji) == item_definitions.REACTION_NEW_ORDER and payload.event_type == 'REACTION_ADD' and payload.channel_id == self.order_channel.id:
            await self.__listen_for_player_reaction(payload)

        order: self.Order = self.__responding_players.get(payload.message_id)
        if order is not None:
            await self.__listen_for_order_specification(payload, order)

    async def __listen_for_player_reaction(self, payload: discord.RawReactionActionEvent):
        usr = await self.client.fetch_user(payload.user_id)
        sent_message, preorder_embed = await self.__create_dm_preorder(usr, payload)
        await self.__init_message.remove_reaction(item_definitions.REACTION_NEW_ORDER, usr)
        self.__responding_players[sent_message.id] = self.Order(sent_message.id, sent_message, usr, preorder_embed)

    async def __listen_for_order_specification(self, payload: discord.RawReactionActionEvent, order: Order):
        #Process Order Reactions
        if payload.event_type == 'REACTION_ADD':
            await self.__wait_for_order_reaction_add(payload, order)

        if payload.event_type == 'REACTION_REMOVE':
            await self.__wait_for_order_reaction_remove(payload, order)
        
        if str(payload.emoji) == item_definitions.REACTION_ACCEPT and payload.channel_id != self.confirm_channel:
            user = await self.client.fetch_user(payload.user_id)
            order.preorder_embed.title = "Confirmed RaidPackage Order"
            order.preorder_embed.description = "Chosen Consumable Package:"
            order.preorder_embed.set_footer(text="")
            order_posting = await self.confirm_channel.send(embed=order.preorder_embed)
            await order_posting.add_reaction('✅')
            await order_posting.add_reaction('💵')
            await user.send(f"Your order is confirmed: {order_posting.jump_url}")
            await order.message.delete()
            self.__gracefully_complete_order(order)
            return

        if str(payload.emoji) == item_definitions.REACTION_CANCEL:
            await self.__cancel_order(order.message, payload.user_id)
            self.__gracefully_complete_order(order)
            return

    async def __create_dm_preorder(self, usr, reaction_payload):
        # Create DMs 
        usr = await self.client.fetch_user(reaction_payload.user_id)
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

    async def __wait_for_order_reaction_add(self, payload, order: Order):  
        for item in item_definitions.items:
            if str(payload.emoji) == item.item_emoji:
                qtyReq = await self.__process_user_quantity_input(self.client, order.author, item.item_name, item.item_max, payload.user_id, order)
                if qtyReq == None:
                    return
                else:
                    await order.message.edit(embed=order.preorder_embed.set_field_at(item.position_id, name=item.item_category, 
                                            value=item.item_name + f" x{qtyReq}", inline=False))
                    break


    async def __wait_for_order_reaction_remove(self, reaction_remove_payload, order: Order):
        for item in item_definitions.items:
            if str(reaction_remove_payload.emoji) == item.item_emoji:
                await order.message.edit(embed=order.preorder_embed.set_field_at(item.position_id, name=item.item_category, value='None', inline=False))
                break
        

    async def __cancel_order(self, msg, usr_id):
        await msg.delete()
        cancelMsg = discord.Embed(title="Order Cancelled", url='', color=0x109319)
        usr = await self.client.fetch_user(usr_id)
        await usr.send(embed=cancelMsg)

    def __gracefully_complete_order(self, order: Order):
        del self.__responding_players[order.id]

    async def __process_user_quantity_input(self, client, usr, item, qtyMax, usr_id, order: Order):
        
        qtyEmbed = discord.Embed(title=item, url='', color=0x109319, description=f"Enter quantity required, for example 20 (Max {qtyMax})")
        botMsg = await usr.send(embed=qtyEmbed)

        def checkMsg(msg):
            if msg.content != "":
                qty = int(msg.content)
                return True
                        
        try:
            msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
        except asyncio.TimeoutError:
            await botMsg.delete()
            msg = await client.wait_for("message", timeout=20.0, check=checkMsg)
            await self.__cancel_order(msg, usr_id, client)
        
        # non-numeric string
        except TypeError:
            await botMsg.delete()
            await order.send_error_message(f"You must enter a number - please unclick and reclick the {item} emoji")
            
        except ValueError:
            await botMsg.delete()
            await order.send_error_message(f"You must enter a number - please unclick and reclick the {item} emoji")

        else:
            await botMsg.delete()
                    
        if int(msg.content) > qtyMax:
            await order.send_error_message(f"You may only purchase a maximum of {qtyMax} {item} in a single order - please unclick and reclick the {item} emoji")

        else:
            await order.delete_order_error_messages()
            return int(msg.content)
