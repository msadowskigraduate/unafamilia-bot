import json
from discord import message

items = []

REACTION_ACCEPT='✅'
REACTION_CANCEL='❌'
REACTION_NEW_ORDER='📝'

class Item(object):
    def __init__(self, position_id, item_name, item_category, item_max, item_emoji):
        self.position_id = position_id
        self.item_name = item_name
        self.item_category = item_category
        self.item_max = item_max
        self.item_emoji = item_emoji


def populate_items():
    with open('resources/items.json') as f:
        json_item_data = json.load(f)

    i = 0
    for json_object in json_item_data:
        item = Item(**json_object)
        items.append(item)
        i += 1

    for item in items:
        print(item.item_name)

