import asyncio
import botpy
from botpy import logging
from botpy.message import GroupMessage

import maimai.Api
from .Commands import bind, binddf, bindlx, pull, mai, query


class Client(botpy.Client):
    async def on_ready(self):
        asyncio.create_task(maimai.Api.D())

        _log = logging.get_logger()
        _log.info("初始化完毕")

    async def on_group_at_message_create(self, message: GroupMessage):
        handlers = [bind, binddf, bindlx, pull, mai, query]
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
