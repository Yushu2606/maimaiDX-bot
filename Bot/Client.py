import botpy
from botpy.message import GroupMessage
from botpy import logging
from .Command import bind, binddf, bindlx, pull


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
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                break
