import discord
import asyncio

class Error_handler():
    def __init__(self):
        self.error_messages = {}

    async def send_usr_error_message(self, user: int, message: str):
        error_msg = await user.send(message)
        if user.id in self.error_messages:
            self.error_messages[user.id].append(error_msg)
        else:
            self.error_messages[user.id] = [error_msg]

    async def delete_usr_error_messages(self, user:int):
        if user.id in self.error_messages:
            del self.error_messages[user.id]


