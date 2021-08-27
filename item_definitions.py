import json
from discord import message
import os.path
from os import path
import asyncio

items = []
__emoji_directory_path = "resources/custom_emojis/"

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
    __existing_emoji_names = {}

    for emoji in guild.emojis:
        __existing_emoji_names[emoji.name] = emoji

    b = None

    with open('resources/items.json') as f:
        json_item_data = json.load(f)

    for json_object in json_item_data:
        item = Item(**json_object)
        items.append(item)

    for item in items:
        print(f"Checking {item.item_name}")
        if item.slug in __existing_emoji_names.keys():
            print(f"{item.slug} found, assigning")
            item.item_emoji = __existing_emoji_names[item.slug]
            print(f"{item.item_name} assigned {__existing_emoji_names[item.slug]}")
            
        if item.slug not in __existing_emoji_names:
            if os.path.isfile(f"{__emoji_directory_path}{item.slug}.png"):
                with open(f"{__emoji_directory_path}{item.slug}.png", "rb") as image:
                    img = image.read()
                    b = bytearray(img)
                    new_emoji = await guild.create_custom_emoji(name=item.slug, image=b)
                    __existing_emoji_names[new_emoji.name] = new_emoji
                    item.item_emoji = new_emoji
            else:
                raise Exception(f"No image file found for {item.item_name} emoji. Please add a .png, .jpg or GIF file named {item.slug} to resources/custom_emojis folder")

        