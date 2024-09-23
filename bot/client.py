import asyncio

import botpy
from botpy import logging
from botpy.message import GroupMessage

import maimai.api
from bot.commands import bind, binddf, bindlx, pull, mai, query, brea, sche


class Client(botpy.Client):
    async def on_ready(self):
        asyncio.create_task(maimai.api.D())

        _log = logging.get_logger()
        _log.info("初始化完毕")

    async def on_group_at_message_create(self, message: GroupMessage):
        handlers = [bind, binddf, bindlx, pull, mai, query, brea, sche]
        for handler in handlers:
            try:
                if await handler(api=self.api, message=message):
                    break
            except:
                try:
                    await message.reply(content="失败！")
                except:
                    pass
                raise
