import os.path
from os import path
import discord


class Emoji_service():
    def __init__(self, guild):
        self.__existing_emoji_names = {} # contains a list of the slugs/names of all existing custom emojis in the server
        self.REACTION_ACCEPT='✅'
        self.REACTION_CANCEL='❌'
        self.REACTION_NEW_ORDER='📝'
        self.guild = guild
        self.__emoji_directory_path = "resources/custom_emojis/" # directory where image files of custom emojis are stored
        
        # Pre-populate dictionary of existing emojis on initialisation
        for emoji in self.guild.emojis: 
            self.__existing_emoji_names[emoji.name] = emoji

    # Takes a slug representing the expected name part of the required emoji
    # If already in the server, returns the emoji object, else creates the emoji if there is
    # an image file matching the slug and returns it
    async def handle_emoji_requirement(self, slug: str):
        if slug in self.__existing_emoji_names.keys():
            return self.__existing_emoji_names[slug]
        else:
            return await self.__create_new_emoji(slug)
  
    # Searches the path folder for image file matching the slug, then uses this to create
    # a custom emoji and return it. Private method to ensure bot always has to check if emoji exists
    # before creating a new emoji due to custom emoji limits on servers
    async def __create_new_emoji(self, slug: str):
        img = None
        if os.path.isfile(f"{self.__emoji_directory_path}{slug}.png"):
                with open(f"{self.__emoji_directory_path}{slug}.png", "rb") as image:
                    img = image.read()
        elif os.path.isfile(f"{self.__emoji_directory_path}{slug}.jpg"):
                with open(f"{self.__emoji_directory_path}{slug}.jpg", "rb") as image:
                    img = image.read()
        elif os.path.isfile(f"{self.__emoji_directory_path}{slug}.gif"):
                with open(f"{self.__emoji_directory_path}{slug}.gif", "rb") as image:
                    img = image.read()

        else:
            raise Exception(f"No image file found for {slug} emoji. Please add a .png, .jpg or GIF file named {slug} to resources/custom_emojis folder")
        
        return await self.__create_emoji_from_file(img, slug)
        
    # Takes an image and slug and returns an emoji 
    async def __create_emoji_from_file(self, img, slug):
        b = []
        b = bytearray(img)
        new_emoji = await self.guild.create_custom_emoji(name=slug, image=b)
        self.__existing_emoji_names[new_emoji.name] = new_emoji
        return new_emoji  