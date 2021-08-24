import json
from discord import message
#import discord
import os.path
from os import path
import asyncio

items = []

REACTION_ACCEPT='✅'
REACTION_CANCEL='❌'
REACTION_NEW_ORDER='📝'

class Item(object):
    def __init__(self, position_id, item_name, item_category, item_max, slug):
        self.position_id = position_id
        self.item_name = item_name
        self.item_category = item_category
        self.item_max = item_max
        self.item_emoji = None
        self.slug = slug

async def populate_items(guild):
    __existing_emoji_names = []
    b = None

    with open('resources/items.json') as f:
        json_item_data = json.load(f)

    for json_object in json_item_data:
        item = Item(**json_object)
        for emoji in guild.emojis:
            __existing_emoji_names.append(emoji.name)
            if str(emoji.name) == item.slug:
                item.item_emoji = f'<:{str(emoji.name)}:{str(emoji.id)}>'
                break
            
        if item.slug not in __existing_emoji_names:
            if os.path.isfile(f"resources/custom_emojis/{item.slug}.png"):
                with open(f"resources/custom_emojis/{item.slug}.png", "rb") as image:
                    img = image.read()
                    b = bytearray(img)
                    new_emoji = await guild.create_custom_emoji(name=item.slug, image=b)
                    item.item_emoji = f'<:{str(new_emoji.name)}:{str(new_emoji.id)}>'
            else:
                raise Exception(f"No image file found for {item.item_name} emoji. Please add a .png, .jpg or GIF file named {item.slug} to resources/custom_emojis folder")

        items.append(item)