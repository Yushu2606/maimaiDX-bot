import botpy
from botpy import logging
from botpy.message import GroupMessage

from .Commands import bind, binddf, bindlx, pull, mai


class Client(botpy.Client):
    async def on_ready(self):
        _log = logging.get_logger()
        _log.info("初始化完毕")

    async def on_group_at_message_create(self, message: GroupMessage):
        handlers = [
            bind,
            binddf,
            bindlx,
            pull,
            mai
        ]
        for handler in handlers:
            try:
                if await handler(api=self.api, message=message):
                    break
            except:
                await message.reply(content="失败！")
                raise
