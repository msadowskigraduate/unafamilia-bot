import discord

async def intialize_order_channels(guild, client, confirmed_channel_name, order_channel_name): 
    confirmed_order_channel = None
    order_channel = None
    for chnl in client.get_all_channels():
        if chnl.name == confirmed_channel_name:
            confirmed_order_channel = chnl
            continue

        if chnl.name == order_channel_name:
            order_channel = chnl
            order_channel.purge(check=lambda m: m.author == client.user)
            continue

    if confirmed_order_channel == None:
        permissions = {
             guild.default_role: discord.PermissionOverwrite(send_messages=False)
        }
        confirmed_order_channel = await guild.create_text_channel(confirmed_channel_name, overwrites=permissions)

    if order_channel == None:
        order_channel = await guild.create_text_channel(order_channel_name)

    return confirmed_order_channel, order_channel 