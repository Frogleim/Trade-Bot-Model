import logging
import os
import random
import time
from pyrogram import Client, filters, types
from core import config

TOKEN = os.getenv('TOKEN')
print(TOKEN)


def get_csv_file_dir():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    csv_file_dir = os.path.join(parent_dir, "core\\files")
    return csv_file_dir


class BotClient:
    def __init__(self):
        self.token = config.TOKEN
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    def create_app(self):
        with Client(f'trade_bots', self.api_id, self.api_hash, self.token) as client:
            return client


bot_app = BotClient()
app = bot_app.create_app()


@app.on_message(filters.command(["start"]))
async def start_handler(client: "Client", message: "types.Message"):
    chat_id = 6865487233
    await client.send_message(chat_id, 'Oracle Starting!')


if __name__ == '__main__':
    app.run()
