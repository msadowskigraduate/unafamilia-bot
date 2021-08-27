from emoji_service import Emoji_service
import json
from discord import message
import os.path
from os import path
import asyncio

# Class to deal with storage and requests for data relating to items offered as part of raid package
class Item_handler():
    def __init__(self, emoji_service_client: Emoji_service):
        self.emoji_service_client = emoji_service_client
        self.items = [] # array stores all item objects

    # Item class contains details of each item. 
    class Item(object):
        def __init__(self, position_id, item_name, item_category, item_max, slug):
            self.position_id = position_id # refers to the position of the embed field in the order embed
            self.item_name = item_name
            self.item_category = item_category
            self.item_max = item_max # maximum number of an item purchasable in a single transaction
            self.item_emoji = None # stores an emoji object
            self.slug = slug # the expected name of the custom emoji relating to the item
        
    async def populate_items(self):
        with open('resources/items.json') as f:
            json_item_data = json.load(f)

        for json_object in json_item_data:
            item = self.Item(**json_object)
            item.item_emoji = await self.emoji_service_client.handle_emoji_requirement(item.slug) #returns an emoji object - creates an emoji if none exists and returns this
            self.items.append(item)
       
            