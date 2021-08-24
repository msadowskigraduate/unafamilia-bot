import discord
import asyncio

class Error_handler():
    def __init__(self):
        self.__error_messages = {}

    async def send_usr_error_message(self, user: int, message: str):
        error_msg = await user.send(message)
        if user.id in self.__error_messages:
            self.__error_messages[user.id].append(error_msg)
        else:
            self.__error_messages[user.id] = [error_msg]
        
        print(self.__error_messages)

    async def delete_usr_error_messages(self, user:int):
        if user.id in self.__error_messages:
            for message in self.__error_messages[user.id]:
                await message.delete()
                del self.__error_messages[user.id]

            


