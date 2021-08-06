import discord
from discord import user
from discord import embeds

client = discord.Client()
channel_id = 872909016806866964


storage = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!raidpackage'):
        preorder_embed = discord.Embed(title="Your RaidPackage Order", url='', color=0x109319, description='Choose your options by clicking the emjois below:')
        preorder_embed.set_author(name=message.author)
        preorder_embed.add_field(name="Weapon Enhancement", value='None', inline=False)
        preorder_embed.add_field(name="Potion", value='None', inline=False)
        preorder_embed.set_footer(text=f'To confirm order click ✅')
        sent_message = await message.author.send(embed=preorder_embed)
        storage[message.author.id] = sent_message
        await sent_message.add_reaction('<:greaterweights:873125531007205397>')
        await sent_message.add_reaction('<:greatersharpen:873125466041643038>')
        await sent_message.add_reaction('<:inv_alchemy_purple:873124799914860564>')
        await sent_message.add_reaction('<:inv_alchemy_str:873124695417974814>')
        await sent_message.add_reaction('✅')
        await message.delete()


@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id:
        return

    if payload.event_type == 'REACTION_REMOVE':
        return

    if str(payload.emoji) == '<:inv_alchemy_str:873124695417974814>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(1, name="Potion", value="Potion of Greater Strength", inline=False))

    if str(payload.emoji) == '<:inv_alchemy_purple:873124799914860564>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(1, name="Potion", value="Potion of Greater Intellect", inline=False))

    if str(payload.emoji) == '<:greatersharpen:873125466041643038>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value="Greater Sharpening Stone", inline=False))

    if str(payload.emoji) == '<:greaterweights:873125531007205397>':
        msg = storage[payload.user_id]
        order = msg.embeds[0]
        await msg.edit(embed=order.set_field_at(0, name="Weapon Enhancement", value="Greater Weight Stone", inline=False))

    if str(payload.emoji) == '✅' and payload.channel_id != channel_id:
        channel = client.get_channel(channel_id)
        user = await client.fetch_user(payload.user_id)
        preorder_embed = storage[payload.user_id].embeds[0]
        preorder_embed.title = "Confirmed RaidPackage Order"
        preorder_embed.description = "Chosen Consumable Package:"
        order_posting = await channel.send(embed=preorder_embed)
        await order_posting.add_reaction('✅')
        await order_posting.add_reaction('💵')
        await user.send(f"Your order is confirmed: {order_posting.jump_url}")
        del storage[payload.user_id]

client.run('ODcyNTk5MzcwNzkxNTE4MjM4.YQsNfg.mkxeHsgWyS3ve5KcgixxRwxbos0')