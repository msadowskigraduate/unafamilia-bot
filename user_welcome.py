import discord
from datetime import datetime

async def welcome_member_to_the_guild(member, client):
    welcome_embed = discord.Embed(title="Welcome to Una Familia!", url='', color=0x109319, description='I am EggBot and I will be your guide!')
